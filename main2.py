import requests
import json
import sys
import time

# ================= KULLANICI BİLGİLERİ (GÖMÜLÜ) =================
# Senin verdiğin bilgiler buraya yazıldı.
EMAIL = "Tolgaatalay91@gmail.com"
SIFRE = "1324.Kova" 

# ================= AYARLAR =================
API_BASE = "https://api.ssportplus.com/MW"

# Tarayıcı gibi görünmek için başlıklar
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Content-Type": "application/json",
    "Origin": "https://app.ssportplus.com",
    "Referer": "https://app.ssportplus.com/",
    "uilanguage": "tr"
}

def giris_yap():
    """Siteye kullanıcı adı şifre ile girip Token alır."""
    url = f"{API_BASE}/User/Login"
    
    payload = {
        "email": EMAIL,
        "password": SIFRE
    }
    
    print(f"🔐 {EMAIL} ile giriş yapılıyor...")
    
    try:
        response = requests.post(url, headers=HEADERS, json=payload)
        
        # Cevabı kontrol edelim
        if response.status_code == 200:
            data = response.json()
            
            # Token genelde bu isimlerle gelir, hepsini kontrol ediyoruz
            token = data.get("ServiceTicket") or data.get("Token") or data.get("Data", {}).get("Token")
            
            if token:
                print("✅ Giriş Başarılı! Token alındı.")
                return token
            else:
                print("⚠️ Giriş yapıldı ama Token bulunamadı. Gelen cevap:")
                print(data)
                return None
        else:
            print(f"❌ Giriş Hatası! Kod: {response.status_code}")
            print("Cevap:", response.text)
            
            # Eğer 'VPN' veya 'Region' hatası varsa uyaralım
            if "VPN" in response.text or "Country" in response.text:
                print("\n🔴 KRİTİK HATA: S Sport, sunucunun yurtdışında olduğunu anladı ve engelledi.")
            return None
            
    except Exception as e:
        print(f"Bağlantı hatası: {e}")
        return None

def verileri_cek(token):
    """Alınan token ile canlı yayın listesini çeker."""
    url = f"{API_BASE}/GetCurrentLiveContents"
    
    # Token'ı başlığa ekle
    auth_headers = HEADERS.copy()
    auth_headers["Authorization"] = f"Bearer {token}"
    
    # İstek paketi
    payload = {
        "action": "GetCurrentLiveContents",
        "pageNumber": 1,
        "count": 100,
        "TSID": int(time.time())
    }
    
    print("📡 Canlı yayın listesi çekiliyor...")
    
    try:
        response = requests.post(url, headers=auth_headers, json=payload)
        
        if response.status_code == 200:
            data = response.json()
            
            # Dosyaya kaydet
            dosya_adi = "canli_yayinlar.json"
            with open(dosya_adi, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
                
            print(f"✅ İŞLEM TAMAM! Veriler '{dosya_adi}' dosyasına kaydedildi.")
            
            # Kaç yayın olduğunu gösterelim
            sayi = len(data.get("Data", []))
            print(f"Toplam {sayi} adet canlı içerik bulundu.")
            
        else:
            print(f"❌ Veri Çekme Hatası: {response.status_code}")
            print(response.text)
            sys.exit(1) # Action hata versin diye
            
    except Exception as e:
        print(f"Veri çekme sırasında hata: {e}")
        sys.exit(1)

if __name__ == "__main__":
    token = giris_yap()
    if token:
        verileri_cek(token)
    else:
        print("Login olunamadığı için işlem iptal edildi.")
        sys.exit(1)
