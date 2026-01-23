import requests
import json
import time

# --- TOKEN (MUTLAKA YENİSİNİ ALIP YAPIŞTIR) ---
MANUAL_TOKEN = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJwcm9qZWN0SWQiOiIyZGE3a2Y4amYiLCJpZGVudGl0eSI6ImVuZHVzZXIiLCJhbm9ueW1vdXMiOmZhbHNlLCJ1c2VySWQiOiJlNGMzYWY2Yi05YWQyLTQ3NDYtYTVlNC0yNGQ1ODQyNjZmYzMiLCJjbGFpbXMiOnsiZW1haWwiOiJmYXRtYW51cnJrcmttenoxODZAZ21haWwuY29tIiwiZnVsbE5hbWUiOiJwaXJ0aXN0YW4iLCJwcm9maWxlSWQiOiJVUkNNUURMRExYSkxITFBGQkFOMFpJOVYiLCJwcm9maWxlQXZhdGFyIjoiUCIsImlzS2lkUHJvZmlsZSI6ZmFsc2V9LCJzZXNzaW9uSWQiOiIyOTVhNWM4N2RlYTk0Y2FhOTcyOTZlYzY2OWNiYjBmZCIsImlhdCI6MTc2OTE5NjA1MywiZXhwIjoxNzcxNzg4MDUzfQ.yKLLAEotOL9BWz3oFDsVyos7zcfMxnPFgRJpmsn50B6IbBe3SMgeZo02X0ghZdz93xB5kUETdBlDRmt1QHzAJ_7z_4qOLukh-z2pnPeaImVT-fRZGjK4Ez--GjRS_sOdnXgNVIdzYkiEsqyVabi8wL46K0C-1oo5B9bJ7sjAxaadAAs4rFKQ-bKx-c1rKgOso31XArEn3zIo0bhjhuvuOECNwvVbDu5Dg2LcgqkbDRA8LQ37iDudkaAwF9jVnxTNHLzmrxMf6KwftzgdmkIoizrsThFw1vVJWXTdaXNXlS5ZbOvC-iQ3UH3gAk2Yjv6gDxk0YgvRRYsDE3vwNKrbeQ"

# --- AYARLAR ---
PROJECT_ID = "2da7kf8jf"
ADULT_PROFILE_ID = "URCMQDLDLXJLHLPFBAN0ZI9V"
KIDS_PROFILE_ID = "KIBPFC0Q9Z08Q1UMMJTO61NI"

# Taranacak Kategoriler
TARGETS = [
    {"name": "Dizi", "profile_id": ADULT_PROFILE_ID, "param": "slug=%2Fdizi", "type": "SERIES"},
    {"name": "Program", "profile_id": ADULT_PROFILE_ID, "param": "slug=%2Fprogram", "type": "SERIES"}, # Programları da dizi mantığıyla tarayacağız
    {"name": "Film", "profile_id": ADULT_PROFILE_ID, "param": "slug=%2Ffilm", "type": "MOVIE"},
    {"name": "Belgesel", "profile_id": ADULT_PROFILE_ID, "param": "slug=%2Fbelgesel", "type": "MOVIE"},
    {"name": "Kids", "profile_id": KIDS_PROFILE_ID, "param": "categoryName=MAIN-PAGE", "type": "MIXED"}
]

BASE_API = f"https://api.gain.tv/{PROJECT_ID}/CALL/ProfileTitle"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Content-Type": "application/json",
    "Authorization": f"Bearer {MANUAL_TOKEN}",
    "x-gain-platform": "web"
}

def get_episodes(title_id, season_id, profile_id):
    """Sezon içindeki bölümleri çeker"""
    # Bazen çok bölümlü işler (Talk showlar) tek sayfada gelmeyebilir, limit artırıldı.
    url = f"{BASE_API}/getProfileSeason/{profile_id}?seasonId={season_id}&titleId={title_id}&__culture=tr-tr&pageIndex=0&pageSize=200"
    try:
        res = requests.get(url, headers=HEADERS)
        if res.status_code == 200:
            return res.json().get("episodes", [])
    except:
        pass
    return []

