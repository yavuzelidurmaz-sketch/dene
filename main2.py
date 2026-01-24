import requests
import json
import os
import sys

# Token'ı GitHub Secrets'tan alıyoruz (Güvenlik için)
TOKEN = os.environ.get("SSPORT_TOKEN")

if not TOKEN:
    print("HATA: Token bulunamadı! Lütfen GitHub Secrets'a 'SSPORT_TOKEN' ekleyin.")
    sys.exit(1)

# API Ayarları
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
    "Origin": "https://app.ssportplus.com",
    "Referer": "https://app.ssportplus.com/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
    "uilanguage": "tr"
}

API_BASE = "https://api.ssportplus.com/MW"

def veri_cek():
    endpoint = f"{API_BASE}/GetCurrentLiveContents"
    payload = {
        "action": "GetCurrentLiveContents",
        "pageNumber": 1,
        "count": 100,
        "TSID": 1769277736
    }
    
    print("Veri çekiliyor...")
    try:
        response = requests.post(endpoint, headers=HEADERS, json=payload)
        if response.status_code == 200:
            data = response.json()
            
            # Veriyi dosyaya yaz
            with open("canli_yayinlar.json", "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            print("✅ Veri başarıyla güncellendi: canli_yayinlar.json")
        else:
            print(f"❌ Hata: {response.status_code} - {response.text}")
            sys.exit(1) # Hata varsa Action'ı durdur
            
    except Exception as e:
        print(f"Script hatası: {e}")
        sys.exit(1)

if __name__ == "__main__":
    veri_cek()
