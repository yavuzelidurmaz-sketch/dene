import requests
import json
import time

# --- TOKEN (YENİSİNİ ALIP YAPIŞTIR) ---
MANUAL_TOKEN = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJwcm9qZWN0SWQiOiIyZGE3a2Y4amYiLCJpZGVudGl0eSI6ImVuZHVzZXIiLCJhbm9ueW1vdXMiOmZhbHNlLCJ1c2VySWQiOiJlNGMzYWY2Yi05YWQyLTQ3NDYtYTVlNC0yNGQ1ODQyNjZmYzMiLCJjbGFpbXMiOnsiZW1haWwiOiJmYXRtYW51cnJrcmttenoxODZAZ21haWwuY29tIiwiZnVsbE5hbWUiOiJwaXJ0aXN0YW4iLCJwcm9maWxlSWQiOiJVUkNNUURMRExYSkxITFBGQkFOMFpJOVYiLCJwcm9maWxlQXZhdGFyIjoiUCIsImlzS2lkUHJvZmlsZSI6ZmFsc2V9LCJzZXNzaW9uSWQiOiJkMzdhMjlkMTMwOGE0NmRmOTA1NzQzZjg4ODdjZDliNiIsImlhdCI6MTc2OTE4NjUzMywiZXhwIjoxNzcxNzc4NTMzfQ.ci3CbqGQHVgUFIPs2PH_tR7CUTzN4HoKu3LY3zpFQztXlqZVgo_kXqp9A-6Pdn0G_R_BDtNC-sWS9eRzgka0KzlP228BGmZ87N_0wpxg1riHierd5LKIMZFNOJw-LkdQ3sFTWhGvD0zJm-lYYunh2gxtoWJXGVyuQYQSlt4xrPEMneUDbw-d0D2nVeJu_WVfkOPMFEC6bEmuFVIHgD6usMkd2_e9sr7mkt7GXwVBGuFJb9dK1p1nWb-KKXN7oIvf-eaxCbtAJ27Lja_NI-YlA8QjvwVsqnmf7qNuJpjJtorPSDvUcR6gp8oiZmzCw8zwJXoB79Xkmxlr0jnxDrTtIQ"

# --- SABİTLER ---
PROJECT_ID = "2da7kf8jf"
PROFILE_ID = "URCMQDLDLXJLHLPFBAN0ZI9V" 

# Çekeceğimiz Sayfaların Listesi (Sluglar)
# Buraya istediğin başka kategori varsa ekleyebilirsin (örn: /belgesel)
TARGET_SLUGS = ["/film", "/dizi", "/program", "/kids", "/belgesel"]

# API Şablonları
# DİKKAT: &pageSize=500 ekleyerek tüm listeyi zorluyoruz!
CATEGORY_URL_TEMPLATE = f"https://api.gain.tv/{PROJECT_ID}/CALL/ProfileTitle/getPlaylistsByCategory/{PROFILE_ID}?slug={{}}&__culture=tr-tr&pageSize=500"
PLAYBACK_URL_TEMPLATE = f"https://api.gain.tv/{PROJECT_ID}/CALL/ProfileTitle/getPlaybackInfo/{PROFILE_ID}/"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Content-Type": "application/json",
    "Accept": "application/json",
    "x-gain-platform": "web",
    "Origin": "https://www.gain.tv",
    "Referer": "https://www.gain.tv/"
}

def get_movies_from_slug(slug):
    """Verilen sayfa (Film, Dizi vb.) içindeki içerikleri çeker"""
    auth_headers = HEADERS.copy()
    auth_headers["Authorization"] = f"Bearer {MANUAL_TOKEN}"
    
    # Slug'ı URL'ye yerleştir (örn: /film)
    target_url = CATEGORY_URL_TEMPLATE.format(slug)
    print(f"\n🌍 '{slug}' sayfası taranıyor...")
    
    try:
        response = requests.get(target_url, headers=auth_headers)
        data = response.json()
        playlists = data.get("playlists", [])
        
        items_found = []
        
        print(f"   📦 {len(playlists)} farklı raf (kategori) bulundu.")

        for playlist in playlists:
            cat_title = playlist.get("title", "Genel")
            items = playlist.get("items", [])
            
            # Eğer raf boşsa geç
            if not items:
                continue

            # print(f"      📂 {cat_title}: {len(items)} içerik var.")
            
            for item in items:
                direct_id = item.get("videoContentId")
                title = item.get("name") or item.get("title") or item.get("originalTitle")
                poster = item.get("logoImageUrl") or item.get("posterImageUrl")
                
                # Türü belirle (Film mi Dizi mi?)
                ctype = item.get("contentType", {}).get("text", "Bilinmiyor")

                if direct_id:
                    items_found.append({
                        "id": direct_id,
                        "title": title,
                        "category": cat_title,
                        "type": ctype, # Film, Dizi, Program vs.
                        "poster": poster,
                        "source_slug": slug # Hangi sayfadan geldiği
                    })
        
        print(f"   ✅ '{slug}' içinden {len(items_found)} içerik toplandı.")
        return items_found

    except Exception as e:
        print(f"🔥 Hata ({slug}): {e}")
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
            current_content = data.get("currentVideoContent", {})
            playback_url = current_content.get("playbackUrl")
            
            if playback_url:
                content["stream_url"] = playback_url
                content["license_url"] = current_content.get("licenseUrl")
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

    # 1. ADIM: Tüm Sayfaları Gez (Film, Dizi, Kids...)
    for slug in TARGET_SLUGS:
        slug_items = get_movies_from_slug(slug)
        
        # Tekrar edenleri engelle (Aynı film hem 'Aksiyon' hem 'Öne Çıkanlar'da olabilir)
        for item in slug_items:
            if item["id"] not in processed_ids:
                all_content.append(item)
                processed_ids.add(item["id"])
        
        time.sleep(1) # Nezaketen bekleme

    total = len(all_content)
    if total == 0:
        print("\n⚠️ Hiçbir içerik bulunamadı. Token'ı kontrol et.")
        return

    print(f"\n🚀 TOPLAM {total} BENZERSİZ İÇERİK BULUNDU! Linkler çekiliyor...")

    # 2. ADIM: Hepsine Link Al
    final_list = []
    
    for i, content in enumerate(all_content):
        full_data = get_stream_url(content)
        
        if full_data:
            final_list.append(full_data)
            # Logu biraz sadeleştirelim
            # print(f"✅ [{i+1}/{total}] {content['type']}: {content['title']}")
        else:
            print(f"❌ [{i+1}/{total}] Link Yok: {content['title']}")
        
        # Her 20 içerikte bir bilgi ver
        if (i + 1) % 20 == 0:
            print(f"   👍 {i+1} içerik tamamlandı... ({len(final_list)} başarılı)")
            
        time.sleep(0.05) # Hızlı mod

    # 3. ADIM: Kaydet
    filename = "gain_full_archive.json"
    print(f"\n💾 {len(final_list)} içerik '{filename}' dosyasına kaydediliyor...")
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(final_list, f, indent=4, ensure_ascii=False)
    print("🏁 OPERASYON TAMAMLANDI!")

if __name__ == "__main__":
    main()
