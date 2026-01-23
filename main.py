import requests
import json
import time

# --- TOKEN (Senin verdiğin çalışan token) ---
MANUAL_TOKEN = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJwcm9qZWN0SWQiOiIyZGE3a2Y4amYiLCJpZGVudGl0eSI6ImVuZHVzZXIiLCJhbm9ueW1vdXMiOmZhbHNlLCJ1c2VySWQiOiJlNGMzYWY2Yi05YWQyLTQ3NDYtYTVlNC0yNGQ1ODQyNjZmYzMiLCJjbGFpbXMiOnsiZW1haWwiOiJmYXRtYW51cnJrcmttenoxODZAZ21haWwuY29tIiwiZnVsbE5hbWUiOiJwaXJ0aXN0YW4iLCJwcm9maWxlSWQiOiJVUkNNUURMRExYSkxITFBGQkFOMFpJOVYiLCJwcm9maWxlQXZhdGFyIjoiUCIsImlzS2lkUHJvZmlsZSI6ZmFsc2V9LCJzZXNzaW9uSWQiOiJkMzdhMjlkMTMwOGE0NmRmOTA1NzQzZjg4ODdjZDliNiIsImlhdCI6MTc2OTE4NjUzMywiZXhwIjoxNzcxNzc4NTMzfQ.ci3CbqGQHVgUFIPs2PH_tR7CUTzN4HoKu3LY3zpFQztXlqZVgo_kXqp9A-6Pdn0G_R_BDtNC-sWS9eRzgka0KzlP228BGmZ87N_0wpxg1riHierd5LKIMZFNOJw-LkdQ3sFTWhGvD0zJm-lYYunh2gxtoWJXGVyuQYQSlt4xrPEMneUDbw-d0D2nVeJu_WVfkOPMFEC6bEmuFVIHgD6usMkd2_e9sr7mkt7GXwVBGuFJb9dK1p1nWb-KKXN7oIvf-eaxCbtAJ27Lja_NI-YlA8QjvwVsqnmf7qNuJpjJtorPSDvUcR6gp8oiZmzCw8zwJXoB79Xkmxlr0jnxDrTtIQ"

# PROJE ID (Önceki loglardan bunu doğrulamıştık)
PROJECT_ID = "2da7kf8jf"

# API URL (Bu sefer App yöntemini deniyoruz, çünkü Token oraya ait olabilir)
CONTENT_URL = f"https://api.gain.tv/{PROJECT_ID}/CALL/Media/GetClientContent?__culture=tr-tr"

# HEADER
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Content-Type": "application/json",
    "Accept": "application/json",
    "x-gain-platform": "web", # Bunu web olarak bıraktık
    "Authorization": f"Bearer {MANUAL_TOKEN}" # Token'ı buraya ekledik
}

def get_video_details(video_id):
    print(f"📡 {video_id} için bağlanılıyor...")
    
    # App API'si POST isteği ve JSON gövdesi ister
    payload = {
        "MediaId": video_id,
        "IncludeOpencast": True
    }
    
    try:
        response = requests.post(CONTENT_URL, json=payload, headers=HEADERS)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("Success"):
                result = data.get("Result", {})
                title = result.get("Title", "Başlık Yok")
                print(f"✅ VİDEO BULUNDU: {title}")
                
                # Linkleri kontrol edelim
                assets = result.get("Assets", [])
                if assets:
                    print(f"   🔗 Yayın Linki Sayısı: {len(assets)}")
                    # İlk linki ekrana yazalım (Merakını gidermek için)
                    print(f"   🔗 Örnek Link: {assets[0].get('Url')}")
                
                return result
            else:
                print(f"❌ API Hatası: {data.get('Message')}")
                return None
        else:
            print(f"❌ HTTP Hatası ({video_id}): {response.status_code}")
            print(f"Detay: {response.text}") # Hata detayını görelim
            return None
    except Exception as e:
        print(f"🔥 Hata: {e}")
        return None

def main():
    target_ids = ["EFQ3X5f4"] 
    all_data = []

    for vid in target_ids:
        data = get_video_details(vid)
        if data:
            all_data.append(data)
        time.sleep(1)

    print("\n💾 gain_data.json kaydediliyor...")
    with open("gain_data.json", "w", encoding="utf-8") as f:
        json.dump(all_data, f, indent=4, ensure_ascii=False)
    print("🏁 İşlem tamam.")

if __name__ == "__main__":
    main()
