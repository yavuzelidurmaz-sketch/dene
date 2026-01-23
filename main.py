import requests
import json
import timeimport requests
import json
import time

# --- TOKEN (MUTLAKA YENİSİNİ ALIP YAPIŞTIR - ESKİSİ BLOKE OLMUŞ OLABİLİR) ---
MANUAL_TOKEN = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJwcm9qZWN0SWQiOiIyZGE3a2Y4amYiLCJpZGVudGl0eSI6ImVuZHVzZXIiLCJhbm9ueW1vdXMiOmZhbHNlLCJ1c2VySWQiOiJlNGMzYWY2Yi05YWQyLTQ3NDYtYTVlNC0yNGQ1ODQyNjZmYzMiLCJjbGFpbXMiOnsiZW1haWwiOiJmYXRtYW51cnJrcmttenoxODZAZ21haWwuY29tIiwiZnVsbE5hbWUiOiJwaXJ0aXN0YW4iLCJwcm9maWxlSWQiOiJVUkNNUURMRExYSkxITFBGQkFOMFpJOVYiLCJwcm9maWxlQXZhdGFyIjoiUCIsImlzS2lkUHJvZmlsZSI6ZmFsc2V9LCJzZXNzaW9uSWQiOiIyOTVhNWM4N2RlYTk0Y2FhOTcyOTZlYzY2OWNiYjBmZCIsImlhdCI6MTc2OTE5NjA1MywiZXhwIjoxNzcxNzg4MDUzfQ.yKLLAEotOL9BWz3oFDsVyos7zcfMxnPFgRJpmsn50B6IbBe3SMgeZo02X0ghZdz93xB5kUETdBlDRmt1QHzAJ_7z_4qOLukh-z2pnPeaImVT-fRZGjK4Ez--GjRS_sOdnXgNVIdzYkiEsqyVabi8wL46K0C-1oo5B9bJ7sjAxaadAAs4rFKQ-bKx-c1rKgOso31XArEn3zIo0bhjhuvuOECNwvVbDu5Dg2LcgqkbDRA8LQ37iDudkaAwF9jVnxTNHLzmrxMf6KwftzgdmkIoizrsThFw1vVJWXTdaXNXlS5ZbOvC-iQ3UH3gAk2Yjv6gDxk0YgvRRYsDE3vwNKrbeQ"

# --- AYARLAR ---
PROJECT_ID = "2da7kf8jf"
ADULT_PROFILE_ID = "URCMQDLDLXJLHLPFBAN0ZI9V"
KIDS_PROFILE_ID = "KIBPFC0Q9Z08Q1UMMJTO61NI"

# Videodaki gibi Kategoriler (Slug'lar doğru olmalı)
TARGETS = [
    {"name": "Dizi", "profile_id": ADULT_PROFILE_ID, "param": "slug=%2Fdizi"},
    {"name": "Film", "profile_id": ADULT_PROFILE_ID, "param": "slug=%2Ffilm"},
    {"name": "Program", "profile_id": ADULT_PROFILE_ID, "param": "slug=%2Fprogram"},
    {"name": "Belgesel", "profile_id": ADULT_PROFILE_ID, "param": "slug=%2Fbelgesel"},
    {"name": "Kids", "profile_id": KIDS_PROFILE_ID, "param": "categoryName=MAIN-PAGE"}
]

BASE_API = f"https://api.gain.tv/{PROJECT_ID}/CALL/ProfileTitle"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Content-Type": "application/json",
    "Authorization": f"Bearer {MANUAL_TOKEN}",
    "x-gain-platform": "web"
}

def get_episodes(title_id, season_id, profile_id):
    """Bir sezonun içindeki tüm bölümleri çeker"""
    # Videodaki gibi, bir diziye girince bölümler listelenir.
    url = f"{BASE_API}/getProfileSeason/{profile_id}?seasonId={season_id}&titleId={title_id}&__culture=tr-tr&pageSize=200"
    try:
        res = requests.get(url, headers=HEADERS)
        if res.status_code == 200:
            return res.json().get("episodes", [])
    except:
        pass
    return []

def get_show_details(title_id, profile_id):
    """Bir içeriğin detayına girer (Sezon var mı bakar)"""
    # Videoda tıkladığında açılan detay sayfası burasıdır.
    url = f"{BASE_API}/getProfileTitle/{profile_id}?titleId={title_id}&__culture=tr-tr"
    try:
        res = requests.get(url, headers=HEADERS)
        if res.status_code == 200:
            return res.json()
    except:
        pass
    return {}

