import requests
import json
import sys
import time
from datetime import datetime

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

def giris_yap():
    """Giriş yapıp Token alır."""
    url = f"{API_BASE}/User/Login"
    payload = {"email": EMAIL, "password": SIFRE}
    
    print(f"🔐 Giriş yapılıyor...")
    try:
        response = requests.post(url, headers=HEADERS, json=payload, timeout=20)
        if response.status_code == 200:
            data = response.json()
            token = data.get("ServiceTicket") or data.get("Token") or data.get("Data", {}).get("Token")
            if token:
                print("✅ Giriş Başarılı!")
                return token
    except Exception as e:
        print(f"Giriş Hatası: {e}")
    
    print("❌ Giriş yapılamadı.")
    return None

def canli_yayinlari_cek(token):
    """Şu an yayında olan maçları çeker."""
    url = f"{API_BASE}/GetCurrentLiveContents"
    auth_headers = HEADERS.copy()
    auth_headers["Authorization"] = f"Bearer {token}"
    
    payload = {
        "action": "GetCurrentLiveContents",
        "pageNumber": 1,
        "count": 50,
        "TSID": int(time.time())
    }
    
    print("\n📡 CANLI YAYINLAR TARANIYOR...")
    try:
        response = requests.post(url, headers=auth_headers, json=payload)
        if response.status_code == 200:
            data = response.json()
            items = data.get("Data", [])
            print(f"✅ {len(items)} adet Canlı Yayın bulundu.")
            return items
        else:
            print(f"❌ Hata: {response.status_code}")
            return []
    except Exception as e:
        print(f"Hata: {e}")
        return []

def yayin_akisini_cek(token):
    """Bugünün yayın akışını (Maç programını) çeker."""
    # S Sport'ta yayın akışı genelde bu adrestedir
    url = f"{API_BASE}/EPG/GetDailyFlow"
    
    auth_headers = HEADERS.copy()
    auth_headers["Authorization"] = f"Bearer {token}"
    
    # Bugünün tarihi (Örn: 2024-01-24)
    bugun = datetime.now().strftime("%Y-%m-%d")
    
    params = {
        "day": "today",  # Veya "date": bugun
        "date": bugun
    }
    
    print(f"\n📅 BUGÜNÜN MAÇ PROGRAMI ÇEKİLİYOR ({bugun})...")
    try:
        response = requests.get(url, headers=auth_headers, params=params)
        if response.status_code == 200:
            data = response.json()
            # Yapı bazen değişebilir, genelde 'Data' veya direkt liste döner
            items = data.get("Data", []) if isinstance(data, dict) else data
            print(f"✅ {len(items)} adet Program/Maç bulundu.")
            return items
        else:
            print(f"❌ Akış çekilemedi: {response.status_code}")
            return []
    except Exception as e:
        print(f"Hata: {e}")
        return []

if __name__ == "__main__":
    token = giris_yap()
    
    if token:
        tum_veriler = {}
        
        # 1. Canlı Yayınları Al
        tum_veriler["Canli"] = canli_yayinlari_cek(token)
        
        # 2. Günlük Maç Programını Al
        tum_veriler["YayinAkisi"] = yayin_akisini_cek(token)
        
        # 3. Hepsini Tek Dosyaya Kaydet
        with open("mac_verileri.json", "w", encoding="utf-8") as f:
            json.dump(tum_veriler, f, indent=4, ensure_ascii=False)
            
        print("\n💾 TÜM VERİLER 'mac_verileri.json' OLARAK KAYDEDİLDİ.")
    else:
        sys.exit(1)
