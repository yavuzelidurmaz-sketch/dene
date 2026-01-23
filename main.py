import requests
import json
import time

# --- SENİN VERDİĞİN TOKEN (Hazır Yerleştirildi) ---
# Bu anahtar sayesinde şifre girmeden direkt veriyi çekeceğiz.
MANUAL_TOKEN = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJwcm9qZWN0SWQiOiIyZGE3a2Y4amYiLCJpZGVudGl0eSI6ImVuZHVzZXIiLCJhbm9ueW1vdXMiOmZhbHNlLCJ1c2VySWQiOiJlNGMzYWY2Yi05YWQyLTQ3NDYtYTVlNC0yNGQ1ODQyNjZmYzMiLCJjbGFpbXMiOnsiZW1haWwiOiJmYXRtYW51cnJrcmttenoxODZAZ21haWwuY29tIiwiZnVsbE5hbWUiOiJwaXJ0aXN0YW4iLCJwcm9maWxlSWQiOiJVUkNNUURMRExYSkxITFBGQkFOMFpJOVYiLCJwcm9maWxlQXZhdGFyIjoiUCIsImlzS2lkUHJvZmlsZSI6ZmFsc2V9LCJzZXNzaW9uSWQiOiJkMzdhMjlkMTMwOGE0NmRmOTA1NzQzZjg4ODdjZDliNiIsImlhdCI6MTc2OTE4NjUzMywiZXhwIjoxNzcxNzc4NTMzfQ.ci3CbqGQHVgUFIPs2PH_tR7CUTzN4HoKu3LY3zpFQztXlqZVgo_kXqp9A-6Pdn0G_R_BDtNC-sWS9eRzgka0KzlP228BGmZ87N_0wpxg1riHierd5LKIMZFNOJw-LkdQ3sFTWhGvD0zJm-lYYunh2gxtoWJXGVyuQYQSlt4xrPEMneUDbw-d0D2nVeJu_WVfkOPMFEC6bEmuFVIHgD6usMkd2_e9sr7mkt7GXwVBGuFJb9dK1p1nWb-KKXN7oIvf-eaxCbtAJ27Lja_NI-YlA8QjvwVsqnmf7qNuJpjJtorPSDvUcR6gp8oiZmzCw8zwJXoB79Xkmxlr0jnxDrTtIQ"

# API URL'Sİ
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
    # Web API URL'si
    url = BASE_VIDEO_URL + video_id
    
    auth_headers = HEADERS.copy()
    # Token'ı başlığa ekliyoruz
    auth_headers["Authorization"] = f"Bearer {MANUAL_TOKEN}"
    
    try:
        response = requests.get(url, headers=auth_headers)
        
        if response.status_code == 200:
            data = response.json()
            title = data.get("title", "Başlık Yok")
            print(f"✅ BAŞARILI: {title} ({video_id}) verisi çekildi.")
            return data
        else:
            print(f"❌ Video Çekilemedi ({video_id}). Kod: {response.status_code}")
            return None
    except Exception as e:
        print(f"🔥 Hata: {e}")
        return None

def main():
    # Şimdilik test videosu
    target_ids = ["EFQ3X5f4"] 
    
    all_data = []
    print(f"\n🚀 {len(target_ids)} içerik taranacak...")

    for vid in target_ids:
        data = get_video_details(vid)
        if data:
            all_data.append(data)
        time.sleep(1)

    # Dosyayı kaydet
    print("\n💾 gain_data.json dosyası kaydediliyor...")
    with open("gain_data.json", "w", encoding="utf-8") as f:
        json.dump(all_data, f, indent=4, ensure_ascii=False)
    print("🏁 İşlem tamam.")

if __name__ == "__main__":
    main()