def get_contents_from_shelves(target):
    """Videodaki kaydırmalı rafları (Playlist) tarar"""
    # Sayfalama parametresi (pageIndex) YOK. Sadece kategoriyi istiyoruz.
    url = f"{BASE_API}/getPlaylistsByCategory/{target['profile_id']}?{target['param']}&__culture=tr-tr"
    print(f"\n🌍 '{target['name']}' kategorisindeki raflar çekiliyor...")

    contents = []
    processed_ids = set() # Aynı içerik farklı raflarda olabilir, tekrarı önle.

    try:
        res = requests.get(url, headers=HEADERS)
        if res.status_code != 200:
            print(f"   ❌ Erişim Hatası: {res.status_code} (Token bitmiş olabilir)")
            return []

        data = res.json()
        playlists = data.get("playlists", []) # Bunlar videodaki "Komedi", "Aksiyon" vb. başlıklar
        print(f"   📦 Toplam {len(playlists)} raf (başlık) bulundu. İçerikleri taranıyor...")

        for playlist in playlists:
            playlist_name = playlist.get("name", "Genel")
            items = playlist.get("items", [])
            
            # print(f"      👉 Raf: {playlist_name} ({len(items)} içerik)")

            for item in items:
                title_id = item.get("titleId")
                video_id = item.get("videoContentId")
                name = item.get("name") or item.get("title")
                poster = item.get("logoImageUrl") or item.get("posterImageUrl")

                # Benzersizlik kontrolü
                unique_key = title_id if title_id else video_id
                if not unique_key or unique_key in processed_ids:
                    continue
                processed_ids.add(unique_key)

                # --- TÜR BELİRLEME (Videodaki mantık) ---
                # Detaya girip bakmamız lazım, çünkü dışarıdan sadece resim görünüyor.
                
                is_series = False
                seasons = []

                # Eğer titleId varsa bu bir "Başlık"tır (Dizi veya Film Grubu olabilir)
                if title_id:
                    details = get_show_details(title_id, target['profile_id'])
                    seasons = details.get("seasons", [])
                    if seasons:
                        is_series = True
                    # Bazen filmdir ama titleId ile gelir, seasons boştur.

                # --- LİSTEYE EKLEME ---

                if is_series:
                    # DİZİ / PROGRAM İSE (Sezonları ve Bölümleri var)
                    for season in seasons:
                        # Sezon içindeki bölümleri çek
                        episodes = get_episodes(title_id, season.get("id"), target['profile_id'])
                        for ep in episodes:
                            ep_num = ep.get('episode', 0)
                            ep_name = ep.get('name', '')
                            full_title = f"{name} - S{season.get('seasonNum', 1)}B{ep_num} - {ep_name}"
                            
                            contents.append({
                                "id": ep.get("videoContentId"),
                                "title": full_title,
                                "group": f"Gain - {name}", # Dizi ismiyle klasör
                                "poster": poster,
                                "profile_id": target['profile_id']
                            })
                else:
                    # FİLM / TEKİL VİDEO İSE
                    # Eğer videoId'si varsa bu oynatılabilir bir şeydir.
                    vid_id_to_use = video_id
                    
                    # Bazen detaydan videoId almak gerekir
                    if not vid_id_to_use and title_id:
                        # Detayları zaten çekmiştik
                        vid_id_to_use = details.get("videoContentId")

                    if vid_id_to_use:
                        contents.append({
                            "id": vid_id_to_use,
                            "title": name,
                            "group": f"Gain - {target['name']}",
                            "poster": poster,
                            "profile_id": target['profile_id']
                        })

        print(f"   ✅ '{target['name']}' kategorisinden {len(contents)} video eklendi.")
        return contents

    except Exception as e:
        print(f"🔥 Hata oluştu: {e}")
        return []

def get_stream_url(content):
    """Video ID'den oynatma linkini (MPD/HLS) alır"""
    url = f"{BASE_API}/getPlaybackInfo/{content['profile_id']}/"
    params = {"videoContentId": content["id"], "packageType": "Dash", "__culture": "tr-tr"}
    try:
        res = requests.get(url, headers=HEADERS, params=params)
        if res.status_code == 200:
            pb_url = res.json().get("currentVideoContent", {}).get("playbackUrl")
            if pb_url:
                content["stream_url"] = pb_url
                return content
            else:
                # Bazen hata döner, DRM vs.
                # print(f"Link yok: {res.text}")
                pass
    except:
        pass
    return None

