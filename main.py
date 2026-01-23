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

# 2. Yayın Linki URL (Playback API)
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
    """Film listesini indirir ve GİZLİ ID'leri bulur"""
    auth_headers = HEADERS.copy()
    auth_headers["Authorization"] = f"Bearer {MANUAL_TOKEN}"
    
    print(f"🌍 Film listesi indiriliyor...")
    
    try:
        response = requests.get(CATEGORY_URL, headers=auth_headers)
        data = response.json()
        playlists = data.get("playlists", [])
        
        movie_list = []
        processed_ids = set()

        print(f"📦 {len(playlists)} kategori bulundu. Ayıklanıyor...")

        for playlist in playlists:
            cat_title = playlist.get("title", "Genel")
            items = playlist.get("items", [])
            
            for item in items:
                # --- İŞTE OLTAYI ATTIĞIMIZ YER ---
                # Eskiden 'titleId' alıyorduk, şimdi direkt 'videoContentId' alıyoruz.
                direct_id = item.get("videoContentId") 
                
                # İsim bazen 'name', bazen 'title' olabiliyor
                title = item.get("name") or item.get("title") or item.get("originalTitle")
                
                # Poster
                poster = item.get("logoImageUrl") or item.get("posterImageUrl")

                if direct_id and direct_id not in processed_ids:
                    movie_list.append({
                        "id": direct_id, # Bu ID ile direkt oynatabiliriz!
                        "title": title,
                        "category": cat_title,
                        "poster": poster
                    })
                    processed_ids.add(direct_id)
        
        print(f"✅ Toplam {len(movie_list)} film bulundu!")
        return movie_list

    except Exception as e:
        print(f"🔥 Liste Hatası: {e}")
        return []

def get_stream_url(movie):
    """Direkt ID ile yayın linkini çeker"""
    params = {
        "videoContentId": movie["id"], 
        "packageType": "Dash",
        "__culture": "tr-tr"
    }
    
    auth_headers = HEADERS.copy()
    auth_headers["Authorization"] = f"Bearer {MANUAL_TOKEN}"
    
    try:
        # print(f"   📡 {movie['title']} için link isteniyor...")
        response = requests.get(PLAYBACK_URL_TEMPLATE, headers=auth_headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("Success"):
                result = data.get("Result", {})
                
                movie["stream_url"] = result.get("Url")
                movie["license_url"] = result.get("LicenseUrl")
                return movie
            else:
                return None
        else:
            return None
    except Exception:
        return None

def main():
    if "BURAYA" in MANUAL_TOKEN:
        print("⛔ Token girmeyi unutma!")
        return

    # 1. Listeyi Bul
    all_movies = get_all_movies()
    
    if not all_movies:
        print("⚠️ Hiç film bulunamadı.")
        with open("gain_movies.json", "w", encoding="utf-8") as f:
            f.write("[]")
        return

    # 2. Detayları Çek
    total = len(all_movies)
    print(f"\n🚀 {total} film için yayın linkleri toplanıyor...")
    
    final_list = []
    
    for i, movie in enumerate(all_movies): 
        full_data = get_stream_url(movie)
        
        if full_data:
            final_list.append(full_data)
            print(f"✅ [{i+1}/{total}] Alındı: {movie['title']}")
        else:
            print(f"❌ [{i+1}/{total}] Alınamadı: {movie['title']}")
        
        time.sleep(0.1)

    # 3. Kaydet
    print(f"\n💾 {len(final_list)} film 'gain_movies.json' dosyasına kaydediliyor...")
    with open("gain_movies.json", "w", encoding="utf-8") as f:
        json.dump(final_list, f, indent=4, ensure_ascii=False)
    print("🏁 İŞLEM TAMAMLANDI!")

if __name__ == "__main__":
    main()
