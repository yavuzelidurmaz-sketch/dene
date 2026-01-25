import json
import re
import base64
from datetime import datetime
from bs4 import BeautifulSoup
from curl_cffi import requests # <--- SİHİRLİ KÜTÜPHANE

# --- AYARLAR ---
BASE_URL = "https://betparktv252.com"  
OUTPUT_FILE = "data.json"

def get_stream_url(iframe_url):
    """
    curl_cffi kullanarak Cloudflare korumasını geçip token'ı alır.
    """
    if not iframe_url: return None
    if iframe_url.startswith("//"): iframe_url = "https:" + iframe_url
    
    print(f"    -> Analiz: {iframe_url}")
    
    try:
        # Chrome 124 gibi davran (TLS Parmak izi taklidi)
        response = requests.get(
            iframe_url,
            impersonate="chrome124", 
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                "Referer": "https://www.google.com/"
            },
            timeout=10
        )
        
        # Eğer koruma sayfasına düştüysek (Status 403 veya 503)
        if response.status_code in [403, 503]:
            print(f"       [!] Koruma Engeli (Status: {response.status_code})")
            return None

        html_content = response.text
        
        # 1. YÖNTEM: tokenKey Regex
        # Şifrelenmiş tokenKey'i bul
        pattern = r"(var|let|const)?\s*tokenKey\s*=\s*['\"]([^'\"]+)['\"]"
        match = re.search(pattern, html_content)
        
        if match:
            encoded_str = match.group(2)
            try:
                decoded_bytes = base64.b64decode(encoded_str)
                m3u8_url = decoded_bytes.decode('utf-8').strip()
                return m3u8_url
            except: pass

        # 2. YÖNTEM: Direkt Link
        match_direct = re.search(r"['\"](https?://[^'\"]+\.m3u8[^'\"]*)['\"]", html_content)
        if match_direct:
            return match_direct.group(1)

        return None

    except Exception as e:
        print(f"    [!] İstek Hatası: {e}")
        return None

def main():
    print(f"[{datetime.now()}] Tarama Başlıyor (GitHub Mode: curl_cffi)...")
    
    try:
        # Ana sayfayı çek (Burada da curl_cffi kullanalım garanti olsun)
        response = requests.get(BASE_URL, impersonate="chrome124", timeout=15)
        soup = BeautifulSoup(response.text, 'lxml')
        
        data = {"matches": []}
        match_elements = soup.select('.bet-matches a.single-match')
        print(f"Toplam {len(match_elements)} maç bulundu.")

        count = 0
        for match in match_elements:
            if count >= 30: break # GitHub süresi için limit
            
            home = match.get('data-home')
            away = match.get('data-away')
            iframe_src = match.get('data-iframe')
            match_title = f"{home} vs {away}"
            
            # Logolar
            home_logo = match.find('img', class_='homeLogo')['src'] if match.find('img', class_='homeLogo') else ""
            away_logo = match.find('img', class_='awayLogo')['src'] if match.find('img', class_='awayLogo') else ""

            stream_url = None
            if iframe_src:
                stream_url = get_stream_url(iframe_src)
            
            if stream_url:
                print(f" [V] YAKALANDI: {match_title}")
                print(f"     Link: {stream_url[:40]}...")
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
            
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print(f"\nİşlem bitti.")

    except Exception as e:
        print(f"Genel Hata: {e}")

if __name__ == "__main__":
    main()