def save_m3u(data, filename="gain_archive.m3u"):
    print(f"\n📺 Dosyalar kaydediliyor: {filename}...")
    try:
        # JSON YEDEK
        with open("gain_full.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

        # M3U
        with open(filename, "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")
            for item in data:
                if "stream_url" in item:
                    f.write(f'#EXTINF:-1 group-title="{item["group"]}" tvg-logo="{item["poster"]}", {item["title"]}\n')
                    f.write('#EXTVLCOPT:http-user-agent=Mozilla/5.0\n')
                    f.write(f"{item['stream_url']}\n")
        print("✅ İŞLEM BAŞARIYLA TAMAMLANDI!")
    except Exception as e:
        print(f"Dosya yazma hatası: {e}")

def main():
    if "BURAYA" in MANUAL_TOKEN:
        print("⛔ Lütfen scriptin başındaki MANUAL_TOKEN kısmına yeni token yapıştırın!")
        return

    all_videos = []
    
    # 1. TÜM RAFLARI TARA
    for target in TARGETS:
        items = get_contents_from_shelves(target)
        all_videos.extend(items)
        time.sleep(1) # API'yi yormamak için bekleme

    total = len(all_videos)
    if total == 0:
        print("\n⛔ HİÇ İÇERİK BULUNAMADI.")
        print("Sebep 1: Token hatalı veya süresi dolmuş.")
        print("Sebep 2: Hesabın başka cihazda açık (Videodaki hata).")
        return

    print(f"\n🚀 TOPLAM {total} VİDEO İÇİN LİNKLER ALINIYOR...")
    print("   (Bu işlem biraz sürebilir, lütfen bekleyin...)")

    final_list = []
    # 2. LİNKLERİ AL
    for i, video in enumerate(all_videos):
        full_data = get_stream_url(video)
        if full_data:
            del full_data["profile_id"] # Dosyada yer kaplamasın
            final_list.append(full_data)
        
        # İlerleme durumu
        if (i+1) % 10 == 0: 
            print(f"   👍 {i+1}/{total} tamamlandı...")
        
        time.sleep(0.1) # Çok hızlı istek atıp 400 yememek için

    save_m3u(final_list)

if __name__ == "__main__":
    main()


# --- TOKEN (MUTLAKA GÜNCEL OLANI YAPIŞTIR) ---
MANUAL_TOKEN = ""

# --- AYARLAR ---
PROJECT_ID = "2da7kf8jf"
PROFILE_ID = "URCMQDLDLXJLHLPFBAN0ZI9V" # Yetişkin Profil

# Bu alfabe ile her harfi tek tek aratacağız
SEARCH_QUERY_LIST = list("abcdefghijklmnopqrstuvwxyz0123456789")

BASE_API = f"https://api.gain.tv/{PROJECT_ID}/CALL"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Content-Type": "application/json",
    "Authorization": f"Bearer {MANUAL_TOKEN}",
    "x-gain-platform": "web"
}

def get_episodes(title_id, season_id):
    """Sezon içindeki bölümleri çeker"""
    url = f"{BASE_API}/ProfileTitle/getProfileSeason/{PROFILE_ID}?seasonId={season_id}&titleId={title_id}&__culture=tr-tr&pageSize=200"
    try:
        res = requests.get(url, headers=HEADERS)
        if res.status_code == 200:
            return res.json().get("episodes", [])
    except:
        pass
    return []

def get_show_details(title_id):
    """Dizi/Program detayına girip sezonları bulur"""
    url = f"{BASE_API}/ProfileTitle/getProfileTitle/{PROFILE_ID}?titleId={title_id}&__culture=tr-tr"
    try:
        res = requests.get(url, headers=HEADERS)
        if res.status_code == 200:
            return res.json().get("seasons", [])
    except:
        pass
    return []

def search_and_collect():
    """A'dan Z'ye arama yaparak tüm kütüphaneyi toplar"""
    print(f"\n🚀 DERİN TARAMA BAŞLIYOR (A-Z)...")
    
    unique_contents = {} # ID tekrarlarını önlemek için sözlük
    
    for query in SEARCH_QUERY_LIST:
        print(f"   🔎 Harf taranıyor: '{query.upper()}' ...")
        
        # Arama Endpointi
        url = f"{BASE_API}/Search/getSearchResults/{PROFILE_ID}?query={query}&__culture=tr-tr"
        
        try:
            res = requests.get(url, headers=HEADERS)
            if res.status_code != 200:
                print(f"      ❌ Hata: {res.status_code}")
                continue

            # Arama sonuçları genellikle 'results' veya 'items' içinde gelir
            data = res.json()
            items = data.get("results", []) or data.get("items", [])

            for item in items:
                title_id = item.get("titleId")
                video_id = item.get("videoContentId")
                name = item.get("name") or item.get("title")
                poster = item.get("logoImageUrl") or item.get("posterImageUrl")
                content_type = item.get("type") # Series, Movie, Video vb.
                
                # Benzersiz ID oluştur (Tekrarları önle)
                unique_key = title_id if title_id else video_id
                if not unique_key or unique_key in unique_contents:
                    continue

                # İçeriği ham haliyle kaydet, aşağıda işleyeceğiz
                unique_contents[unique_key] = {
                    "title_id": title_id,
                    "video_id": video_id,
                    "name": name,
                    "poster": poster,
                    "type": content_type
                }
                
        except Exception as e:
            print(f"      🔥 Hata: {e}")
        
        time.sleep(0.5) # API'yi boğmamak için bekleme

    print(f"\n✅ Tarama Bitti! Toplam {len(unique_contents)} benzersiz içerik bulundu.")
    return list(unique_contents.values())

