import requests
import json
import time

# --- BİLGİLERİNİ BURAYA YAZ ---
EMAIL = "fatmanurrkrkmzz186@gmail.com"
# Şifreni tırnakların içine yaz:
PASSWORD = "Lordmaster5557."

# PROJE ID (Önceki hatadan çalışan ID'yi aldık)
PROJECT_ID = "2da7kf8jf"

# API URL'LERİ (App/Device API yapısı - Bu yapı 400 vererek çalıştığını kanıtladı)
LOGIN_URL = f"https://api.gain.tv/{PROJECT_ID}/CALL/User/signin?__culture=tr-tr"
CONTENT_URL = f"https://api.gain.tv/{PROJECT_ID}/CALL/Media/GetClientContent?__culture=tr-tr"

# HEADER
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Content-Type": "application/json",
    "Accept": "application/json"
}

def login():
    print(f"🔑 Giriş deneniyor: {EMAIL}")
    print(f"📡 URL: {LOGIN_URL}")
    
    # DÜZELTME: "Request" kutusunu kaldırdık. Direkt veriyoruz.
    # Önceki 400 hatası "missingProperty: password" demişti, yani bunu istiyor:
    payload = {
        "Email": EMAIL,
        "Password": PASSWORD
    }
    
    try:
        # App API'si genellikle POST ister
        response = requests.post(LOGIN_URL, json=payload, headers=HEADERS)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("Success"):
                result = data.get("Result", {})
                # Token bazen büyük harfle Token, bazen AccessToken döner
                token = result.get("Token") or result.get("AccessToken")
                print("✅ GİRİŞ BAŞARILI! Token alındı.")
                return token
            else:
                print(f"❌ Giriş Başarısız (API Mesajı): {data.get('Message')}")
                return None
        else:
            print(f"❌ HTTP Hatası: {response.status_code}")
            # Hatanın detayını görelim ki yine format hatası varsa anlayalım
            print(f"Detay: {response.text}")
            return None

    except Exception as e:
        print(f"🔥 Bağlantı Hatası: {e}")
        return None

def get_video_details(video_id, token):
    # App API'si video detayını da POST ile ister
    
    # Payload'ı da düzeltip düz gönderiyoruz
    payload = {
        "MediaId": video_id,
        "IncludeOpencast": True
    }
    
    auth_headers = HEADERS.copy()
    auth_headers["Authorization"] = f"Bearer {token}"
    
    try:
        response = requests.post(CONTENT_URL, json=payload, headers=auth_headers)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("Success"):
                result = data.get("Result", {})
                title = result.get("Title", "Başlık Yok")
                print(f"✅ Veri çekildi: {title} ({video_id})")
                return result
            else:
                print(f"❌ Video API Hatası: {data.get('Message')}")
                return None
        else:
            print(f"❌ HTTP Hatası ({video_id}): {response.status_code}")
            return None
    except Exception as e:
        print(f"🔥 Hata: {e}")
        return None

def main():
    token = login()
    if not token:
        print("⛔ Token alınamadı, işlem durduruluyor.")
        # Yine de boş dosya oluştur ki GitHub hata vermesin
        with open("gain_data.json", "w", encoding="utf-8") as f:
            f.write("[]")
        return

    # Şimdilik test videosu
    target_ids = ["EFQ3X5f4"] 
    
    all_data = []
    print(f"\n🚀 {len(target_ids)} içerik taranacak...")

    for vid in target_ids:
        data = get_video_details(vid, token)
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
