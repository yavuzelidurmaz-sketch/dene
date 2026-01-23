import requests
import json
import time

# --- TOKEN (Tarayıcıdan taze token alıp buraya yapıştır) ---
MANUAL_TOKEN = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJwcm9qZWN0SWQiOiIyZGE3a2Y4amYiLCJpZGVudGl0eSI6ImVuZHVzZXIiLCJhbm9ueW1vdXMiOmZhbHNlLCJ1c2VySWQiOiJlNGMzYWY2Yi05YWQyLTQ3NDYtYTVlNC0yNGQ1ODQyNjZmYzMiLCJjbGFpbXMiOnsiZW1haWwiOiJmYXRtYW51cnJrcmttenoxODZAZ21haWwuY29tIiwiZnVsbE5hbWUiOiJwaXJ0aXN0YW4iLCJwcm9maWxlSWQiOiJVUkNNUURMRExYSkxITFBGQkFOMFpJOVYiLCJwcm9maWxlQXZhdGFyIjoiUCIsImlzS2lkUHJvZmlsZSI6ZmFsc2V9LCJzZXNzaW9uSWQiOiJkMzdhMjlkMTMwOGE0NmRmOTA1NzQzZjg4ODdjZDliNiIsImlhdCI6MTc2OTE4NjUzMywiZXhwIjoxNzcxNzc4NTMzfQ.ci3CbqGQHVgUFIPs2PH_tR7CUTzN4HoKu3LY3zpFQztXlqZVgo_kXqp9A-6Pdn0G_R_BDtNC-sWS9eRzgka0KzlP228BGmZ87N_0wpxg1riHierd5LKIMZFNOJw-LkdQ3sFTWhGvD0zJm-lYYunh2gxtoWJXGVyuQYQSlt4xrPEMneUDbw-d0D2nVeJu_WVfkOPMFEC6bEmuFVIHgD6usMkd2_e9sr7mkt7GXwVBGuFJb9dK1p1nWb-KKXN7oIvf-eaxCbtAJ27Lja_NI-YlA8QjvwVsqnmf7qNuJpjJtorPSDvUcR6gp8oiZmzCw8zwJXoB79Xkmxlr0jnxDrTtIQ"

# --- SABİTLER ---
PROJECT_ID = "2da7kf8jf"
PROFILE_ID = "URCMQDLDLXJLHLPFBAN0ZI9V" 

# 1. Aşama URL: Kısa koddan (Slug) tüm bilgileri çeken Web API'si
METADATA_API_URL = "https://api.gain.tv/videos/"

# 2. Aşama URL: Gerçek ID ile yayın linkini veren Player API'si
PLAYBACK_URL = f"https://api.gain.tv/{PROJECT_ID}/CALL/ProfileTitle/getPlaybackInfo/{PROFILE_ID}/"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Content-Type": "application/json",
    "Accept": "application/json",
    "x-gain-platform": "web",
    "Origin": "https://www.gain.tv",
    "Referer": "https://www.gain.tv/"
}

def get_real_id_via_api(slug):
    """HTML yerine direkt API'ye sorarak Gerçek ID'yi bulur"""
    url = METADATA_API_URL + slug
    
    auth_headers = HEADERS.copy()
    auth_headers["Authorization"] = f"Bearer {MANUAL_TOKEN}"
    
    try:
        print(f"🔍 '{slug}' için API'den bilgi isteniyor...")
        response = requests.get(url, headers=auth_headers)
        
        if response.status_code == 200:
            data = response.json()
            real_id = data.get("id")
            title = data.get("title")
            
            if real_id:
                print(f"✅ METADATA BULUNDU: {title}")
                print(f"   🆔 Gerçek ID (GUID): {real_id}")
                return real_id
            else:
                print("⚠️ API yanıt verdi ama içinde ID yok.")
                return None
        else:
            print(f"❌ Metadata Alınamadı. Kod: {response.status_code}")
            return None
    except Exception as e:
        print(f"🔥 Hata (Metadata): {e}")
        return None

def get_stream_url(real_id):
    """Gerçek ID ile yayın linkini çeker"""
    params = {
        "videoContentId": real_id, 
        "packageType": "Dash",
        "__culture": "tr-tr"
    }
    
    auth_headers = HEADERS.copy()
    auth_headers["Authorization"] = f"Bearer {MANUAL_TOKEN}"
    
    try:
        print(f"📡 Yayın linki isteniyor (ID: {real_id})...")
        response = requests.get(PLAYBACK_URL, headers=auth_headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("Success"):
                result = data.get("Result", {})
                stream_url = result.get("Url")
                license_url = result.get("LicenseUrl")
                
                print(f"✅✅ YAYIN LİNKİ ALINDI!")
                print(f"   🔗 LINK: {stream_url}")
                if license_url:
                    print(f"   🔑 LICENSE: {license_url}")
                return result
            else:
                print(f"❌ API Reddedildi: {data.get('Message')}")
                return None
        else:
            print(f"❌ HTTP Hatası: {response.status_code}")
            return None
    except Exception as e:
        print(f"🔥 Hata (Playback): {e}")
        return None

def main():
    if "BURAYA" in MANUAL_TOKEN:
        print("⛔ Token'ı güncellemeyi unutma!")
        return

    # Tarayıcıdaki Kısa Link (Slug)
    target_slug = "B294FGF3xvkT" 
    
    all_data = []

    # 1. Adım: API'den Gerçek ID'yi bul
    real_id = get_real_id_via_api(target_slug)
    
    # 2. Adım: Yayın linkini çek
    if real_id:
        data = get_stream_url(real_id)
        if data:
            all_data.append(data)

    print("\n💾 gain_data.json kaydediliyor...")
    with open("gain_data.json", "w", encoding="utf-8") as f:
        json.dump(all_data, f, indent=4, ensure_ascii=False)
    print("🏁 İşlem tamam.")

if __name__ == "__main__":
    main()