def process_contents(raw_items):
    """Bulunan içerikleri Dizi/Film olarak ayırır ve linkleri hazırlar"""
    final_list = []
    print("\n📦 İçerikler işleniyor (Diziler bölümlere ayrılıyor)...")
    
    total = len(raw_items)
    for i, item in enumerate(raw_items):
        title_id = item["title_id"]
        video_id = item["video_id"]
        name = item["name"]
        
        # Log (Her 20 içerikte bir yaz)
        if (i+1) % 20 == 0:
            print(f"   ⚙️ {i+1}/{total} işlendi...")

        # --- SENARYO 1: DİZİ / PROGRAM ---
        # Eğer title_id var ve video_id yoksa veya tipi Series ise
        if title_id and (not video_id or item.get("type") == "Series"):
            seasons = get_show_details(title_id)
            if seasons:
                for season in seasons:
                    episodes = get_episodes(title_id, season.get("id"))
                    for ep in episodes:
                        ep_num = ep.get('episode', 0)
                        ep_name = ep.get('name', '')
                        full_title = f"{name} - S{season.get('seasonNum', 1)}B{ep_num} - {ep_name}"
                        
                        final_list.append({
                            "id": ep.get("videoContentId"),
                            "title": full_title,
                            "group": f"Gain - Dizi & Program",
                            "poster": item["poster"],
                            "profile_id": PROFILE_ID
                        })
                continue # Diziyi hallettik, döngüye devam

        # --- SENARYO 2: FİLM / TEK VİDEO ---
        if video_id:
            final_list.append({
                "id": video_id,
                "title": name,
                "group": "Gain - Filmler",
                "poster": item["poster"],
                "profile_id": PROFILE_ID
            })

    return final_list

def get_stream_url(content):
    url = f"{BASE_API}/ProfileTitle/getPlaybackInfo/{content['profile_id']}/"
    params = {"videoContentId": content["id"], "packageType": "Dash", "__culture": "tr-tr"}
    try:
        res = requests.get(url, headers=HEADERS, params=params)
        if res.status_code == 200:
            pb_url = res.json().get("currentVideoContent", {}).get("playbackUrl")
            if pb_url:
                content["stream_url"] = pb_url
                return content
    except:
        pass
    return None

def save_m3u(data, filename="gain_archive.m3u"):
    print(f"\n📺 M3U ve JSON oluşturuluyor...")
    
    # JSON Kayıt
    with open("gain_full.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
        
    # M3U Kayıt
    with open(filename, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for item in data:
            if "stream_url" in item:
                f.write(f'#EXTINF:-1 group-title="{item["group"]}" tvg-logo="{item["poster"]}", {item["title"]}\n')
                f.write('#EXTVLCOPT:http-user-agent=Mozilla/5.0\n')
                f.write(f"{item['stream_url']}\n")
    print("✅ Dosyalar Hazır!")

def main():
    if "BURAYA" in MANUAL_TOKEN:
        print("⛔ Token girmeyi unutma!")
        return

    # 1. Aşama: A-Z Tarama
    raw_items = search_and_collect()
    
    if not raw_items:
        print("⛔ Hiç içerik bulunamadı. Token veya IP kontrolü yapın.")
        return

    # 2. Aşama: Detaylandırma (Sezon/Bölüm bulma)
    processed_items = process_contents(raw_items)
    
    print(f"\n🚀 TOPLAM {len(processed_items)} OYNATILABİLİR VİDEO İÇİN LİNKLER ÇEKİLİYOR...")

    # 3. Aşama: Linkleri Çekme
    final_list = []
    for i, video in enumerate(processed_items):
        full_data = get_stream_url(video)
        if full_data:
            del full_data["profile_id"]
            final_list.append(full_data)
        
        if (i+1) % 50 == 0: 
            print(f"   👍 {i+1}/{len(processed_items)} link alındı...")
        time.sleep(0.01)

    save_m3u(final_list)
    print("\n🏁 MUTLU SON! Tüm arşiv indi.")

if __name__ == "__main__":
    main()
