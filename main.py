import requests
import json
import time

# --- TOKEN (YENİSİNİ ALIP YAPIŞTIRMAN GARANTİ OLUR) ---
MANUAL_TOKEN = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJwcm9qZWN0SWQiOiIyZGE3a2Y4amYiLCJpZGVudGl0eSI6ImVuZHVzZXIiLCJhbm9ueW1vdXMiOmZhbHNlLCJ1c2VySWQiOiJlNGMzYWY2Yi05YWQyLTQ3NDYtYTVlNC0yNGQ1ODQyNjZmYzMiLCJjbGFpbXMiOnsiZW1haWwiOiJmYXRtYW51cnJrcmttenoxODZAZ21haWwuY29tIiwiZnVsbE5hbWUiOiJwaXJ0aXN0YW4iLCJwcm9maWxlSWQiOiJVUkNNUURMRExYSkxITFBGQkFOMFpJOVYiLCJwcm9maWxlQXZhdGFyIjoiUCIsImlzS2lkUHJvZmlsZSI6ZmFsc2V9LCJzZXNzaW9uSWQiOiJkMzdhMjlkMTMwOGE0NmRmOTA1NzQzZjg4ODdjZDliNiIsImlhdCI6MTc2OTE4NjUzMywiZXhwIjoxNzcxNzc4NTMzfQ.ci3CbqGQHVgUFIPs2PH_tR7CUTzN4HoKu3LY3zpFQztXlqZVgo_kXqp9A-6Pdn0G_R_BDtNC-sWS9eRzgka0KzlP228BGmZ87N_0wpxg1riHierd5LKIMZFNOJw-LkdQ3sFTWhGvD0zJm-lYYunh2gxtoWJXGVyuQYQSlt4xrPEMneUDbw-d0D2nVeJu_WVfkOPMFEC6bEmuFVIHgD6usMkd2_e9sr7mkt7GXwVBGuFJb9dK1p1nWb-KKXN7oIvf-eaxCbtAJ27Lja_NI-YlA8QjvwVsqnmf7qNuJpjJtorPSDvUcR6gp8oiZmzCw8zwJXoB79Xkmxlr0jnxDrTtIQ"

# --- SABİTLER ---
PROJECT_ID = "2da7kf8jf"
PROFILE_ID = "URCMQDLDLXJLHLPFBAN0ZI9V" 

# URL'ler
CATEGORY_URL = f"https://api.gain.tv/{PROJECT_ID}/CALL/ProfileTitle/getPlaylistsByCategory/{PROFILE_ID}?slug=%2Ffilm&__culture=tr-tr"
PLAYBACK_URL_TEMPLATE = f"https://api.gain.tv/{PROJECT_ID}/CALL/ProfileTitle/getPlaybackInfo/{PROFILE_ID}/"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Content-Type": "application/json",
    "Accept": "application/json",
    "x-gain-platform": "web",
    "Origin": "https://www.gain.tv",
    "Referer": "https://www.gain.tv/"
}

def debug_playback():
    """Hatanın sebebini bulmak için detaylı sorgu yapar"""
    auth_headers = HEADERS.copy()
    auth_headers["Authorization"] = f"Bearer {MANUAL_TOKEN}"
    
    print(f"🌍 Film listesi indiriliyor...")
    
    # 1. Listeyi Çek
    try:
        response = requests.get(CATEGORY_URL, headers=auth_headers)
        if response.status_code != 200:
            print(f"❌ Liste alınamadı! Kod: {response.status_code}")
            print(f"   Cevap: {response.text}")
            return

        data = response.json()
        playlists = data.get("playlists", [])
        
        if not playlists:
            print("❌ Liste boş geldi.")
            return

        # İlk filmi bulalım
        first_item = playlists[0].get("items", [])[0]
        
        # Hem videoContentId hem titleId'yi deneyelim
        video_content_id = first_item.get("videoContentId")
        title_id = first_item.get("titleId")
        title = first_item.get("title") or first_item.get("name")
        
        print(f"\n🔎 İNCELENEN FİLM: {title}")
        print(f"   🔹 videoContentId: {video_content_id}")
        print(f"   🔹 titleId: {title_id}")
        
        # TEST: videoContentId ile deneme
        if video_content_id:
            print(f"\n🧪 TEST 1: 'videoContentId' ({video_content_id}) ile bağlanılıyor...")
            params = {
                "videoContentId": video_content_id, 
                "packageType": "Dash",
                "__culture": "tr-tr"
            }
            res = requests.get(PLAYBACK_URL_TEMPLATE, headers=auth_headers, params=params)
            
            print(f"   📡 Durum Kodu: {res.status_code}")
            print(f"   📄 SUNUCU CEVABI: {res.text}") # <-- İŞTE BU MESAJ LAZIM!
            
    except Exception as e:
        print(f"🔥 Hata: {e}")

def main():
    if "BURAYA" in MANUAL_TOKEN:
        print("⛔ Token girmeyi unutma!")
        return

    debug_playback()

if __name__ == "__main__":
    main()
