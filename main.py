import requests
import json
import time

# --- TOKEN ---
# Tarayıcıdan aldığın "ey..." ile başlayan uzun kodu buraya tırnak içine yapıştır.
# Token'ın süresi dolmuş olabilir, taze bir tane alıp yapıştırman en iyisi.
MANUAL_TOKEN = "BURAYA_TARAYICIDAN_ALDIGIN_UZUN_TOKENI_YAPISTIR"

# --- BULDUĞUMUZ DEĞERLER ---
PROJECT_ID = "2da7kf8jf"
PROFILE_ID = "URCMQDLDLXJLHLPFBAN0ZI9V" # URL'den bulduğun sana özel ID

# API URL ŞABLONU
# Senin bulduğun yapı: /CALL/ProfileTitle/getPlaybackInfo/{PROFILE_ID}/
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
        "packageType": "Dash", # İstersen "Hls" de deneyebiliriz ama Dash bulmuşsun
        "__culture": "tr-tr"
    }
    
    auth_headers = HEADERS.copy()
    auth_headers["Authorization"] = f"Bearer {MANUAL_TOKEN}"
    
    try:
        print(f"📡 {video_id} için yayın linki isteniyor...")
        response = requests.get(PLAYBACK_URL, headers=auth_headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            
            # Başarılı olup olmadığını kontrol et
            if data.get("Success"):
                result = data.get("Result", {})
                
                # Yayın Linkini Bulalım (Genellikle 'Url' veya 'MediaUrl' içindedir)
                stream_url = result.get("Url")
                license_url = result.get("LicenseUrl") # DRM Lisans linki
                
                print(f"✅ VİDEO BİLGİLERİ ALINDI!")
                print(f"   🔗 Yayın Linki (.mpd): {stream_url}")
                if license_url:
                    print(f"   🔑 Lisans URL: {license_url}")
                
                return result
            else:
                print(f"❌ API Hatası: {data.get('Message')}")
                return None
        else:
            print(f"❌ HTTP Hatası: {response.status_code}")
            print(f"Detay: {response.text}")
            return None
            
    except Exception as e:
        print(f"🔥 Hata: {e}")
        return None

def main():
    # Token kontrolü
    if "BURAYA" in MANUAL_TOKEN:
        print("⛔ Token yapıştırmayı unuttun! Kodu düzenle.")
        return

    # Test videosu
    target_ids = ["B294FGF3xvkT"] 
    
    all_data = []

    for vid in target_ids:
        data = get_video_stream(vid)
        if data:
            all_data.append(data)
        time.sleep(1)

    # Dosyayı kaydet
    print("\n💾 gain_data.json kaydediliyor...")
    with open("gain_data.json", "w", encoding="utf-8") as f:
        json.dump(all_data, f, indent=4, ensure_ascii=False)
    print("🏁 İşlem tamam.")

if __name__ == "__main__":
    main()
