import requests
import json
import sys
import time

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

# ================= TÜRKİYE PROXY LİSTESİ =================
# Ücretsiz proxy'ler çabuk ölür. Buraya "IP:PORT" formatında çalışan TR proxy'leri eklenmeli.
# Kaynak siteler: spys.one/free-proxy-list/TR/ veya proxynova.com/proxy-server-list/country-tr/
PROXY_HAVUZU = [
    # Format: "ip:port"
    "88.255.102.126:8080", 
    "212.156.128.98:8080",
    "85.105.77.22:8080",
    "95.0.219.86:8080",
    "195.175.210.122:8080",
    "212.175.116.155:3128"
]

def calisan_proxy_bul():
    """Listeden çalışan bir proxy bulana kadar dener."""
    print(f"🌍 Toplam {len(PROXY_HAVUZU)} adet Proxy denenecek...")
    
    for ip in PROXY_HAVUZU:
        proxy = {"http": f"http://{ip}", "https": f"http://{ip}"}
        print(f"🔄 Deneniyor: {ip} ...", end="")
        
        try:
            # Sadece siteye erişim var mı diye basit bir test atıyoruz
            test = requests.get("https://api.ssportplus.com", proxies=proxy, timeout=5)
            if test.status_code < 500: # 404 veya 200 vermesi sitenin cevap verdiği anlamına gelir
                print(" ✅ ÇALIŞIYOR!")
                return proxy
        except:
            print(" ❌ BAŞARISIZ (Zaman Aşımı/Kapalı)")
            
    return None

def giris_yap(proxy):
    """Bulunan proxy ile giriş yapar."""
    url = f"{API_BASE}/User/Login"
    payload = {"email": EMAIL, "password": SIFRE}
    
    print(f"\n🔐 Giriş yapılıyor...")
    
    try:
        response = requests.post(url, headers=HEADERS, json=payload, proxies=proxy, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("ServiceTicket") or data.get("Token") or data.get("Data", {}).get("Token")
            
            if token:
                print("✅ GİRİŞ BAŞARILI! Token alındı.")
                return token
            else:
                print("⚠️ Giriş yapıldı ama token yok. Cevap:", data)
                return None
        else:
            print(f"❌ Giriş Reddedildi. Hata Kodu: {response.status_code}")
            # Eğer 403 veriyorsa Proxy TR değildir veya banlıdır.
            return None
            
    except Exception as e:
        print(f"Login sırasında hata: {e}")
        return None

def verileri_cek(token, proxy):
    """Maç verilerini çeker."""
    url = f"{API_BASE}/GetCurrentLiveContents"
    
    auth_headers = HEADERS.copy()
    auth_headers["Authorization"] = f"Bearer {token}"
    
    payload = {
        "action": "GetCurrentLiveContents",
        "pageNumber": 1,
        "count": 100,
        "TSID": int(time.time())
    }
    
    print("📡 Veriler çekiliyor...")
    
    try:
        response = requests.post(url, headers=auth_headers, json=payload, proxies=proxy, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            items = data.get("Data", [])
            print(f"✅ İŞLEM TAMAM! {len(items)} adet yayın bulundu.")
            
            with open("canli_yayinlar.json", "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            print("💾 Dosya kaydedildi: canli_yayinlar.json")
            return True
        else:
            print(f"❌ Veri Çekme Hatası: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"Hata: {e}")
        return False

if __name__ == "__main__":
    # 1. Adım: Çalışan Proxy Bul
    secilen_proxy = calisan_proxy_bul()
    
    if not secilen_proxy:
        print("\n🔴 HATA: Listedeki hiçbir Proxy çalışmadı!")
        print("Lütfen 'main.py' içindeki PROXY_HAVUZU listesine yeni 'Turkey Proxy IP'leri ekleyin.")
        print("Kaynak: https://spys.one/free-proxy-list/TR/")
        sys.exit(1)
        
    # 2. Adım: Giriş Yap
    token = giris_yap(secilen_proxy)
    
    # 3. Adım: Veri Çek
    if token:
        verileri_cek(token, secilen_proxy)
    else:
        sys.exit(1)
