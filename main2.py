import time
import json
import re
import base64
from datetime import datetime
import requests
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# --- AYARLAR ---
BASE_URL = "https://betparktv252.com"  
OUTPUT_FILE = "data.json"

def get_driver():
    """Anti-detect özellikli Selenium tarayıcısı hazırlar"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Arka planda çalış
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--mute-audio")
    
    # Cloudflare ve Bot korumasını aşmak için kritik ayarlar
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # Navigator.webdriver izini sil
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    return driver

def solve_with_selenium_source(driver, iframe_url):
    """
    Selenium ile sayfayı açar (Cloudflare'i geçer),
    Sonra HTML kaynağını alıp Regex ile tokenKey'i çözer.
    """
    if not iframe_url: return None
    if iframe_url.startswith("//"): iframe_url = "https:" + iframe_url
    
    print(f"    -> Siteye giriliyor (Selenium): {iframe_url}")
    
    try:
        driver.get(iframe_url)
        # Sayfanın ve JS'in yüklenmesi için bekle (Cloudflare kontrolü burada geçilir)
        time.sleep(4) 
        
        # Sayfanın işlenmiş HTML kodunu al
        page_source = driver.page_source
        
        # --- 1. YÖNTEM: tokenKey Regex ---
        # Sayfa kaynağında 'var tokenKey = "..."' arıyoruz
        pattern = r"var\s+tokenKey\s*=\s*['\"]([^'\"]+)['\"]"
        match = re.search(pattern, page_source)
        
        if match:
            encoded_str = match.group(1)
            try:
                decoded_bytes = base64.b64decode(encoded_str)
                m3u8_url = decoded_bytes.decode('utf-8').strip()
                return m3u8_url
            except:
                pass # Base64 hatası olursa devam et

        # --- 2. YÖNTEM: Direkt Link (source: '...') ---
        # Bazen token yoktur, direkt .m3u8 yazar
        match_direct = re.search(r"['\"](https?://[^'\"]+\.m3u8[^'\"]*)['\"]", page_source)
        if match_direct:
            return match_direct.group(1)

        # Hata ayıklama: Eğer bulamazsa sayfanın başını yazdıralım ki ne görüyor anlayalım
        # print(f"DEBUG HTML: {page_source[:200]}") 
        
        return None

    except Exception as e:
        print(f"    [!] Selenium Hatası: {e}")
        return None

def main():
    print(f"[{datetime.now()}] Tarama Başlıyor (Hibrit Mod: Selenium + Regex)...")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Referer": "https://www.google.com/"
    }
    
    # Driver'ı döngü dışında bir kere başlat (Performans için)
    driver = get_driver()
    
    try:
        # Ana sayfayı requests ile hızlıca çek
        response = requests.get(BASE_URL, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'lxml')
        
        data = {"matches": []}
        match_elements = soup.select('.bet-matches a.single-match')
        print(f"Toplam {len(match_elements)} maç bulundu. Analiz başlıyor...")

        count = 0
        for match in match_elements:
            # Test için sayı limiti (İstersen kaldır)
            if count >= 30: break 
            
            home = match.get('data-home')
            away = match.get('data-away')
            iframe_src = match.get('data-iframe')
            match_title = f"{home} vs {away}"
            
            home_logo = match.find('img', class_='homeLogo')['src'] if match.find('img', class_='homeLogo') else ""
            away_logo = match.find('img', class_='awayLogo')['src'] if match.find('img', class_='awayLogo') else ""

            stream_url = None
            if iframe_src:
                # Hibrit fonksiyonu çağır
                stream_url = solve_with_selenium_source(driver, iframe_src)
            
            if stream_url:
                print(f" [V] YAKALANDI: {match_title}")
                print(f"     Link: {stream_url}")
            else:
                print(f" [X] Bulunamadı: {match_title}")

            # Headers oluştur
            request_headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                "Referer": "https://sttc2.kakirikodes.shop/"
            }
            if iframe_src:
                 try:
                    from urllib.parse import urlparse
                    parsed = urlparse(iframe_src)
                    request_headers["Referer"] = f"{parsed.scheme}://{parsed.netloc}/"
                    request_headers["Origin"] = f"{parsed.scheme}://{parsed.netloc}"
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
                "headers": request_headers
            })
            count += 1

    except Exception as e:
        print(f"Genel Hata: {e}")
    finally:
        driver.quit() # Tarayıcıyı kapat
        
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print(f"\nİşlem bitti. Veriler kaydedildi.")

if __name__ == "__main__":
    main()
