import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime

# Hedef Site
BASE_URL = "https://betparktv252.com" 
OUTPUT_FILE = "data.json"

# Headerlar (Referer çok önemli, yoksa yayın açılmaz)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Referer": "https://www.google.com/"
}

def extract_m3u8_from_iframe(iframe_url):
    """
    Iframe adresine gidip kaynak kodun içinden .m3u8 linkini regex ile arar.
    """
    if not iframe_url:
        return None
        
    try:
        # Iframe'e istek atarken Referer olarak ana siteyi gösteriyoruz
        iframe_headers = HEADERS.copy()
        iframe_headers["Referer"] = BASE_URL
        
        response = requests.get(iframe_url, headers=iframe_headers, timeout=10)
        
        if response.status_code == 200:
            # Regex ile .m3u8 ile biten linkleri arıyoruz (genelde "source": "..." içinde olur)
            # Bu regex http veya https ile başlayan ve .m3u8 ile biten stringi yakalar
            m3u8_pattern = r'(https?://[^\s"\']+\.m3u8[^\s"\']*)'
            matches = re.search(m3u8_pattern, response.text)
            
            if matches:
                return matches.group(1)
            else:
                # Bazen m3u8 base64 veya farklı bir değişken içinde olabilir,
                # bu basit regex çoğu standart player (Clappr, JWPlayer) için çalışır.
                return None
    except Exception as e:
        print(f"M3U8 çekme hatası: {e}")
        return None

def scrape_data():
    print(f"[{datetime.now()}] Site taranıyor: {BASE_URL}")
    
    try:
        response = requests.get(BASE_URL, headers=HEADERS, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'lxml')
        
        data_output = {
            "last_updated": str(datetime.now()),
            "channels": [], # Kanal mantığı maçlarla aynıysa buraya da uygulanabilir
            "matches": []
        }

        # --- MAÇ LİSTESİNİ VE M3U8 LİNKLERİNİ ÇEKME ---
        match_elements = soup.select('.bet-matches a.single-match')
        
        print(f"{len(match_elements)} adet maç bulundu, m3u8 linkleri taranıyor...")

        for match in match_elements:
            home_team = match.get('data-home')
            away_team = match.get('data-away')
            match_name = f"{home_team} vs {away_team}"
            
            # Iframe URL'ini al
            iframe_src = match.get('data-iframe')
            
            # ---> KRİTİK NOKTA: Iframe'e gidip m3u8'i alıyoruz <---
            # Token varsa URL'e eklememiz gerekebilir, HTML'de data-token varsa onu da alabilirsin.
            # Senin HTML örneğinde iframe url'i token içeriyor gibi görünüyordu.
            
            direct_stream_url = extract_m3u8_from_iframe(iframe_src)
            
            # Görseller
            home_img = match.find('img', class_='homeLogo')
            home_logo = home_img['src'] if home_img else ""
            
            away_img = match.find('img', class_='awayLogo')
            away_logo = away_img['src'] if away_img else ""

            # Sadece yayını bulunanları listeye eklemek istersen if direct_stream_url: kullanabilirsin.
            data_output["matches"].append({
                "name": match_name,
                "home_team": home_team,
                "away_team": away_team,
                "home_logo": home_logo,
                "away_logo": away_logo,
                "time": match.get('data-saat'),
                "sport": match.get('data-matchtype'),
                "iframe_url": iframe_src,     # Yedek olarak kalsın
                "stream_url": direct_stream_url, # İŞTE BU SENİN M3U8 LİNKİN
                "headers": { # Oynatıcıya (ExoPlayer) bu headerları göndermen gerekebilir
                    "Referer": "https://sttc2.kakirikodes.shop/", 
                    "User-Agent": HEADERS["User-Agent"]
                }
            })
            
            print(f"Çekildi: {match_name} -> {direct_stream_url if direct_stream_url else 'LINK YOK'}")

        # JSON Kaydetme
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(data_output, f, indent=4, ensure_ascii=False)
            
        print("İşlem tamamlandı. data.json kontrol et.")

    except Exception as e:
        print(f"Genel Hata: {e}")

if __name__ == "__main__":
    scrape_data()