def get_contents(target):
    """Kategoriyi sayfalar halinde tarar"""
    print(f"\n🌍 '{target['name']}' taranıyor...")
    
    contents = []
    processed_ids = set()
    page_index = 0
    empty_streak = 0 # Boş sayfa sayacı

    while True:
        # Sayfalama parametreleri eklendi: pageIndex ve pageSize
        url = f"{BASE_API}/getPlaylistsByCategory/{target['profile_id']}?{target['param']}&pageIndex={page_index}&pageSize=20&__culture=tr-tr"
        
        try:
            res = requests.get(url, headers=HEADERS)
            if res.status_code != 200:
                print(f"   ❌ Erişim Hatası (Page {page_index}): {res.status_code}")
                break

            data = res.json()
            playlists = data.get("playlists", [])
            
            # Eğer playlist boş geldiyse döngüyü kır (Son sayfa)
            if not playlists:
                # Bazen aralarda boşluk olabilir, hemen pes etme (Opsiyonel güvenlik)
                empty_streak += 1
                if empty_streak > 2:
                    print(f"   🏁 Tarama tamamlandı. (Toplam {page_index} sayfa tarandı)")
                    break
                page_index += 1
                continue
            
            empty_streak = 0 # Playlist bulunduysa sayacı sıfırla
            print(f"   📖 Sayfa {page_index+1} işleniyor... ({len(playlists)} raf)")

            for playlist in playlists:
                items = playlist.get("items", [])
                
                # Bazen "İzlemeye Devam Et" gibi listeler gelir, bunları atlayabiliriz veya alabiliriz.
                # Şimdilik hepsini alıyoruz.

                for item in items:
                    title_id = item.get("titleId")
                    video_id = item.get("videoContentId")
                    name = item.get("name") or item.get("title")
                    poster = item.get("logoImageUrl") or item.get("posterImageUrl")
                    
                    # API'den gelen seasons verisi
                    seasons = item.get("seasons", [])
                    
                    # ÖNEMLİ: Eğer içerik "Dizi" veya "Program" kategorisindeyse ve 'seasons' boş geldiyse bile
                    # bu bir "Film" olmayabilir. Bu yüzden 'titleId' varsa onu dizi gibi işlemeye zorlayabiliriz.
                    # Ancak Gain'de bazen tek bölümlük programlar da var.
                    
                    # İşlenmiş içerikleri atla
                    unique_key = title_id if title_id else video_id
                    if unique_key in processed_ids: continue
                    processed_ids.add(unique_key)

                    # --- MANTIK: Dizi/Program mı Film mi? ---

                    is_series_logic = False
                    
                    # 1. Eğer 'seasons' doluysa kesin dizidir.
                    if seasons:
                        is_series_logic = True
                    
                    # 2. Eğer 'seasons' boş ama kategori DİZİ/PROGRAM ise ve elimizde bir titleId varsa
                    # (Bazen API ana listede sezonları vermez, ama aslında vardır)
                    elif target['type'] == "SERIES" and title_id and not video_id:
                         # Burada detay sorgusu yapılabilir ama çok yavaşlatır. 
                         # Genelde titleId varsa ve videoId yoksa bu bir "Show"dur.
                         is_series_logic = True

                    if is_series_logic and seasons:
                        # Sezonları olan Dizi/Program
                        print(f"      running -> Dizi/Prog: {name}")
                        for season in seasons:
                            episodes = get_episodes(title_id, season.get("id"), target['profile_id'])
                            for ep in episodes:
                                ep_num = ep.get('episode', 0)
                                ep_name = ep.get('name', '')
                                full_title = f"{name} - S{season.get('seasonNum',1)}B{ep_num} - {ep_name}"
                                
                                contents.append({
                                    "id": ep.get("videoContentId"),
                                    "title": full_title,
                                    "group": f"Gain - {name}", 
                                    "poster": poster,
                                    "profile_id": target['profile_id']
                                })
                    
                    elif video_id:
                        # Tekil Video (Film, Belgesel veya Tek Bölümlük İşler)
                        # Sadece Film kategorisindeyse veya gerçekten tekilse al
                        ctype = "Film" if target['type'] == "MOVIE" else "Program/Video"
                        
                        contents.append({
                            "id": video_id,
                            "title": name,
                            "group": f"Gain - {target['name']}",
                            "poster": poster,
                            "profile_id": target['profile_id']
                        })

            # Sonraki sayfaya geç
            page_index += 1
            time.sleep(0.5) # API'yi boğmamak için bekleme

        except Exception as e:
            print(f"🔥 Hata (Sayfa {page_index}): {e}")
            break

    print(f"   ✅ '{target['name']}' kategorisinden {len(contents)} video eklendi.")
    return contents

