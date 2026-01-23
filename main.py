import requests
import json
import time
import os

# --- BİLGİLERİNİ BURAYA YAZ ---
EMAIL = "fatmanurrkrkmzz186@gmail.com"
# Şifreni tırnakların içine yaz:
PASSWORD = "Lordmaster5557."

# API URL'LERİ
LOGIN_URL = "https://api.gain.tv/auth/signin"
BASE_VIDEO_URL = "https://api.gain.tv/videos/"

# HEADER (Tarayıcı taklidi)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Content-Type": "application/json",
    "Accept": "application/json, text/plain, */*",
    "x-gain-platform": "web",
    "Origin": "https://www.gain.tv",
    "Referer": "https://www.gain.tv/"
}

def login():
    print(f"🔑 Giriş deneniyor: {EMAIL}")
    
    payload = {
        "email": EMAIL,
        "password": PASSWORD
    }
    # Culture parametresi önemli
    params = {"_culture": "tr-tr"}
    
    try:
        print("📡 Sunucuya istek gönderiliyor...")
        response = requests.post(LOGIN_URL, json=payload, headers=HEADERS, params=params)
        
        print(f"Durum Kodu: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("token") or data.get("accessToken")
            
            if token:
                print("✅ GİRİŞ BAŞARILI! Token alındı.")
                return token
            else:
                print(f"⚠️ Yanıt 200 OK ama Token yok. Gelen veri:\n{json.dumps(data, indent=2)}")
                return None
        else:
            print(f"❌ Giriş Başarısız!")
            print(f"Hata Mesajı: {response.text}") # Burası hatanın sebebini söyleyecek
            return None

    except Exception as e:
        print(f"🔥 Kritik Bağlantı Hatası: {e}")
        return None

def get_video_details(video_id, token):
    url = BASE_VIDEO_URL + video_id
    auth_headers = HEADERS.copy()
    auth_headers["Authorization"] = f"Bearer {token}"
    
    try:
        response = requests.get(url, headers=auth_headers)
        if response.status_code == 200:
            data = response.json()
            title = data.get("title", "Başlık Yok")
            print(f"✅ Veri çekildi: {title}")
            return data
        else:
            print(f"❌ Video Çekilemedi ({video_id}). Kod: {response.status_code}")
            return None
    except Exception as e:
        print(f"🔥 Video Hatası: {e}")
        return None

def main():
    all_data = []
    
    try:
        token = login()
        if token:
            target_ids = ["EFQ3X5f4"] 
            print(f"\n🚀 Taranıyor: {target_ids}")

            for vid in target_ids:
                data = get_video_details(vid, token)
                if data:
                    all_data.append(data)
                time.sleep(1)
        else:
            print("⛔ Token alınamadığı için video çekilemedi.")

    except Exception as e:
        print(f"🔥 Genel Program Hatası: {e}")
    
    finally:
        # Hata olsa bile dosyayı oluşturuyoruz ki GitHub kızmasın
        print("\n💾 gain_data.json dosyası oluşturuluyor...")
        with open("gain_data.json", "w", encoding="utf-8") as f:
            json.dump(all_data, f, indent=4, ensure_ascii=False)
        print(f"🏁 Dosya kaydedildi. (İçindeki veri sayısı: {len(all_data)})")

if __name__ == "__main__":
    main()
