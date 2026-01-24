import requests
import json
import sys
import time
import random

# ================= KULLANICI BİLGİLERİ =================
EMAIL = "Tolgaatalay91@gmail.com"
SIFRE = "1324.Kova" 

# ================= AYARLAR =================
API_BASE = "https://api.ssportplus.com/MW"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Content-Type": "application/json",
    "Origin": "https://app.ssportplus.com",
    "Referer": "https://app.ssportplus.com/",
    "uilanguage": "tr"
}

# --- TÜRKİYE PROXY LİSTESİ (Deneme için) ---
# GitHub sunucusu yurtdışında olduğu için trafiği Türkiye üzerinden geçirmeliyiz.
# Eğer bunlar çalışmazsa taze bir proxy bulup buraya yazmalısın.
PROXY_LISTESI = [
    # Format: "ip:port"
    "88.255.102.126:8080",
    "85.105.77.22:8080",
    "212.156.128.98:8080"
]

def get_proxy():
    """Rastgele bir TR proxy seçer ve requests formatına sokar."""
    proxy_ip = random.choice(PROXY_LISTESI)
    print(f"🌍 Bağlantı şu Türkiye Proxy üzerinden denenecek: {proxy_ip}")
    return {
        "http": f"http://{proxy_ip}",
        "https": f"http://{proxy_ip}"
    }

def giris_yap(proxy):
    """Siteye giriş yapıp Token alır."""
    url = f"{API_BASE}/User/Login"
    payload = {"email": EMAIL, "password": SIFRE}
    
    print(f"🔐 Giriş deneniyor...")
    
    try:
        # Timeout ekledik çünkü proxy yavaş olabilir
        response = requests.post(url, headers=HEADERS, json=payload, proxies=proxy, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("ServiceTicket") or data.get("Token") or data.get("Data", {}).get("Token")
            
            if token:
                print("✅ Giriş Başarılı! Token alındı.")
                return token
            else:
                print("⚠️ Token bulunamadı. Cevap:", data)
                return None
        else:
            print(f"❌ Giriş Başarısız. Hata Kodu: {response.status_code}")
            print("Sunucu Cevabı:", response.text)
            return None
            
    except Exception as e:
        print(f"Bağlantı/Proxy hatası: {e}")
        return None

def kategorileri_tara(token, proxy):
    """Kategorileri tek tek tarar."""
    kategoriler = ["Film", "Dizi", "Program", "Belgesel", "Kids"]
    bulunan_icerikler = []
    
    auth_headers = HEADERS.copy()
    auth_headers["Authorization"] = f"Bearer {token}"
    
    url = f"{API_BASE}/GetCategories" # Kategori endpointi (Tahmini)
    # Veya canlı yayın endpointi ile test edelim, en garantisi o:
    url_live = f"{API_BASE}/GetCurrentLiveContents"

    # Test için Canlı Yayınları çekiyoruz (Daha garanti)
    print("\n🌍 CANLI YAYINLAR TARANIYOR...")
    payload = {
        "action": "GetCurrentLiveContents",
        "pageNumber": 1,
        "count": 100,
        "TSID": int(time.time())
    }

    try:
        response = requests.post(url_live, headers=auth_headers, json=payload, proxies=proxy, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            items = data.get("Data", [])
            print(f"✅ Başarılı! {len(items)} adet içerik bulundu.")
            
            # Kaydet
            with open("canli_yayinlar.json", "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            print("💾 Dosya kaydedildi: canli_yayinlar.json")
            
        else:
            print(f"❌ Erişim Hatası (Kod {response.status_code})")
            print("Detay:", response.text) # Hatanın sebebini görmek için
            
    except Exception as e:
        print(f"Hata oluştu: {e}")

if __name__ == "__main__":
    # Proxy seç
    secilen_proxy = get_proxy()
    
    # İşlemi başlat
    token = giris_yap(secilen_proxy)
    
    if token:
        kategorileri_tara(token, secilen_proxy)
    else:
        print("\n🛑 Token alınamadığı için işlem durduruldu.")
        # GitHub Action hata versin diye
        sys.exit(1)
