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

# S Sport'u kandırmak için sahte başlıklar (Türkiye'denmiş gibi görünmek için)
def get_headers(fake_ip=None):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Content-Type": "application/json",
        "Origin": "https://app.ssportplus.com",
        "Referer": "https://app.ssportplus.com/",
        "uilanguage": "tr",
        "Accept": "application/json, text/plain, */*"
    }
    # Eğer IP taklidi yapacaksak bu başlıkları ekle
    if fake_ip:
        headers["X-Forwarded-For"] = fake_ip
        headers["X-Real-IP"] = fake_ip
        headers["Client-IP"] = fake_ip
    return headers

def taze_tr_proxy_bul():
    """İnternetten güncel Türkiye Proxy listesini indirir."""
    print("🌍 İnternetten taze Türkiye Proxy'leri aranıyor...")
    
    # Ücretsiz proxy kaynağı (Sadece TR)
    proxy_url = "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=5000&country=TR&ssl=all&anonymity=all"
    
    try:
        r = requests.get(proxy_url)
        if r.status_code == 200:
            proxies = r.text.strip().split("\n")
            # Temizle ve boşlukları at
            proxies = [p.strip() for p in proxies if p.strip()]
            print(f"✅ Toplam {len(proxies)} adet potansiyel TR Proxy bulundu.")
            return proxies
    except:
        print("Proxy listesi indirilemedi.")
    
    return []

def giris_yap_ve_veri_cek():
    # 1. Taze Proxy Listesini Al
    proxy_listesi = taze_tr_proxy_bul()
    
    # Listeye kendi manuel yedeklerimizi de ekleyelim (Ne olur ne olmaz)
    proxy_listesi.extend(["88.255.102.126:8080", "85.105.77.22:8080", "212.156.128.98:8080"])
    
    token = None
    calisan_session = None
    
    # 2. Proxy'leri Sırayla Dene
    print("🚀 Deneme başlatılıyor (Bu işlem biraz sürebilir)...")
    
    for proxy_ip in proxy_listesi:
        proxy_dict = {"http": f"http://{proxy_ip}", "https": f"http://{proxy_ip}"}
        
        # IP Spoofing (Başlık kandırmaca) için rastgele bir TR IP üretelim
        fake_tr_ip = f"88.255.{random.randint(10,200)}.{random.randint(10,200)}"
        
        print(f"🔄 Proxy deneniyor: {proxy_ip} ...", end="")
        
        try:
            # Önce Login Deneyelim
            login_url = f"{API_BASE}/User/Login"
            payload = {"email": EMAIL, "password": SIFRE}
            
            # Timeout'u kısa tutalım ki hızlı geçsin (5 saniye)
            resp = requests.post(
                login_url, 
                headers=get_headers(fake_tr_ip), 
                json=payload, 
                proxies=proxy_dict, 
                timeout=8
            )
            
            if resp.status_code == 200:
                data = resp.json()
                token = data.get("ServiceTicket") or data.get("Token") or data.get("Data", {}).get("Token")
                
                if token:
                    print(" ✅ BAŞARILI! Giriş yapıldı.")
                    calisan_session = proxy_dict
                    break # Döngüden çık, çalışanı bulduk
            elif resp.status_code == 403:
                print(" ❌ (Yasaklı Bölge)")
            else:
                print(f" ❌ (Hata: {resp.status_code})")
                
        except Exception as e:
            # Hata detayını yazdırma, sadece geç
            print(" ❌ (Zaman Aşımı/Ölü)")
            pass
            
    # 3. Eğer Token Alındıysa Veriyi Çek
    if token and calisan_session:
        print("\n📡 Canlı Yayınlar çekiliyor...")
        list_url = f"{API_BASE}/GetCurrentLiveContents"
        
        auth_headers = get_headers()
        auth_headers["Authorization"] = f"Bearer {token}"
        
        payload_data = {
            "action": "GetCurrentLiveContents",
            "pageNumber": 1,
            "count": 100,
            "TSID": int(time.time())
        }
        
        try:
            # Aynı proxy ile devam ediyoruz
            resp = requests.post(list_url, headers=auth_headers, json=payload_data, proxies=calisan_session, timeout=15)
            
            if resp.status_code == 200:
                data = resp.json()
                items = data.get("Data", [])
                
                print(f"✅ İŞLEM TAMAM! {len(items)} adet yayın bulundu.")
                
                # Dosyaya yaz
                with open("canli_yayinlar.json", "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=4, ensure_ascii=False)
                print("💾 Kayıt edildi: canli_yayinlar.json")
                
            else:
                print(f"❌ Veri çekerken hata: {resp.status_code}")
                sys.exit(1)
                
        except Exception as e:
            print(f"Veri çekme hatası: {e}")
            sys.exit(1)
    else:
        print("\n⛔ MAALESEF: Hiçbir çalışan Türkiye Proxy'si bulunamadı.")
        print("GitHub sunucuları Amerika'da olduğu için S Sport engelliyor.")
        print("Çözüm: Bu kodu kendi bilgisayarında çalıştırırsan %100 çalışır.")
        sys.exit(1)

if __name__ == "__main__":
    giris_yap_ve_veri_cek()
