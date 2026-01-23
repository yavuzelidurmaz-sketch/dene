import requests
import json
import time

# --- TOKEN (MUTLAKA YENİSİNİ ALIP YAPIŞTIR) ---
MANUAL_TOKEN = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJwcm9qZWN0SWQiOiIyZGE3a2Y4amYiLCJpZGVudGl0eSI6ImVuZHVzZXIiLCJhbm9ueW1vdXMiOmZhbHNlLCJ1c2VySWQiOiJlNGMzYWY2Yi05YWQyLTQ3NDYtYTVlNC0yNGQ1ODQyNjZmYzMiLCJjbGFpbXMiOnsiZW1haWwiOiJmYXRtYW51cnJrcmttenoxODZAZ21haWwuY29tIiwiZnVsbE5hbWUiOiJwaXJ0aXN0YW4iLCJwcm9maWxlSWQiOiJVUkNNUURMRExYSkxITFBGQkFOMFpJOVYiLCJwcm9maWxlQXZhdGFyIjoiUCIsImlzS2lkUHJvZmlsZSI6ZmFsc2V9LCJzZXNzaW9uSWQiOiI1NTljN2IwNTlhZmY0MWUwODc2N2Y1YjM2ZDI4MWFjYyIsImlhdCI6MTc2OTE5NDU0MCwiZXhwIjoxNzcxNzg2NTQwfQ.KIzx3nAQWJXM8gc2dDNAOD3iOxoi81xWRnf4sGRDkYmZDKIoHxSsAbE7OqMJ7Paq27GgkUldXM7L9BlIDRrangEYKXQPUIq6l6IcY7xKIPMp3T2srgxdpnKuWoZPCkPNMFpVNO5OCfI78xiGsiRDheGSdEV63ekISdpH6b0W38hZY0WIoVZZKSHw1fyLOPX76B5bg01U9ZgbRG0WuxKzHUnC0g3A2NkBjSR31drQeq0gdf-NAJO7w1qvnI923z_pLOowoyDYVr-eRcl6NRW8NYdhui1eKRtEFp9I4qwtodxFQnz_65e-o5S6C6Nvqgb6oGmrPBMbAAP2Vk-UO5PoCA"

# --- SABİTLER ---
PROJECT_ID = "2da7kf8jf"
PROFILE_ID = "URCMQDLDLXJLHLPFBAN0ZI9V" 

# Hedef Kategoriler (Sunucuya uygun şifreli halleri)
TARGET_SLUGS = ["%2Ffilm", "%2Fdizi", "%2Fprogram", "%2Fkids", "%2Fbelgesel"]

# URL Şablonları
CATEGORY_URL_TEMPLATE = f"https://api.gain.tv/{PROJECT_ID}/CALL/ProfileTitle/getPlaylistsByCategory/{PROFILE_ID}?slug={{}}&__culture=tr-tr"
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
    """Kategoriyi tarar, boş dönerse sebebini yazar"""
    auth_headers = HEADERS.copy()
    auth_headers["Authorization"] = f"Bearer {MANUAL_TOKEN}"
    
    target_url = CATEGORY_URL_TEMPLATE.format(slug)
    readable_slug = slug.replace("%2F", "/")
    print(f"\n🌍 '{readable_slug}' sayfası taranıyor...")
    
    try:
        response = requests.get(target_url, headers=auth_headers)
        
        # Hata Kontrolü 1: HTTP Hatası var mı?
        if response.status_code != 200:
            print(f"   ❌ HTTP Hatası: {response.status_code}")
            return []

        data = response.json()
        
        # Hata Kontrolü 2: Gain 'Success: false' dedi mi?
        if not data.get("Success", True): # Bazen Success alanı hiç gelmeyebilir, o yüzden default True
             print(f"   ⚠️ API Uyarısı: {data.get('Message')}")

        playlists = data.get("playlists", [])
        
        # Eğer liste boşsa sunucu cevabını görelim
        if not playlists:
            print(f"   ⚠️ Liste boş geldi! Sunucu cevabı şuydu:")
            print(json.dumps(data, indent=2, ensure_ascii=False)[:500]) # İlk 500 karakter
            return []

        items_found = []
        print(f"   📦 {len(playlists)} farklı raf bulundu.")

        for playlist in playlists:
            cat_title = playlist.get("title", "Genel")
            items = playlist.get("items", [])
            
            for item in items:
                direct_id = item.get("videoContentId")
                title = item.get("name") or item.get("title") or item.get("originalTitle")
                poster = item.get("logoImageUrl") or item.get("posterImageUrl")
                ctype = item.get("contentType", {}).get("text", "Bilinmiyor")

                if direct_id:
                    items_found.append({
                        "id": direct_id,
                        "title": title,
                        "category": cat_title,
                        "type": ctype,
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
            # Yeni yapıya göre linki alıyoruz
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
        print("⛔ Lütfen Token'ı girmeyi unutma!")
        return

    all_content = []
    processed_ids = set()

    # 1. ADIM: Tüm Kategorileri Gez
    for slug in TARGET_SLUGS:
        slug_items = get_contents_from_slug(slug)
        for item in slug_items:
            if item["id"] not in processed_ids:
                all_content.append(item)
                processed_ids.add(item["id"])
        time.sleep(1)

    total = len(all_content)
    if total == 0:
        print("\n⛔ HİÇBİR İÇERİK BULUNAMADI.")
        print("👉 Lütfen tarayıcıdan YENİ BİR TOKEN alıp kodu güncelle.")
        return

    print(f"\n🚀 TOPLAM {total} BENZERSİZ İÇERİK BULUNDU! Linkler çekiliyor...")

    final_list = []
    for i, content in enumerate(all_content):
        full_data = get_stream_url(content)
        if full_data:
            final_list.append(full_data)
        
        if (i + 1) % 20 == 0:
            print(f"   👍 {i+1} içerik tarandı... ({len(final_list)} başarılı)")
            
        time.sleep(0.05)

    # Dosya adını 'archive' yaptık ki hepsi bir olsun
    filename = "gain_full_archive.json"
    print(f"\n💾 {len(final_list)} içerik '{filename}' dosyasına kaydediliyor...")
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(final_list, f, indent=4, ensure_ascii=False)
    print("🏁 OPERASYON TAMAMLANDI!")

if __name__ == "__main__":
    main()
