import requests
from bs4 import BeautifulSoup
import json
import re
import time
from datetime import datetime

# --- AYARLAR ---
BASE_URL = "https://betparktv252.com"  # Site adresi değişirse buradan güncelle
OUTPUT_FILE = "data.json"

# Bot olduğumuzu gizlemek ve yayını açabilmek için gerekli başlıklar
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Referer": "https://www.google.com/"
}

def extract_m3u8(iframe_url):
    """
    Iframe adresine gidip gizli .m3u8 linkini bulmaya çalışır.
    """
    if not iframe_url:
        return None
    
    try:
        # Iframe'e giderken Referer olarak ana siteyi gösteriyoruz
        frame_headers = HEADERS.copy()
        frame_headers["Referer"] = BASE_URL
        
        # Iframe içeriğini çek
        response = requests.get(iframe_url, headers=frame_headers, timeout=10)
        
        if response.status_code == 200:
            content = response.text
            
            # 1. Yöntem: Standart .m3u8 arama
            # (http veya https ile başlayan ve .m3u8 ile biten stringleri bul)
            m3u8_pattern = r'(https?://[^\s"\']+\.m3u8[^\s"\']*)'
            matches = re.search(m3u8_pattern, content)
            
            if matches:
                # Linkte escape karakterleri (\/) varsa düzelt
                clean_link = matches.group(1).replace('\\/', '/')
                return clean_link
            
            # 2. Yöntem: Eğer m3u8 yoksa, belki başka bir .php veya tokenli link vardır
            # Burası sitenin yapısına göre özelleştirilebilir.
            
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
                "source": BASE_URL
            },
            "channels": [],
            "matches": []
        }

        # --- KANALLARI ÇEK ---
        # (Slider kısmındaki sabit kanallar)
        print("--- Kanallar Taranıyor ---")
        channel_elements = soup.select('.channel-list .single-channel')
        for ch in channel_elements:
            name = ch.get('data-name')
            stream_slug = ch.get('data-stream')
            
            # Resim linkini düzelt
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

            data["channels"].append({
                "name": name,
                "slug": stream_slug,
                "logo": img_url,
                "url": f"{BASE_URL}/kanal/{stream_slug}" # Kanalın sayfa linki
            })

        # --- MAÇLARI ÇEK ---
        print("--- Maçlar ve M3U8 Linkleri Taranıyor ---")
        match_elements = soup.select('.bet-matches a.single-match')
        
        for match in match_elements:
            home = match.get('data-home')
            away = match.get('data-away')
            match_title = f"{home} vs {away}"
            
            iframe_src = match.get('data-iframe')
            match_time = match.get('data-saat')
            sport_type = match.get('data-matchtype')
            
            # Logolar
            home_logo = match.find('img', class_='homeLogo')['src']
            away_logo = match.find('img', class_='awayLogo')['src']

            print(f" > İşleniyor: {match_title}...")

            # Canlı yayın linkini avla
            real_stream_url = extract_m3u8(iframe_src)
            
            match_data = {
                "title": match_title,
                "home": home,
                "away": away,
                "time": match_time,
                "sport": sport_type,
                "home_logo": home_logo,
                "away_logo": away_logo,
                "iframe_url": iframe_src, # Yedek olarak dursun
                "stream_url": real_stream_url, # ASIL LİNK (varsa)
                "headers": { # Oynatıcıya gönderilecek headerlar
                    "User-Agent": HEADERS["User-Agent"],
                    "Referer": "https://sttc2.kakirikodes.shop/" # Genelde iframe domaini referer istenir
                }
            }
            
            data["matches"].append(match_data)
            
            # Sunucuyu yormamak için çok kısa bekle
            time.sleep(0.1)

        # JSON DOSYASINA YAZ
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
            
        print(f"\nBaşarılı! Toplam {len(data['matches'])} maç bulundu. 'data.json' dosyasına yazıldı.")

    except Exception as e:
        print(f"KRİTİK HATA: {e}")

if __name__ == "__main__":
    main()
