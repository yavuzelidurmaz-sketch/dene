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

# --- JS UNPACKER SINIFI (Senin attığın Kotlin kodunun Python hali) ---
class JsUnpacker:
    def __init__(self, packedJS):
        self.packedJS = packedJS

    def detect(self):
        """JavaScript'in P.A.C.K.E.R. formatında olup olmadığını kontrol eder."""
        if not self.packedJS: return False
        js = self.packedJS.replace(" ", "")
        return bool(re.search(r"eval\(function\(p,a,c,k,e,[rd]", js))

    def unpack(self):
        """Şifreli JS kodunu çözer."""
        if not self.packedJS: return None
        
        try:
            # P.A.C.K.E.R. Regex deseni (Kotlin kodundaki mantık)
            pattern = r"}\s*\('(.*)',\s*(.*?),\s*(\d+),\s*'(.*?)'\.split\('\|'\)"
            match = re.search(pattern, self.packedJS, re.DOTALL)
            
            if match and len(match.groups()) == 4:
                payload = match.group(1).replace("\\'", "'")
                radix = int(match.group(2))
                count = int(match.group(3))
                keywords = match.group(4).split('|')

                if len(keywords) != count:
                    return None # Hatalı paket

                # Base kod çözücü
                def unbase(val, base):
                    if 2 <= base <= 36:
                        return int(val, base)
                    else:
                        # Base62+ desteği (Kotlin kodundaki Unbase mantığı)
                        ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
                        ret = 0
                        for i, char in enumerate(val[::-1]):
                            ret += ALPHABET.index(char) * (base ** i)
                        return ret

                def lookup(match):
                    word = match.group(0)
                    index = unbase(word, radix)
                    if 0 <= index < len(keywords):
                        return keywords[index] if keywords[index] else word
                    return word

                # Payload içindeki şifreli kelimeleri değiştir
                # \b kelime sınırı demektir, alfanümerik kelimeleri bulur
                decoded = re.sub(r'\b\w+\b', lookup, payload)
                return decoded

        except Exception as e:
            print(f"Unpack Hatası: {e}")
        
        return None

# --- TARAYICI AYARLARI ---
def get_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless") 
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def extract_stream_url(driver, iframe_url):
    """
    Iframe'e gider, şifreli JS'i bulur ve çözer.
    """
    if not iframe_url: return None
    
    print(f"    -> Analiz ediliyor: {iframe_url}")
    try:
        driver.get(iframe_url)
        time.sleep(2) # JS yüklenmesi için bekle
        
        page_source = driver.page_source
        
        # 1. YÖNTEM: Direkt açıkta olan m3u8 var mı?
        simple_m3u8 = re.search(r'(https?://[^\s"\']+\.m3u8[^\s"\']*)', page_source)
        if simple_m3u8:
            return simple_m3u8.group(1).replace('\\/', '/')

        # 2. YÖNTEM: P.A.C.K.E.R (eval(function(p,a,c,k,e,d)) koruması var mı?
        # Sayfa kaynağındaki script etiketlerini tara
        scripts = re.findall(r'<script.*?>(.*?)</script>', page_source, re.DOTALL)
        
        for script_content in scripts:
            unpacker = JsUnpacker(script_content)
            if unpacker.detect():
                print("    [!] Şifreli kod bulundu, çözülüyor...")
                decoded_js = unpacker.unpack()
                
                if decoded_js:
                    # Çözülen kodun içinde m3u8 ara
                    hidden_m3u8 = re.search(r'(https?://[^\s"\']+\.m3u8[^\s"\']*)', decoded_js)
                    if hidden_m3u8:
                        return hidden_m3u8.group(1).replace('\\/', '/')

    except Exception as e:
        print(f"    [!] Hata: {e}")
        
    return None

def main():
    print(f"[{datetime.now()}] Tarama Başlıyor (Selenium + JsUnpacker)...")
    
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        # Ana sayfayı çek
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
            # Test için limit (Github'a yüklerken bu limiti kaldırabilirsin)
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
                stream_url = extract_stream_url(driver, iframe_src)
            
            if stream_url:
                print(f" [V] Link Çözüldü: {match_title}")
            else:
                print(f" [X] Link Bulunamadı: {match_title}")

            # Referer, iframe'in ana domaini olmalı
            referer_header = "https://sttc2.kakirikodes.shop/"
            if iframe_src and "http" in iframe_src:
                from urllib.parse import urlparse
                parsed = urlparse(iframe_src)
                referer_header = f"{parsed.scheme}://{parsed.netloc}/"

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
        except:
            pass

if __name__ == "__main__":
    main()
