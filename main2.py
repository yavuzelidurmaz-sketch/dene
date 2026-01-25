import requests
from bs4 import BeautifulSoup
import json
import re
import base64
from datetime import datetime

# --- AYARLAR ---
BASE_URL = "https://betparktv252.com"
OUTPUT_FILE = "data.json"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://www.google.com/"
}

def decode_token(iframe_url):
    """
    Iframe HTML'ini çeker, içindeki gizli Base64 'tokenKey'i bulur ve çözer.
    Selenium gerektirmez, çok hızlıdır.
    """
    try:
        # Eğer link // ile başlıyorsa düzelt
        if iframe_url.startswith("//"):
            iframe_url = "https:" + iframe_url

        print(f"    -> Kaynak taranıyor: {iframe_url}")
        
        # Iframe içeriğini indir
        response = requests.get(iframe_url, headers=HEADERS, timeout=10)
        html_content = response.text
        
        # 1. YÖNTEM: 'tokenKey' değişkenini Regex ile yakala
        # Kodda: var tokenKey = 'aHR0cHM...'; şeklinde duruyor.
        pattern = r"var\s+tokenKey\s*=\s*['\"]([^'\"]+)['\"]"
        match = re.search(pattern, html_content)
        
        if match:
            encoded_str = match.group(1)
            # Base64 decode işlemi
            decoded_bytes = base64.b64decode(encoded_str)
            m3u8_url = decoded_bytes.decode('utf-8')
            
            # Bazen linkin başında/sonunda boşluk olabilir, temizle
            return m3u8_url.strip()
        
        # 2. YÖNTEM: Eğer tokenKey yoksa, direkt .m3u8 linki var mı diye bak (Yedek)
        direct_m3u8 = re.search(r"['\"](https?://.*?\.m3u8.*?)['\"]", html_content)
        if direct_m3u8:
            return direct_m3u8.group(1)

        return None

    except Exception as e:
        print(f"    [!] Decode Hatası: {e}")
        return None

def main():
    print(f"[{datetime.now()}] Hızlı Tarama Başlıyor (Static Analysis Mode)...")
    
    try:
        response = requests.get(BASE_URL, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(response.text, 'lxml')
        
        data = {
            "meta": {"updated_at": str(datetime.now()), "source": BASE_URL},
            "matches": []
        }

        match_elements = soup.select('.bet-matches a.single-match')
        print(f"Toplam {len(match_elements)} maç bulundu.")

        count = 0
        for match in match_elements:
            # Test için limit (İstersen kaldır)
            if count >= 50: break 
            
            home = match.get('data-home')
            away = match.get('data-away')
            iframe_src = match.get('data-iframe')
            match_title = f"{home} vs {away}"
            
            # Logolar
            home_logo = match.find('img', class_='homeLogo')['src'] if match.find('img', class_='homeLogo') else ""
            away_logo = match.find('img', class_='awayLogo')['src'] if match.find('img', class_='awayLogo') else ""

            stream_url = None
            if iframe_src:
                # ARTIK SELENIUM YOK, DIREKT DECODE VAR
                stream_url = decode_token(iframe_src)
            
            if stream_url:
                print(f" [V] ÇÖZÜLDÜ: {match_title}")
                print(f"     Link: {stream_url}")
            else:
                print(f" [X] Bulunamadı: {match_title}")

            # Referer Header'ı oluştur (Player'ın çalışması için gerekli olabilir)
            player_referer = "https://sttc2.kakirikodes.shop/"
            if iframe_src:
                 try:
                    from urllib.parse import urlparse
                    parsed = urlparse(iframe_src)
                    player_referer = f"{parsed.scheme}://{parsed.netloc}/"
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
                "headers": {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                    "Referer": player_referer
                }
            })
            count += 1

        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
            
        print(f"\nİşlem bitti. Veriler kaydedildi.")

    except Exception as e:
        print(f"Genel Hata: {e}")

if __name__ == "__main__":
    main()
