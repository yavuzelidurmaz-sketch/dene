import requests
import json
import os

# --- AYARLAR (TOKEN İÇİNDE GÖMÜLÜ) ---
TOKEN = "59790226f62e8e4df21962131f0f431dc9500f289c8d40ee1f8e359df201ee64565485371940835d426b5b777fb896db"

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
    "Origin": "https://app.ssportplus.com",
    "Referer": "https://app.ssportplus.com/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
    "uilanguage": "tr",
    "sngt": "1079460410356963642469465811" # cURL'den gelen güvenlik parametresi
}

def veri_cek():
    url = "https://api.ssportplus.com/MW/GetCurrentLiveContents"
    
    payload = {
        "action": "GetCurrentLiveContents",
        "pageNumber": 1,
        "count": 100,
        "TSID": 1769277736
    }
    
    print("Veriler çekiliyor...")
    
    try:
        response = requests.post(url, headers=HEADERS, json=payload)
        
        if response.status_code == 200:
            data = response.json()
            
            # Veriyi dosyaya yaz
            with open("canli_yayinlar.json", "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            
            print("✅ İŞLEM BAŞARILI! 'canli_yayinlar.json' oluşturuldu.")
            
            # Örnek olarak kaç yayın olduğunu yazdıralım
            if "Data" in data:
                print(f"Toplam {len(data['Data'])} adet canlı yayın bulundu.")
        else:
            print(f"❌ HATA: {response.status_code}")
            print(response.text)
            exit(1) # GitHub Action hatayı görsün diye
            
    except Exception as e:
        print(f"Kod hatası: {e}")
        exit(1)

if __name__ == "__main__":
    veri_cek()
