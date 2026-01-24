import requests
from bs4 import BeautifulSoup
import json
import re
import time
from datetime import datetime

# --- AYARLAR ---
BASE_URL = "https://betparktv252.com"  
OUTPUT_FILE = "data.json"

# Bot olduğumuzu gizlemek için
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://www.google.com/",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7"
}

def extract_m3u8(iframe_url):
    """
    Iframe adresine gidip JavaScript değişkenleri içine gizlenmiş .m3u8 linkini bulur.
    """
    if not iframe_url:
        return None
    
    try:
        # Iframe'e giderken Referer olarak ana siteyi gösteriyoruz (Çok Önemli!)
        frame_headers = HEADERS.copy()
        frame_headers["Referer"] = BASE_URL
        
        # Iframe içeriğini çek
        response = requests.get(iframe_url, headers=frame_headers, timeout=10)
        
        if response.status_code == 200:
            content = response.text
            
            # --- YÖNTEM 1: Basit .m3u8 arama ---
            # "http... .m3u8" kalıbını arar
            simple_pattern = r'(https?://[^\s"\']+\.m3u8[^\s"\']*)'
            matches = re.search(simple_pattern, content)
            if matches:
                return matches.group(1).replace('\\/', '/')

            # --- YÖNTEM 2: Oynatıcı değişkenlerini arama (Kakirikodes vb. için) ---
            # source: "..." veya file: "..." şeklindeki yapıları arar
            player_pattern = r'(?:source|file|src)\s*:\s*["\']([^"\']+)["\']'
            matches_js = re.findall(player_pattern, content)
            
            for match in matches_js:
                if ".m3u8" in match:
                    # Bazen link relative (kısmi) olabilir, onu tamamlama mantığı eklenebilir
                    # Ama genelde bu playerlar full link verir.
                    return match.replace('\\/', '/')

            # --- YÖNTEM 3: JSON içindeki url'i arama ---
            # Bazen veri json objesi içindedir
            json_pattern = r'["\'](https?://.*?\.m3u8.*?)["\']'
            matches_json = re.search(json_pattern, content)
            if matches_json:
                return matches_json.group(1).replace('\\/', '/')

    except Exception as e:
        print(f"   [!] M3U8 Hatası ({iframe_url}): {e}")
    
    return None

def main():
    print(f"[{datetime.now()}] Tarama Başlıyor: {BASE_URL}")
    
    try:
        response = requests.get(BASE_URL, headers=HEADERS, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'lxml')
        
        # JSON İskeleti
        data = {
            "meta": {
                "updated_at": str(datetime.now()),
                "source": BASE_URL,
                "note": "Stream linklerini oynatırken Header göndermeyi unutmayın."
            },
            "channels": [],
            "matches": []
        }

        # --- KANALLARI ÇEK ---
        print("--- Kanallar Taranıyor ---")
        channel_elements = soup.select('.channel-list .single-channel')
        for ch in channel_elements:
            name = ch.get('data-name')
            stream_slug = ch.get('data-stream')
            
            img_tag = ch.find('img')
            img_url = ""
            if img_tag:
                src = img_tag.get('src', '')
                if src.startswith('//'):
                    img_url = "https:" + src
                elif src.startswith('/'):
                    img_url = BASE_URL + src
                else:
                    img_url = src

            # Kanalın kendi sayfasını bulup oradan m3u8 çekmek gerekebilir
            # Şimdilik sadece ana bilgileri alıyoruz
            data["channels"].append({
                "name": name,
                "slug": stream_slug,
                "logo": img_url,
                "url": f"{BASE_URL}/kanal/{stream_slug}"
            })

        # --- MAÇLARI ÇEK ---
        print("--- Maçlar ve M3U8 Linkleri Taranıyor ---")
        match_elements = soup.select('.bet-matches a.single-match')
        
        for match in match_elements:
            home = match.get('data-home')
            away = match.get('data-away')
            match_title = f"{home} vs {away}"
            
            iframe_src = match.get('data-iframe')
            
            # Logolar
            home_logo_tag = match.find('img', class_='homeLogo')
            home_logo = home_logo_tag['src'] if home_logo_tag else ""
            
            away_logo_tag = match.find('img', class_='awayLogo')
            away_logo = away_logo_tag['src'] if away_logo_tag else ""

            print(f" > İşleniyor: {match_title}...")

            # Canlı yayın linkini avla
            real_stream_url = extract_m3u8(iframe_src)
            
            # Referer belirleme (Video oynatıcı bu referer olmadan çalışmaz)
            # Genelde iframe'in ana domaini referer olarak istenir
            referer_header = "https://sttc2.kakirikodes.shop/"
            if iframe_src:
                try:
                    # Iframe domainini parse et
                    from urllib.parse import urlparse
                    parsed_uri = urlparse(iframe_src)
                    referer_header = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
                except:
                    pass

            match_data = {
                "title": match_title,
                "home": home,
                "away": away,
                "time": match.get('data-saat'),
                "sport": match.get('data-matchtype'),
                "home_logo": home_logo,
                "away_logo": away_logo,
                "iframe_url": iframe_src,
                "stream_url": real_stream_url, # <-- BURASI ARTIK DOLU OLMALI
                "headers": {
                    "User-Agent": HEADERS["User-Agent"],
                    "Referer": referer_header,
                    "Origin": referer_header.rstrip('/')
                }
            }
            
            data["matches"].append(match_data)
            
            # Rate limit yememek için minik bekleme
            time.sleep(0.2)

        # JSON DOSYASINA YAZ
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
            
        print(f"\nBaşarılı! 'data.json' dosyasına yazıldı.")

    except Exception as e:
        print(f"KRİTİK HATA: {e}")

if __name__ == "__main__":
    main()
