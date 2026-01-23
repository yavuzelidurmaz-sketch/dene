import requests
import json
import time

# --- TOKEN ---
# Tarayıcıdan aldığın "ey..." ile başlayan uzun kodu buraya tırnak içine yapıştır.
# Eğer hata alırsan tarayıcıdan yeni token kopyala.
MANUAL_TOKEN = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJwcm9qZWN0SWQiOiIyZGE3a2Y4amYiLCJpZGVudGl0eSI6ImVuZHVzZXIiLCJhbm9ueW1vdXMiOmZhbHNlLCJ1c2VySWQiOiJlNGMzYWY2Yi05YWQyLTQ3NDYtYTVlNC0yNGQ1ODQyNjZmYzMiLCJjbGFpbXMiOnsiZW1haWwiOiJmYXRtYW51cnJrcmttenoxODZAZ21haWwuY29tIiwiZnVsbE5hbWUiOiJwaXJ0aXN0YW4iLCJwcm9maWxlSWQiOiJVUkNNUURMRExYSkxITFBGQkFOMFpJOVYiLCJwcm9maWxlQXZhdGFyIjoiUCIsImlzS2lkUHJvZmlsZSI6ZmFsc2V9LCJzZXNzaW9uSWQiOiJkMzdhMjlkMTMwOGE0NmRmOTA1NzQzZjg4ODdjZDliNiIsImlhdCI6MTc2OTE4NjUzMywiZXhwIjoxNzcxNzc4NTMzfQ.ci3CbqGQHVgUFIPs2PH_tR7CUTzN4HoKu3LY3zpFQztXlqZVgo_kXqp9A-6Pdn0G_R_BDtNC-sWS9eRzgka0KzlP228BGmZ87N_0wpxg1riHierd5LKIMZFNOJw-LkdQ3sFTWhGvD0zJm-lYYunh2gxtoWJXGVyuQYQSlt4xrPEMneUDbw-d0D2nVeJu_WVfkOPMFEC6bEmuFVIHgD6usMkd2_e9sr7mkt7GXwVBGuFJb9dK1p1nWb-KKXN7oIvf-eaxCbtAJ27Lja_NI-YlA8QjvwVsqnmf7qNuJpjJtorPSDvUcR6gp8oiZmzCw8zwJXoB79Xkmxlr0jnxDrTtIQ"

# API URL (Web sitesinin kullandığı standart adres)
BASE_VIDEO_URL = "https://api.gain.tv/videos/"

# HEADER
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Content-Type": "application/json",
    "Accept": "application/json",
    "x-gain-platform": "web",
    "Origin": "https://www.gain.tv",
    "Referer": "https://www.gain.tv/"
}

def get_video_details(video_id):
    # Web API'si GET isteği kullanır (POST değil)
    url = BASE_VIDEO_URL + video_id
    
    auth_headers = HEADERS.copy()
    auth_headers["Authorization"] = f"Bearer {MANUAL_TOKEN}"
    
    try:
        print(f"📡 {video_id} için bağlanılıyor...")
        response = requests.get(url, headers=auth_headers)
        
        if response.status_code == 200:
            data = response.json()
            # Başlık bilgisini alalım
            title = data.get("title", "Başlık Yok")
            print(f"✅ VİDEO BULUNDU: {title}")
            
            # Yayın linki var mı diye bakalım (hls, mpd, streams vb.)
            if "streams" in data:
                print(f"   🔗 Yayın Akışları Mevcut: {len(data['streams'])} adet")
            
            return data
        else:
            print(f"❌ HTTP Hatası ({video_id}): {response.status_code}")
            # Hata detayını görelim (Token süresi dolmuş olabilir)
            if response.status_code == 401:
                print("⚠️ İPUCU: Token süresi dolmuş olabilir. Tarayıcıdan yeni token al.")
            return None
            
    except Exception as e:
        print(f"🔥 Hata: {e}")
        return None

def main():
    # Yeni verdiğin video linki: https://www.gain.tv/watch/B294FGF3xvkT
    # ID: B294FGF3xvkT
    target_ids = ["B294FGF3xvkT"] 
    
    all_data = []

    for vid in target_ids:
        data = get_video_details(vid)
        if data:
            all_data.append(data)
        time.sleep(1)

    print("\n💾 gain_data.json dosyası kaydediliyor...")
    with open("gain_data.json", "w", encoding="utf-8") as f:
        json.dump(all_data, f, indent=4, ensure_ascii=False)
    print("🏁 İşlem tamam.")

if __name__ == "__main__":
    main()
