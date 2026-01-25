import requests
from bs4 import BeautifulSoup
import json
import time
import re
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from webdriver_manager.chrome import ChromeDriverManager

# --- AYARLAR ---
BASE_URL = "https://betparktv252.com"  
OUTPUT_FILE = "data.json"

# --- TARAYICIYI HAZIRLA (AĞ DİNLEME MODU) ---
def get_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Ekransız mod
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--mute-audio") # Sesi kapat
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    # Performans Loglarını Aç (Ağ trafiğini izlemek için)
    capabilities = DesiredCapabilities.CHROME
    capabilities["goog:loggingPrefs"] = {"performance": "ALL"}
    chrome_options.set_capability("goog:loggingPrefs", {"performance": "ALL"})

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def sniff_m3u8(driver, iframe_url):
    """
    Iframe adresine gider, videonun yüklenmesini bekler ve
    AĞ TRAFİĞİNDEN (Network Logs) .m3u8 linkini yakalar.
    """
    if not iframe_url: return None
    
    print(f"    -> Trafik dinleniyor: {iframe_url}")
    try:
        driver.get(iframe_url)
        time.sleep(5)  # Sayfanın ve playerın yüklenmesi için bekleme süresi (Gerekirse arttır)
        
        # Tarayıcının performans loglarını (Ağ istekleri dahil) çek
        logs = driver.get_log("performance")
        
        # Logları tersten tara (En son yüklenen genellikle master playlisttir)
        found_m3u8 = None
        
        for entry in logs:
            message = json.loads(entry["message"])["message"]
            
            # Sadece ağ isteklerini filtrele
            if message["method"] == "Network.requestWillBeSent":
                request_url = message["params"]["request"]["url"]
                
                # Linkin içinde .m3u8 geçiyor mu?
                if ".m3u8" in request_url:
                    found_m3u8 = request_url
                    # Eğer 'master.m3u8' bulursak en iyisi odur, direkt döndür
                    if "master.m3u8" in request_url or "playlist.m3u8" in request_url:
                         return request_url
        
        return found_m3u8

    except Exception as e:
        print(f"    [!] Sniff Hatası: {e}")
        return None

def main():
    print(f"[{datetime.now()}] Tarama Başlıyor (Network Sniffing Modu)...")
    
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        # Ana sayfayı normal requests ile çek (Hız için)
        response = requests.get(BASE_URL, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'lxml')
        
        data = {
            "meta": {
                "updated_at": str(datetime.now()),
                "source": BASE_URL
            },
            "matches": []
        }

        match_elements = soup.select('.bet-matches a.single-match')
        print(f"Toplam {len(match_elements)} maç bulundu. Tarayıcı başlatılıyor...")

        driver = get_driver()

        count = 0
        for match in match_elements:
            # GitHub Action süresi dolmasın diye test amaçlı limit koyabilirsin
            if count >= 30: break 
            
            home = match.get('data-home')
            away = match.get('data-away')
            match_title = f"{home} vs {away}"
            iframe_src = match.get('data-iframe')
            
            # Logolar
            home_logo = match.find('img', class_='homeLogo')['src'] if match.find('img', class_='homeLogo') else ""
            away_logo = match.find('img', class_='awayLogo')['src'] if match.find('img', class_='awayLogo') else ""

            stream_url = None
            if iframe_src:
                # Iframe linkini tarayıcıya gönder ve ağ trafiğini dinle
                stream_url = sniff_m3u8(driver, iframe_src)
            
            if stream_url:
                print(f" [V] YAKALANDI: {match_title}")
                print(f"     Link: {stream_url[:60]}...") # Linkin başını göster
            else:
                print(f" [X] Bulunamadı: {match_title}")

            # Referer Header'ı oluştur
            referer_header = "https://sttc2.kakirikodes.shop/"
            if iframe_src and "http" in iframe_src:
                try:
                    from urllib.parse import urlparse
                    parsed = urlparse(iframe_src)
                    referer_header = f"{parsed.scheme}://{parsed.netloc}/"
                except: pass

            data["matches"].append({
                "title": match_title,
                "home": home,
                "away": away,
                "time": match.get('data-saat'),
                "sport": match.get('data-matchtype'),
                "home_logo": home_logo,
                "away_logo": away_logo,
                "iframe_url": iframe_src,
                "stream_url": stream_url, # <-- BURASI DOLACAK
                "headers": {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                    "Referer": referer_header
                }
            })
            count += 1

        driver.quit()

        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
            
        print(f"\nİşlem bitti. Veriler kaydedildi.")

    except Exception as e:
        print(f"Genel Hata: {e}")
        try:
            driver.quit()
        except: pass

if __name__ == "__main__":
    main()
