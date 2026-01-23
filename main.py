import requests
import json
import time

# --- TOKEN (Senin gönderdiğin token yerleştirildi) ---
# Başındaki "Bearer " kelimesini sildim, sadece kod kısmı gerekli.
MANUAL_TOKEN = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJwcm9qZWN0SWQiOiIyZGE3a2Y4amYiLCJpZGVudGl0eSI6ImVuZHVzZXIiLCJhbm9ueW1vdXMiOmZhbHNlLCJ1c2VySWQiOiJlNGMzYWY2Yi05YWQyLTQ3NDYtYTVlNC0yNGQ1ODQyNjZmYzMiLCJjbGFpbXMiOnsiZW1haWwiOiJmYXRtYW51cnJrcmttenoxODZAZ21haWwuY29tIiwiZnVsbE5hbWUiOiJwaXJ0aXN0YW4iLCJwcm9maWxlSWQiOiJVUkNNUURMRExYSkxITFBGQkFOMFpJOVYiLCJwcm9maWxlQXZhdGFyIjoiUCIsImlzS2lkUHJvZmlsZSI6ZmFsc2V9LCJzZXNzaW9uSWQiOiJkMzdhMjlkMTMwOGE0NmRmOTA1NzQzZjg4ODdjZDliNiIsImlhdCI6MTc2OTE4NjUzMywiZXhwIjoxNzcxNzc4NTMzfQ.ci3CbqGQHVgUFIPs2PH_tR7CUTzN4HoKu3LY3zpFQztXlqZVgo_kXqp9A-6Pdn0G_R_BDtNC-sWS9eRzgka0KzlP228BGmZ87N_0wpxg1riHierd5LKIMZFNOJw-LkdQ3sFTWhGvD0zJm-lYYunh2gxtoWJXGVyuQYQSlt4xrPEMneUDbw-d0D2nVeJu_WVfkOPMFEC6bEmuFVIHgD6usMkd2_e9sr7mkt7GXwVBGuFJb9dK1p1nWb-KKXN7oIvf-eaxCbtAJ27Lja_NI-YlA8QjvwVsqnmf7qNuJpjJtorPSDvUcR6gp8oiZmzCw8zwJXoB79Xkmxlr0jnxDrTtIQ"

# --- URL'DEN BULDUĞUMUZ DEĞERLER ---
PROJECT_ID = "2da7kf8jf"
PROFILE_ID = "URCMQDLDLXJLHLPFBAN0ZI9V" 

# API URL (PlaybackInfo - Doğru Adres)
PLAYBACK_URL = f"https://api.gain.tv/{PROJECT_ID}/CALL/ProfileTitle/getPlaybackInfo/{PROFILE_ID}/"

# HEADER
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Content-Type": "application/json",
    "Accept": "application/json",
    "x-gain-platform": "web",
    "Origin": "https://www.gain.tv",
    "Referer": "https://www.gain.tv/"
}

def get_video_stream(video_id):
    # Senin bulduğun URL parametreleri
    params = {
        "videoContentId": video_id,
        "packageType": "Dash",
        "__culture": "tr-tr"
    }
    
    auth_headers = HEADERS.copy()
    auth_headers["Authorization"] = f"Bearer {MANUAL_TOKEN}"
    
    try:
        print(f"📡 {video_id} için yayın linki isteniyor...")
        response = requests.get(PLAYBACK_URL, headers=auth_headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get("Success"):
                result = data.get("Result", {})
                stream_url = result.get("Url")
                license_url = result.get("LicenseUrl")
                
                print(f"✅ VİDEO BİLGİLERİ ALINDI!")
                # GitHub loglarında linki görmek için yazdırıyoruz
                print(f"   🔗 Stream URL: {stream_url}")
                if license_url:
                    print(f"   🔑 Lisans URL: {license_url}")
                
                return result
            else:
                print(f"❌ API Hatası: {data.get('Message')}")
                # Hata detayını görelim
                print(json.dumps(data, indent=2))
                return None
        else:
            print(f"❌ HTTP Hatası: {response.status_code}")
            print(f"Detay: {response.text}")
            return None
            
    except Exception as e:
        print(f"🔥 Hata: {e}")
        return None

def main():
    # Test videosu (Senin verdiğin ID)
    target_ids = ["B294FGF3xvkT"] 
    
    all_data = []

    for vid in target_ids:
        data = get_video_stream(vid)
        if data:
            all_data.append(data)
        time.sleep(1)

    print("\n💾 gain_data.json kaydediliyor...")
    with open("gain_data.json", "w", encoding="utf-8") as f:
        json.dump(all_data, f, indent=4, ensure_ascii=False)
    print("🏁 İşlem tamam.")

if __name__ == "__main__":
    main()
