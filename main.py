import requests
import json
import time

# --- BİLGİLERİNİ BURAYA YAZ ---
EMAIL = "fatmanurrkrkmzz186@gmail.com"
# Şifreni aşağıdaki tırnakların içine, boşluk bırakmadan yaz:
PASSWORD = "Lordmaster5557."

# API URL'LERİ (Web tarayıcısının kullandığı standart yapı)
LOGIN_URL = "https://api.gain.tv/auth/signin"
BASE_VIDEO_URL = "https://api.gain.tv/videos/"

# HEADER (Tarayıcı taklidi yapan kimlik bilgileri)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Content-Type": "application/json",
    "Accept": "application/json, text/plain, */*",
    "x-gain-platform": "web",
    "Origin": "https://www.gain.tv",
    "Referer": "https://www.gain.tv/"
}

def login():
    """Sisteme giriş yapar ve Token alır"""
    print(f"🔑 Giriş yapılıyor: {EMAIL}")
    
    # HATA DÜZELTİLDİ: Artık iç içe "Request" yok, doğrudan veriyoruz.
    payload = {
        "email": EMAIL,
        "password": PASSWORD
    }
    params = {"_culture": "tr-tr"}
    
    try:
        response = requests.post(LOGIN_URL, json=payload, headers=HEADERS, params=params)
        
        if response.status_code == 200:
            data = response.json()
            # Token bazen 'token', bazen 'accessToken' olarak gelir
            token = data.get("token") or data.get("accessToken")
            
            if token:
                print("✅ GİRİŞ BAŞARILI! Token alındı.")
                return token
            else:
                print(f"⚠️ Giriş OK ama Token yok. Gelen veri: {str(data)[:100]}...")
                return None
        else:
            print(f"❌ Giriş Başarısız! Hata Kodu: {response.status_code}")
            print(f"Sunucu Cevabı: {response.text}")
            return None
    except Exception as e:
        print(f"🔥 Bağlantı Hatası: {e}")
        return None

def get_video_details(video_id, token):
    """Video detaylarını çeker"""
    url = BASE_VIDEO_URL + video_id
    
    auth_headers = HEADERS.copy()
    auth_headers["Authorization"] = f"Bearer {token}"
    
    try:
        response = requests.get(url, headers=auth_headers)
        if response.status_code == 200:
            data = response.json()
            title = data.get("title", "Başlık Bulunamadı")
            print(f"✅ Veri çekildi: {title} ({video_id})")
            return data
        else:
            print(f"❌ {video_id} çekilemedi. Kod: {response.status_code}")
            return None
    except Exception as e:
        print(f"🔥 Hata: {e}")
        return None

def main():
    token = login()
    if not token:
        print("⛔ Token alınamadı, işlem iptal.")
        return

    # --- ŞİMDİLİK TEST LİSTESİ ---
    # Sistem çalışınca burayı "Tüm Listeyi Çek" moduyla değiştireceğiz.
    target_ids = ["EFQ3X5f4"] 
    
    all_data = []
    print(f"\n🚀 {len(target_ids)} adet içerik taranacak...")

    for vid in target_ids:
        data = get_video_details(vid, token)
        if data:
            all_data.append(data)
        time.sleep(1) # Seri istek atıp engellenmemek için bekleme

    # Dosyayı kaydet
    if all_data:
        print("\n💾 Dosya kaydediliyor...")
        with open("gain_data.json", "w", encoding="utf-8") as f:
            json.dump(all_data, f, indent=4, ensure_ascii=False)
        print("🏁 İşlem başarıyla tamamlandı.")
    else:
        print("⚠️ Hiç veri çekilemedi.")

if __name__ == "__main__":
    main()
