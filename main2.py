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
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# --- AYARLAR ---
BASE_URL = "https://betparktv252.com"  
OUTPUT_FILE = "data.json"

def get_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--mute-audio")
    # Otomasyon tespitini zorlaştıran flagler
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    capabilities = DesiredCapabilities.CHROME
    capabilities["goog:loggingPrefs"] = {"performance": "ALL"}
    chrome_options.set_capability("goog:loggingPrefs", {"performance": "ALL"})

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def sniff_m3u8(driver, iframe_url, referer):
    """
    Iframe adresine gider, referer ekler, videoyu başlatmaya zorlar ve m3u8 çeker.
    """
    if not iframe_url: return None
    
    # URL // ile başlıyorsa https ekle
    if iframe_url.startswith("//"):
        iframe_url = "https:" + iframe_url

    print(f"    -> Analiz ediliyor: {iframe_url}")
    
    try:
        # --- KRİTİK HAMLE 1: Referer Header Ekleme (CDP ile) ---
        # Iframe'i direkt açtığımızda sunucu bizi engellemesin diye Referer ayarla
        driver.execute_cdp_cmd('Network.enable', {})
        driver.execute_cdp_cmd('Network.setExtraHTTPHeaders', {
            'headers': {'Referer': referer}
        })

        driver.get(iframe_url)
        
        # --- KRİTİK HAMLE 2: Videoyu Başlatmaya Zorla ---
        # Video başlamazsa network isteği oluşmaz. Sayfaya tıkla ve play komutu dene.
        time.sleep(2) # Sayfanın render olması için kısa bekleme
        
        try:
            # Önce sayfanın ortasına hayalet bir tıklama yap (Overlay reklam varsa geçer)
            driver.find_element(By.TAG_NAME, "body").click()
            
            # Video elementini bulup zorla oynat
            driver.execute_script("""
                var videos = document.querySelectorAll('video');
                videos.forEach(v => { v.muted = true; v.play(); });
                
                // Clappr veya JWPlayer gibi oynatıcılar varsa butonlarını bulup tıkla
                var playBtns = document.querySelectorAll('.vjs-big-play-button, .jw-display-icon-container, .play-wrapper');
                playBtns.forEach(btn => btn.click());
            """)
            print("    -> Oynatma tetiklendi...")
        except:
            pass # Hata verirse de devam et, belki autoplay açıktır

        # Network loglarının dolması için bekle
        time.sleep(4) 
        
        logs = driver.get_log("performance")
        found_m3u8 = None
        
        # Logları tersten tara (En son yüklenen genellikle en kalitelisidir)
        for entry in reversed(logs):
            try:
                message = json.loads(entry["message"])["message"]
                if message["method"] == "Network.requestWillBeSent":
                    request_url = message["params"]["request"]["url"]
                    
                    # .m3u8 veya .mp4 veya playlist linklerini yakala
                    if ".m3u8" in request_url or "playlist" in request_url:
                        # Gereksiz reklam m3u8'lerini ele (örneğin google ads)
                        if "google" not in request_url and "ads" not in request_url:
                            found_m3u8 = request_url
                            # Master bulursak döngüyü kır
                            if "master" in request_url:
                                break
            except:
                continue
        
        return found_m3u8

    except Exception as e:
        print(f"    [!] Sniff Hatası: {e}")
        return None

def main():
    print(f"[{datetime.now()}] Gelişmiş Tarama Başlıyor...")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Referer": "https://www.google.com/"
    }
    
    try:
        response = requests.get(BASE_URL, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'lxml')
        
        data = {"matches": []}
        match_elements = soup.select('.bet-matches a.single-match')
        print(f"Toplam {len(match_elements)} maç bulundu.")

        driver = get_driver()

        count = 0
        for match in match_elements:
            if count >= 30: break 
            
            home = match.get('data-home')
            away = match.get('data-away')
            iframe_src = match.get('data-iframe')
            
            # Görsel ve diğer detaylar
            home_logo = match.find('img', class_='homeLogo')['src'] if match.find('img', class_='homeLogo') else ""
            away_logo = match.find('img', class_='awayLogo')['src'] if match.find('img', class_='awayLogo') else ""
            match_title = f"{home} vs {away}"

            stream_url = None
            if iframe_src:
                # sniff fonksiyonuna REFERER olarak ana siteyi gönderiyoruz
                stream_url = sniff_m3u8(driver, iframe_src, BASE_URL)
            
            if stream_url:
                print(f" [V] YAKALANDI: {stream_url[:60]}...")
            else:
                print(f" [X] Bulunamadı: {match_title}")

            # Header oluşturma
            match_headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                "Referer": "https://sttc2.kakirikodes.shop/" # Genelde bu tür sitelerin player referer'ı
            }
            
            # Eğer stream url bulunduysa ve içinde token vs varsa referer iframe domaini olmalı
            if stream_url and iframe_src:
                 try:
                    from urllib.parse import urlparse
                    parsed = urlparse(iframe_src)
                    match_headers["Referer"] = f"{parsed.scheme}://{parsed.netloc}/"
                    match_headers["Origin"] = f"{parsed.scheme}://{parsed.netloc}"
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
                "stream_url": stream_url,
                "headers": match_headers
            })
            count += 1

        driver.quit()

        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
            
        print(f"\nİşlem bitti.")

    except Exception as e:
        print(f"Kritik Hata: {e}")
        try: driver.quit()
        except: pass

if __name__ == "__main__":
    main()
