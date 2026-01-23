import requests
import json
import time

# --- TOKEN (YENİSİNİ ALIP YAPIŞTIR) ---
MANUAL_TOKEN = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJwcm9qZWN0SWQiOiIyZGE3a2Y4amYiLCJpZGVudGl0eSI6ImVuZHVzZXIiLCJhbm9ueW1vdXMiOmZhbHNlLCJ1c2VySWQiOiJlNGMzYWY2Yi05YWQyLTQ3NDYtYTVlNC0yNGQ1ODQyNjZmYzMiLCJjbGFpbXMiOnsiZW1haWwiOiJmYXRtYW51cnJrcmttenoxODZAZ21haWwuY29tIiwiZnVsbE5hbWUiOiJwaXJ0aXN0YW4iLCJwcm9maWxlSWQiOiJVUkNNUURMRExYSkxITFBGQkFOMFpJOVYiLCJwcm9maWxlQXZhdGFyIjoiUCIsImlzS2lkUHJvZmlsZSI6ZmFsc2V9LCJzZXNzaW9uSWQiOiJkMzdhMjlkMTMwOGE0NmRmOTA1NzQzZjg4ODdjZDliNiIsImlhdCI6MTc2OTE4NjUzMywiZXhwIjoxNzcxNzc4NTMzfQ.ci3CbqGQHVgUFIPs2PH_tR7CUTzN4HoKu3LY3zpFQztXlqZVgo_kXqp9A-6Pdn0G_R_BDtNC-sWS9eRzgka0KzlP228BGmZ87N_0wpxg1riHierd5LKIMZFNOJw-LkdQ3sFTWhGvD0zJm-lYYunh2gxtoWJXGVyuQYQSlt4xrPEMneUDbw-d0D2nVeJu_WVfkOPMFEC6bEmuFVIHgD6usMkd2_e9sr7mkt7GXwVBGuFJb9dK1p1nWb-KKXN7oIvf-eaxCbtAJ27Lja_NI-YlA8QjvwVsqnmf7qNuJpjJtorPSDvUcR6gp8oiZmzCw8zwJXoB79Xkmxlr0jnxDrTtIQ"

# --- SABİTLER ---
PROJECT_ID = "2da7kf8jf"
PROFILE_ID = "URCMQDLDLXJLHLPFBAN0ZI9V" 

# DÜZELTME: Başlarına %2F koyduk (Sunucu bunu istiyor)
TARGET_SLUGS = ["%2Ffilm", "%2Fdizi", "%2Fprogram", "%2Fkids", "%2Fbelgesel"]

# Kategori URL Şablonu (pageSize'ı kaldırdık, standart istek atıyoruz)
CATEGORY_URL_TEMPLATE = f"https://api.gain.tv/{PROJECT_ID}/CALL/ProfileTitle/getPlaylistsByCategory/{PROFILE_ID}?slug={{}}&__culture=tr-tr"

# Playback URL
PLAYBACK_URL_TEMPLATE = f"https://api.gain.tv/{PROJECT_ID}/CALL/ProfileTitle/getPlaybackInfo/{PROFILE_ID}/"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Content-Type": "application/json",
    "Accept": "application/json",
    "x-gain-platform": "web",
    "Origin": "https://www.gain.tv",
    "Referer": "https://www.gain.tv/"
}

def get_contents_from_slug(slug):
    """Verilen sayfadaki (Film, Dizi vb.) içerikleri çeker"""
    auth_headers = HEADERS.copy()
    auth_headers["Authorization"] = f"Bearer {MANUAL_TOKEN}"
    
    # URL'yi oluştur
    target_url = CATEGORY_URL_TEMPLATE.format(slug)
    # Logda okunaklı olsun diye %2F'yi siliyoruz
    readable_slug = slug.replace("%2F", "/")
    print(f"\n🌍 '{readable_slug}' sayfası taranıyor...")
    
    try:
        response = requests.get(target_url, headers=auth_headers)
        data = response.json()
        playlists = data.get("playlists", [])
        
        items_found = []
        
        print(f"   📦 {len(playlists)} farklı raf bulundu.")

        for playlist in playlists:
            cat_title = playlist.get("title", "Genel")
            items = playlist.get("items", [])
            
            for item in items:
                direct_id = item.get("videoContentId")
                title = item.get("name") or item.get("title") or item.get("originalTitle")
                poster = item.get("logoImageUrl") or item.get("posterImageUrl")
                
                # Türü (Dizi/Film)
                content_type = item.get("contentType", {}).get("text", "Bilinmiyor")

                if direct_id:
                    items_found.append({
                        "id": direct_id,
                        "title": title,
                        "category": cat_title,
                        "type": content_type,
                        "poster": poster,
                        "source": readable_slug
                    })
        
        print(f"   ✅ '{readable_slug}' içinden {len(items_found)} içerik alındı.")
        return items_found

    except Exception as e:
        print(f"🔥 Hata ({readable_slug}): {e}")
        return []

def get_stream_url(content):
    """Yayın linkini çeker"""
    params = {
        "videoContentId": content["id"], 
        "packageType": "Dash",
        "__culture": "tr-tr"
    }
    auth_headers = HEADERS.copy()
    auth_headers["Authorization"] = f"Bearer {MANUAL_TOKEN}"
    
    try:
        response = requests.get(PLAYBACK_URL_TEMPLATE, headers=auth_headers, params=params)
        if response.status_code == 200:
            data = response.json()
            current = data.get("currentVideoContent", {})
            playback_url = current.get("playbackUrl")
            
            if playback_url:
                content["stream_url"] = playback_url
                content["license_url"] = current.get("licenseUrl")
                return content
    except:
        pass
    return None

def main():
    if "BURAYA" in MANUAL_TOKEN:
        print("⛔ Token girmeyi unutma!")
        return

    all_content = []
    processed_ids = set()

    # 1. ADIM: Tüm Sayfaları Gez
    for slug in TARGET_SLUGS:
        slug_items = get_contents_from_slug(slug)
        
        for item in slug_items:
            # Tekrar edenleri (aynı film farklı kategoride olabilir) engelle
            if item["id"] not in processed_ids:
                all_content.append(item)
                processed_ids.add(item["id"])
        
        time.sleep(1) 

    total = len(all_content)
    if total == 0:
        print("\n⚠️ Hiçbir içerik bulunamadı. Token süresi dolmuş olabilir.")
        # Boş dosya oluştur
        with open("gain_full_archive.json", "w", encoding="utf-8") as f:
            f.write("[]")
        return

    print(f"\n🚀 TOPLAM {total} BENZERSİZ İÇERİK BULUNDU! Linkler çekiliyor...")

    final_list = []
    for i, content in enumerate(all_content):
        full_data = get_stream_url(content)
        
        if full_data:
            final_list.append(full_data)
        
        if (i + 1) % 10 == 0:
            print(f"   👍 {i+1} içerik tarandı... ({len(final_list)} başarılı)")
            
        time.sleep(0.05)

    # 3. ADIM: Kaydet
    filename = "gain_full_archive.json"
    print(f"\n💾 {len(final_list)} içerik '{filename}' dosyasına kaydediliyor...")
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(final_list, f, indent=4, ensure_ascii=False)
    print("🏁 OPERASYON TAMAMLANDI!")

if __name__ == "__main__":
    main()
