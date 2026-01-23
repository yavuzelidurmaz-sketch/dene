import requests
import json
import time

# --- TOKEN (YENİSİNİ ALIP YAPIŞTIR) ---
MANUAL_TOKEN = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJwcm9qZWN0SWQiOiIyZGE3a2Y4amYiLCJpZGVudGl0eSI6ImVuZHVzZXIiLCJhbm9ueW1vdXMiOmZhbHNlLCJ1c2VySWQiOiJlNGMzYWY2Yi05YWQyLTQ3NDYtYTVlNC0yNGQ1ODQyNjZmYzMiLCJjbGFpbXMiOnsiZW1haWwiOiJmYXRtYW51cnJrcmttenoxODZAZ21haWwuY29tIiwiZnVsbE5hbWUiOiJwaXJ0aXN0YW4iLCJwcm9maWxlSWQiOiJVUkNNUURMRExYSkxITFBGQkFOMFpJOVYiLCJwcm9maWxlQXZhdGFyIjoiUCIsImlzS2lkUHJvZmlsZSI6ZmFsc2V9LCJzZXNzaW9uSWQiOiJkMzdhMjlkMTMwOGE0NmRmOTA1NzQzZjg4ODdjZDliNiIsImlhdCI6MTc2OTE4NjUzMywiZXhwIjoxNzcxNzc4NTMzfQ.ci3CbqGQHVgUFIPs2PH_tR7CUTzN4HoKu3LY3zpFQztXlqZVgo_kXqp9A-6Pdn0G_R_BDtNC-sWS9eRzgka0KzlP228BGmZ87N_0wpxg1riHierd5LKIMZFNOJw-LkdQ3sFTWhGvD0zJm-lYYunh2gxtoWJXGVyuQYQSlt4xrPEMneUDbw-d0D2nVeJu_WVfkOPMFEC6bEmuFVIHgD6usMkd2_e9sr7mkt7GXwVBGuFJb9dK1p1nWb-KKXN7oIvf-eaxCbtAJ27Lja_NI-YlA8QjvwVsqnmf7qNuJpjJtorPSDvUcR6gp8oiZmzCw8zwJXoB79Xkmxlr0jnxDrTtIQ"

# --- SABİTLER ---
PROJECT_ID = "2da7kf8jf"
PROFILE_ID = "URCMQDLDLXJLHLPFBAN0ZI9V" 

# 1. Kategori Listesi URL
CATEGORY_URL = f"https://api.gain.tv/{PROJECT_ID}/CALL/ProfileTitle/getPlaylistsByCategory/{PROFILE_ID}?slug=%2Ffilm&__culture=tr-tr"

# 2. ID Çevirici URL (Başlık ID -> Gerçek ID)
METADATA_API_URL = "https://api.gain.tv/videos/"

# 3. Yayın Linki URL
PLAYBACK_URL_TEMPLATE = f"https://api.gain.tv/{PROJECT_ID}/CALL/ProfileTitle/getPlaybackInfo/{PROFILE_ID}/"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Content-Type": "application/json",
    "Accept": "application/json",
    "x-gain-platform": "web",
    "Origin": "https://www.gain.tv",
    "Referer": "https://www.gain.tv/"
}

def get_all_movies():
    """Film listesini indirir"""
    auth_headers = HEADERS.copy()
    auth_headers["Authorization"] = f"Bearer {MANUAL_TOKEN}"
    
    print(f"🌍 Film listesi indiriliyor...")
    try:
        response = requests.get(CATEGORY_URL, headers=auth_headers)
        data = response.json()
        playlists = data.get("playlists", [])
        
        movie_list = []
        processed_ids = set()

        for playlist in playlists:
            cat_title = playlist.get("title", "Genel")
            items = playlist.get("items", [])
            
            for item in items:
                title_id = item.get("titleId") # Bu kısa ID
                title = item.get("title") or item.get("originalTitle")
                poster = item.get("logoImageUrl") or item.get("posterImageUrl")

                if title_id and title_id not in processed_ids:
                    movie_list.append({
                        "short_id": title_id, # Bunu çevirmemiz gerekecek
                        "title": title,
                        "category": cat_title,
                        "poster": poster
                    })
                    processed_ids.add(title_id)
        
        print(f"📦 Listede {len(movie_list)} film bulundu. Linkler toplanıyor...")
        return movie_list
    except Exception as e:
        print(f"🔥 Liste Hatası: {e}")
        return []

def get_real_id(short_id):
    """Kısa ID'yi (NjBLOX...) Gerçek ID'ye (GUID) çevirir"""
    url = METADATA_API_URL + short_id
    auth_headers = HEADERS.copy()
    auth_headers["Authorization"] = f"Bearer {MANUAL_TOKEN}"
    
    try:
        response = requests.get(url, headers=auth_headers)
        if response.status_code == 200:
            data = response.json()
            return data.get("id") # İşte gerçek ID bu!
    except:
        pass
    return None

def get_stream_url(real_id):
    """Gerçek ID ile yayını çeker"""
    params = {
        "videoContentId": real_id, 
        "packageType": "Dash",
        "__culture": "tr-tr"
    }
    auth_headers = HEADERS.copy()
    auth_headers["Authorization"] = f"Bearer {MANUAL_TOKEN}"
    
    try:
        response = requests.get(PLAYBACK_URL_TEMPLATE, headers=auth_headers, params=params)
        if response.status_code == 200:
            data = response.json()
            if data.get("Success"):
                return data.get("Result", {})
    except:
        pass
    return None

def main():
    if "BURAYA" in MANUAL_TOKEN:
        print("⛔ Token girmeyi unutma!")
        return

    all_movies = get_all_movies()
    final_list = []
    
    # İlerlemeyi görmek için sayaç
    total = len(all_movies)
    
    for i, movie in enumerate(all_movies):
        # 1. Önce Gerçek ID'yi bul
        real_id = get_real_id(movie["short_id"])
        
        if real_id:
            # 2. Sonra Yayını Çek
            stream_data = get_stream_url(real_id)
            
            if stream_data:
                movie["stream_url"] = stream_data.get("Url")
                movie["license_url"] = stream_data.get("LicenseUrl")
                movie["real_id"] = real_id # Lazım olur diye bunu da kaydedelim
                
                final_list.append(movie)
                print(f"✅ [{i+1}/{total}] Alındı: {movie['title']}")
            else:
                print(f"❌ [{i+1}/{total}] Yayın Yok: {movie['title']}")
        else:
            print(f"❌ [{i+1}/{total}] ID Bulunamadı: {movie['title']}")
        
        time.sleep(0.1)

    print(f"\n💾 {len(final_list)} film 'gain_movies.json' dosyasına kaydediliyor...")
    with open("gain_movies.json", "w", encoding="utf-8") as f:
        json.dump(final_list, f, indent=4, ensure_ascii=False)
    print("🏁 İŞLEM TAMAMLANDI!")

if __name__ == "__main__":
    main()
