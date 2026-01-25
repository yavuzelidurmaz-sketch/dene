import time
import json
import re
import base64
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import undetected_chromedriver as uc # <--- KRİTİK DEĞİŞİKLİK

# --- AYARLAR ---
BASE_URL = "https://betparktv252.com"  
OUTPUT_FILE = "data.json"

def get_driver():
    """Undetected Chrome Driver başlatır (Cloudflare'i geçmek için)"""
    options = uc.ChromeOptions()
    # GitHub Actions veya Sunucuda çalışırken bu ayarlar şart:
    options.add_argument('--headless=new') # Yeni nesil headless mod (Daha az yakalanır)
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--mute-audio')
    options.add_argument('--window-size=1920,1080')
    
    # Driver'ı başlat
    driver = uc.Chrome(options=options, use_subprocess=True)
    return driver

def solve_with_undetected(driver, iframe_url):
    if not iframe_url: return None
    if iframe_url.startswith("//"): iframe_url = "https:" + iframe_url
    
    print(f"    -> Siteye giriliyor (UC Mode): {iframe_url}")
    
    try:
        driver.get(iframe_url)
        # Sayfanın tam yüklenmesi ve JS'in çalışması için bekle
        time.sleep(5) 
        
        page_source = driver.page_source
        
        # --- DEBUG: Sayfa ne durumda? ---
        # Eğer korumaya takılıyorsak başlık 'Just a moment...' veya 'Access denied' olur.
        print(f"       [DEBUG] Sayfa Başlığı: {driver.title}")

        # 1. YÖNTEM: tokenKey Regex (Genişletilmiş)
        # var, let veya const olabilir, boşluklar değişebilir.
        pattern = r"(var|let|const)?\s*tokenKey\s*=\s*['\"]([^'\"]+)['\"]"
        match = re.search(pattern, page_source)
        
        if match:
            encoded_str = match.group(2) # 2. grup şifreli veri
            try:
                decoded_bytes = base64.b64decode(encoded_str)
                m3u8_url = decoded_bytes.decode('utf-8').strip()
                return m3u8_url
            except: pass

        # 2. YÖNTEM: HTML içinde açık .m3u8 var mı?
        match_direct = re.search(r"['\"](https?://[^'\"]+\.m3u8[^'\"]*)['\"]", page_source)
        if match_direct:
            return match_direct.group(1)

        return None

    except Exception as e:
        print(f"    [!] UC Hatası: {e}")
        return None

def main():
    print(f"[{datetime.now()}] Tarama Başlıyor (Undetected-Chromedriver)...")
    
    # Requests ile maç listesini çek (Burası zaten çalışıyor, değiştirmedik)
    headers = {"User-Agent": "Mozilla/5.0", "Referer": "https://www.google.com/"}
    
    driver = None
    try:
        response = requests.get(BASE_URL, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'lxml')
        
        data = {"matches": []}
        match_elements = soup.select('.bet-matches a.single-match')
        print(f"Toplam {len(match_elements)} maç bulundu.")

        # Driver'ı burada başlatıyoruz
        driver = get_driver()

        count = 0
        for match in match_elements:
            if count >= 30: break 
            
            home = match.get('data-home')
            away = match.get('data-away')
            iframe_src = match.get('data-iframe')
            match_title = f"{home} vs {away}"
            
            # Logolar
            home_logo = match.find('img', class_='homeLogo')['src'] if match.find('img', class_='homeLogo') else ""
            away_logo = match.find('img', class_='awayLogo')['src'] if match.find('img', class_='awayLogo') else ""

            stream_url = None
            if iframe_src:
                stream_url = solve_with_undetected(driver, iframe_src)
            
            if stream_url:
                print(f" [V] YAKALANDI: {match_title}")
                print(f"     Link: {stream_url[:50]}...")
            else:
                print(f" [X] Bulunamadı: {match_title}")

            # Referer Ayarı
            req_headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                "Referer": "https://sttc2.kakirikodes.shop/"
            }
            if iframe_src:
                 try:
                    from urllib.parse import urlparse
                    parsed = urlparse(iframe_src)
                    req_headers["Referer"] = f"{parsed.scheme}://{parsed.netloc}/"
                 except: pass

            data["matches"].append({
                "title": match_title,
                "home": home,
                "away": away,
                "iframe_url": iframe_src,
                "stream_url": stream_url,
                "headers": req_headers,
                "home_logo": home_logo,
                "away_logo": away_logo,
                "time": match.get('data-saat'),
                "sport": match.get('data-matchtype')
            })
            count += 1

    except Exception as e:
        print(f"Genel Hata: {e}")
    finally:
        if driver:
            try: driver.quit()
            except: pass
        
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print(f"\nİşlem bitti.")

if __name__ == "__main__":
    main()
