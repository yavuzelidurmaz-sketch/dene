import requests
import json
import time

# --- TOKEN (MUTLAKA GÜNCEL OLANI YAPIŞTIR) ---
MANUAL_TOKEN = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJwcm9qZWN0SWQiOiIyZGE3a2Y4amYiLCJpZGVudGl0eSI6ImVuZHVzZXIiLCJhbm9ueW1vdXMiOmZhbHNlLCJ1c2VySWQiOiJlNGMzYWY2Yi05YWQyLTQ3NDYtYTVlNC0yNGQ1ODQyNjZmYzMiLCJjbGFpbXMiOnsiZW1haWwiOiJmYXRtYW51cnJrcmttenoxODZAZ21haWwuY29tIiwiZnVsbE5hbWUiOiJwaXJ0aXN0YW4iLCJwcm9maWxlSWQiOiJVUkNNUURMRExYSkxITFBGQkFOMFpJOVYiLCJwcm9maWxlQXZhdGFyIjoiUCIsImlzS2lkUHJvZmlsZSI6ZmFsc2V9LCJzZXNzaW9uSWQiOiIyOTVhNWM4N2RlYTk0Y2FhOTcyOTZlYzY2OWNiYjBmZCIsImlhdCI6MTc2OTE5NjA1MywiZXhwIjoxNzcxNzg4MDUzfQ.yKLLAEotOL9BWz3oFDsVyos7zcfMxnPFgRJpmsn50B6IbBe3SMgeZo02X0ghZdz93xB5kUETdBlDRmt1QHzAJ_7z_4qOLukh-z2pnPeaImVT-fRZGjK4Ez--GjRS_sOdnXgNVIdzYkiEsqyVabi8wL46K0C-1oo5B9bJ7sjAxaadAAs4rFKQ-bKx-c1rKgOso31XArEn3zIo0bhjhuvuOECNwvVbDu5Dg2LcgqkbDRA8LQ37iDudkaAwF9jVnxTNHLzmrxMf6KwftzgdmkIoizrsThFw1vVJWXTdaXNXlS5ZbOvC-iQ3UH3gAk2Yjv6gDxk0YgvRRYsDE3vwNKrbeQ"

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