def get_stream_url(content):
    url = f"{BASE_API}/getPlaybackInfo/{content['profile_id']}/"
    params = {"videoContentId": content["id"], "packageType": "Dash", "__culture": "tr-tr"}
    try:
        res = requests.get(url, headers=HEADERS, params=params)
        if res.status_code == 200:
            data = res.json()
            # Bazen video şifreli olabilir, DRM kontrolü gerekebilir ama Gain genelde web için açık veriyor.
            pb_url = data.get("currentVideoContent", {}).get("playbackUrl")
            if pb_url:
                content["stream_url"] = pb_url
                return content
    except:
        pass
    return None

def save_m3u(data, filename="gain_archive.m3u"):
    print(f"\n📺 M3U oluşturuluyor: {filename}...")
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")
            for item in data:
                if not item.get("stream_url"): continue
                f.write(f'#EXTINF:-1 group-title="{item["group"]}" tvg-logo="{item["poster"]}", {item["title"]}\n')
                f.write('#EXTVLCOPT:http-user-agent=Mozilla/5.0\n')
                f.write(f"{item['stream_url']}\n")
        print("✅ M3U Hazır!")
    except Exception as e:
        print(f"Dosya yazma hatası: {e}")

def main():
    if "BURAYA" in MANUAL_TOKEN:
        print("⛔ Lütfen geçerli bir TOKEN yapıştırın!")
        return

    all_videos = []
    
    # Tüm hedefleri tara
    for target in TARGETS:
        items = get_contents(target)
        all_videos.extend(items)
        time.sleep(1)

    total = len(all_videos)
    if total == 0:
        print("\n⛔ HİÇ İÇERİK BULUNAMADI. Token süresi dolmuş veya IP engeli yemiş olabilirsiniz.")
        return

    print(f"\n🚀 TOPLAM {total} VİDEO İÇİN LİNKLER ÇEKİLİYOR... (Bu işlem biraz sürebilir)")

    final_list = []
    # Linkleri çekme döngüsü
    for i, video in enumerate(all_videos):
        full_data = get_stream_url(video)
        if full_data:
            # Gereksiz veriyi silip listeye ekle
            del full_data["profile_id"]
            final_list.append(full_data)
        
        # İlerleme çubuğu benzeri log
        if (i+1) % 10 == 0 or (i+1) == total: 
            print(f"   👍 {i+1}/{total} tamamlandı...")
        
        time.sleep(0.05) # Hızlı istek atıp ban yememek için

    # JSON Olarak Kaydet (Yedek)
    with open("gain_full_db.json", "w", encoding="utf-8") as f:
        json.dump(final_list, f, indent=4, ensure_ascii=False)

    # M3U Olarak Kaydet
    save_m3u(final_list, "gain_playlist.m3u")
    print("\n🏁 MUTLU SON! 'gain_playlist.m3u' dosyanız hazır.")

if __name__ == "__main__":
    main()
