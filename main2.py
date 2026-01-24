import requests
from bs4 import BeautifulSoup
import json
import re
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# --- AYARLAR ---
BASE_URL = "https://betparktv252.com"  
OUTPUT_FILE = "data.json"

# --- SELENIUM AYARLARI ---
def get_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless") # Ekransız mod (Sunucuda çalışması için şart)
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    # GitHub Actions veya Local için Driver'ı otomatik kur
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def extract_m3u8_with_selenium(driver, iframe_url):
    """
    Gerçek tarayıcı ile iframe'e gider, JS'in çalışmasını bekler ve linki avlar.
    """
    if not iframe_url:
        return None
        
    print(f"    -> Tarayıcı ile link aranıyor: {iframe_url}")
    try:
        driver.get(iframe_url)
        time.sleep(3) # Sayfanın ve Player'ın yüklenmesi için bekle
        
        page_source = driver.page_source
        
        # 1. Yöntem: Sayfa kaynağında .m3u8 ara
        m3u8_pattern = r'(https?://[^\s"\']+\.m3u8[^\s"\']*)'
        matches = re.search(m3u8_pattern, page_source)
        
        if matches:
            return matches.group(1).replace('\\/', '/')
            
        # 2. Yöntem: Network loglarını dinlemek (Basit Selenium'da zordur, o yüzden kaynak koda güveniyoruz)
        # Genelde bu tür playerlar (kakirikodes) linki page_source içinde bir değişkende tutar.
        
    except Exception as e:
        print(f"    [!] Selenium Hatası: {e}")
        
    return None

def main():
    print(f"[{datetime.now()}] Tarama Başlıyor (Selenium Modu)...")
    
    # Önce hızlıca ana sayfayı Requests ile çekelim (Hız kazanmak için)
    # Sadece link çözme işini Selenium'a bırakacağız.
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(BASE_URL, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'lxml')
        
        data = {
            "meta": {
                "updated_at": str(datetime.now()),
                "source": BASE_URL
            },
            "matches": []
        }

        # Maçları bul
        match_elements = soup.select('.bet-matches a.single-match')
        print(f"Toplam {len(match_elements)} maç bulundu. Tarayıcı başlatılıyor...")

        # Tarayıcıyı başlat (Döngüden önce başlatmak performansı artırır)
        driver = get_driver()

        count = 0
        for match in match_elements:
            # Test için sadece ilk 10 maça bakalım (GitHub süresi dolmasın diye)
            # Hepsini istiyorsan bu 'if' bloğunu kaldır.
            # if count >= 10: break 
            
            home = match.get('data-home')
            away = match.get('data-away')
            match_title = f"{home} vs {away}"
            iframe_src = match.get('data-iframe')
            
            # Logolar
            home_logo_tag = match.find('img', class_='homeLogo')
            home_logo = home_logo_tag['src'] if home_logo_tag else ""
            away_logo_tag = match.find('img', class_='awayLogo')
            away_logo = away_logo_tag['src'] if away_logo_tag else ""

            # Eğer iframe linki varsa Selenium ile içine gir
            real_stream_url = None
            if iframe_src:
                real_stream_url = extract_m3u8_with_selenium(driver, iframe_src)
            
            if real_stream_url:
                print(f" [V] Link Bulundu: {match_title}")
            else:
                print(f" [X] Link Bulunamadı: {match_title}")

            data["matches"].append({
                "title": match_title,
                "home": home,
                "away": away,
                "time": match.get('data-saat'),
                "sport": match.get('data-matchtype'),
                "home_logo": home_logo,
                "away_logo": away_logo,
                "iframe_url": iframe_src,
                "stream_url": real_stream_url, # <-- Artık burası dolacak
                "headers": {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                    "Referer": "https://sttc2.kakirikodes.shop/"
                }
            })
            count += 1

        # Tarayıcıyı kapat
        driver.quit()

        # Kaydet
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
            
        print(f"\nİşlem bitti. Veriler kaydedildi.")

    except Exception as e:
        print(f"Genel Hata: {e}")
        try:
            driver.quit()
        except:
            pass

if __name__ == "__main__":
    main()
