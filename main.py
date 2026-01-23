import requests
import json
import time

# --- TOKEN (YENİSİNİ ALIP YAPIŞTIR) ---
MANUAL_TOKEN = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJwcm9qZWN0SWQiOiIyZGE3a2Y4amYiLCJpZGVudGl0eSI6ImVuZHVzZXIiLCJhbm9ueW1vdXMiOmZhbHNlLCJ1c2VySWQiOiJlNGMzYWY2Yi05YWQyLTQ3NDYtYTVlNC0yNGQ1ODQyNjZmYzMiLCJjbGFpbXMiOnsiZW1haWwiOiJmYXRtYW51cnJrcmttenoxODZAZ21haWwuY29tIiwiZnVsbE5hbWUiOiJwaXJ0aXN0YW4iLCJwcm9maWxlSWQiOiJVUkNNUURMRExYSkxITFBGQkFOMFpJOVYiLCJwcm9maWxlQXZhdGFyIjoiUCIsImlzS2lkUHJvZmlsZSI6ZmFsc2V9LCJzZXNzaW9uSWQiOiJkMzdhMjlkMTMwOGE0NmRmOTA1NzQzZjg4ODdjZDliNiIsImlhdCI6MTc2OTE4NjUzMywiZXhwIjoxNzcxNzc4NTMzfQ.ci3CbqGQHVgUFIPs2PH_tR7CUTzN4HoKu3LY3zpFQztXlqZVgo_kXqp9A-6Pdn0G_R_BDtNC-sWS9eRzgka0KzlP228BGmZ87N_0wpxg1riHierd5LKIMZFNOJw-LkdQ3sFTWhGvD0zJm-lYYunh2gxtoWJXGVyuQYQSlt4xrPEMneUDbw-d0D2nVeJu_WVfkOPMFEC6bEmuFVIHgD6usMkd2_e9sr7mkt7GXwVBGuFJb9dK1p1nWb-KKXN7oIvf-eaxCbtAJ27Lja_NI-YlA8QjvwVsqnmf7qNuJpjJtorPSDvUcR6gp8oiZmzCw8zwJXoB79Xkmxlr0jnxDrTtIQ"

# --- SABİTLER ---
PROJECT_ID = "2da7kf8jf"
PROFILE_ID = "URCMQDLDLXJLHLPFBAN0ZI9V" 

# Kategori Listesi URL
CATEGORY_URL = f"https://api.gain.tv/{PROJECT_ID}/CALL/ProfileTitle/getPlaylistsByCategory/{PROFILE_ID}?slug=%2Ffilm&__culture=tr-tr"

# ID Çevirici URL
METADATA_API_URL = "https://api.gain.tv/videos/"

# Yayın Linki URL
PLAYBACK_URL_TEMPLATE = f"https://api.gain.tv/{PROJECT_ID}/CALL/ProfileTitle/getPlaybackInfo/{PROFILE_ID}/"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Content-Type": "application/json",
    "Accept": "application/json",
    "x-gain-platform": "web",
    "Origin": "https://www.gain.tv",
    "Referer": "https://www.gain.tv/"
}

def debug_extraction():
    """Verinin neden okunamadığını anlamak için detaylı analiz yapar"""
    auth_headers = HEADERS.copy()
    auth_headers["Authorization"] = f"Bearer {MANUAL_TOKEN}"
    
    print(f"🌍 Film listesi çekiliyor...")
    
    try:
        response = requests.get(CATEGORY_URL, headers=auth_headers)
        data = response.json()
        playlists = data.get("playlists", [])
        
        if not playlists:
            print("❌ Hiç çalma listesi bulunamadı!")
            return

        # İLK LİSTENİN İLK FİLMİNİ İNCELEYELİM
        first_playlist = playlists[0]
        items = first_playlist.get("items", [])
        
        if not items:
            print("❌ İlk listede hiç film yok.")
            return

        first_item = items[0]
        print("\n🔎 --- İLK FİLMİN HAM VERİSİ ---")
        print(json.dumps(first_item, indent=2, ensure_ascii=False))
        print("---------------------------------")
        
        # Test: ID'yi alıp çevirmeyi deneyelim
        short_id = first_item.get("titleId")
        print(f"\n🧪 Test Edilen ID: {short_id}")
        
        if short_id:
            # Metadata API'ye soralım
            url = METADATA_API_URL + short_id
            print(f"📡 API'ye Soruluyor: {url}")
            
            meta_response = requests.get(url, headers=auth_headers)
            print(f"   Durum Kodu: {meta_response.status_code}")
            
            if meta_response.status_code == 200:
                meta_data = meta_response.json()
                real_id = meta_data.get("id")
                real_title = meta_data.get("title")
                print(f"   ✅ BAŞARILI! Gerçek ID: {real_id}")
                print(f"   🎬 Film Adı: {real_title}")
            else:
                print(f"   ❌ BAŞARISIZ! Cevap: {meta_response.text}")
        else:
            print("❌ Bu item içinde 'titleId' bulunamadı!")

    except Exception as e:
        print(f"🔥 Kritik Hata: {e}")

def main():
    if "BURAYA" in MANUAL_TOKEN:
        print("⛔ Token girmeyi unutma!")
        return

    debug_extraction()

if __name__ == "__main__":
    main()
