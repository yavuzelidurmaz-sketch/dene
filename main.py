import requests
import json
import time

# --- YENİ TOKENI BURAYA YAPIŞTIR (Token süresi dolunca 403 hatası alırsın) ---
MANUAL_TOKEN = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJwcm9qZWN0SWQiOiIyZGE3a2Y4amYiLCJpZGVudGl0eSI6ImVuZHVzZXIiLCJhbm9ueW1vdXMiOmZhbHNlLCJ1c2VySWQiOiJlNGMzYWY2Yi05YWQyLTQ3NDYtYTVlNC0yNGQ1ODQyNjZmYzMiLCJjbGFpbXMiOnsiZW1haWwiOiJmYXRtYW51cnJrcmttenoxODZAZ21haWwuY29tIiwiZnVsbE5hbWUiOiJwaXJ0aXN0YW4iLCJwcm9maWxlSWQiOiJVUkNNUURMRExYSkxITFBGQkFOMFpJOVYiLCJwcm9maWxlQXZhdGFyIjoiUCIsImlzS2lkUHJvZmlsZSI6ZmFsc2V9LCJzZXNzaW9uSWQiOiIyOTVhNWM4N2RlYTk0Y2FhOTcyOTZlYzY2OWNiYjBmZCIsImlhdCI6MTc2OTE5NjA1MywiZXhwIjoxNzcxNzg4MDUzfQ.yKLLAEotOL9BWz3oFDsVyos7zcfMxnPFgRJpmsn50B6IbBe3SMgeZo02X0ghZdz93xB5kUETdBlDRmt1QHzAJ_7z_4qOLukh-z2pnPeaImVT-fRZGjK4Ez--GjRS_sOdnXgNVIdzYkiEsqyVabi8wL46K0C-1oo5B9bJ7sjAxaadAAs4rFKQ-bKx-c1rKgOso31XArEn3zIo0bhjhuvuOECNwvVbDu5Dg2LcgqkbDRA8LQ37iDudkaAwF9jVnxTNHLzmrxMf6KwftzgdmkIoizrsThFw1vVJWXTdaXNXlS5ZbOvC-iQ3UH3gAk2Yjv6gDxk0YgvRRYsDE3vwNKrbeQ"

# --- PROJE VE PROFİL ID'LERİ ---
PROJECT_ID = "2da7kf8jf"
ADULT_PROFILE_ID = "URCMQDLDLXJLHLPFBAN0ZI9V" # Yetişkin (Film/Dizi/Program)
KIDS_PROFILE_ID = "KIBPFC0Q9Z08Q1UMMJTO61NI"  # Çocuk (Kids - Senin verdiğin ID)

TARGETS = [
    {
        "name": "Film",
        "profile_id": ADULT_PROFILE_ID,
        "url_param": "slug=%2Ffilm"
    },
    {
        "name": "Dizi",
        "profile_id": ADULT_PROFILE_ID,
        "url_param": "slug=%2Fdizi"
    },
    {
        "name": "Program",
        "profile_id": ADULT_PROFILE_ID,
        "url_param": "slug=%2Fprogram"
    },
    {
        "name": "Kids",
        "profile_id": KIDS_PROFILE_ID,
        "url_param": "categoryName=MAIN-PAGE" # Kids için özel parametre
    }
]

BASE_API = f"https://api.gain.tv/{PROJECT_ID}/CALL/ProfileTitle"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Content-Type": "application/json",
    "Accept": "application/json",
    "x-gain-platform": "web",
    "Origin": "https://www.gain.tv",
    "Referer": "https://www.gain.tv/"
}

def get_contents(target):
    profile_id = target["profile_id"]
    param = target["url_param"]
    cat_name = target["name"]
    target_url = f"{BASE_API}/getPlaylistsByCategory/{profile_id}?{param}&__culture=tr-tr"
    
    auth_headers = HEADERS.copy()
    auth_headers["Authorization"] = f"Bearer {MANUAL_TOKEN}"
    
    print(f"\n🌍 '{cat_name}' sayfası taranıyor...")
    
    try:
        response = requests.get(target_url, headers=auth_headers)
        if response.status_code != 200:
            print(f"   ❌ Erişim Hatası: {response.status_code}")
            return []

        data = response.json()
        playlists = data.get("playlists", [])
        
        if not playlists:
            print(f"   ⚠️ Liste boş geldi.")
            return []

        items_found = []
        print(f"   📦 {len(playlists)} farklı raf bulundu.")

        for playlist in playlists:
            shelf_title = playlist.get("title", "Genel")
            items = playlist.get("items", [])
            for item in items:
                direct_id = item.get("videoContentId")
                title = item.get("name") or item.get("title") or item.get("originalTitle")
                poster = item.get("logoImageUrl") or item.get("posterImageUrl")
                if direct_id:
                    items_found.append({
                        "id": direct_id,
                        "title": title,
                        "category": cat_name,
                        "sub_category": shelf_title,
                        "poster": poster or "",
                        "profile_id": profile_id
                    })
        print(f"   ✅ '{cat_name}' kategorisinden {len(items_found)} içerik alındı.")
        return items_found
    except Exception as e:
        print(f"🔥 Hata ({cat_name}): {e}")
        return []

def get_stream_url(content):
    profile_id = content["profile_id"]
    params = {"videoContentId": content["id"], "packageType": "Dash", "__culture": "tr-tr"}
    auth_headers = HEADERS.copy()
    auth_headers["Authorization"] = f"Bearer {MANUAL_TOKEN}"
    
    try:
        response = requests.get(f"{BASE_API}/getPlaybackInfo/{profile_id}/", headers=auth_headers, params=params)
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

def save_as_m3u(data_list, filename="fanatik_gain.m3u"):
    print(f"\n📺 M3U dosyası oluşturuluyor: {filename}...")
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")
            for item in data_list:
                title = item.get("title", "Bilinmeyen")
                group = f"Gain - {item.get('category', 'Genel')}"
                logo = item.get("poster", "")
                url = item.get("stream_url", "")
                f.write(f'#EXTINF:-1 group-title="{group}" tvg-logo="{logo}", {title}\n')
                f.write('#EXTVLCOPT:http-user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)\n')
                f.write(f"{url}\n")
        print("✅ M3U Kaydedildi!")
    except Exception as e:
        print(f"❌ M3U Hatası: {e}")

def main():
    if "BURAYA" in MANUAL_TOKEN:
        print("⛔ Lütfen Token'ı girmeyi unutma!")
        return

    all_content = []
    processed_ids = set()

    for target in TARGETS:
        target_items = get_contents(target)
        for item in target_items:
            if item["id"] not in processed_ids:
                all_content.append(item)
                processed_ids.add(item["id"])
        time.sleep(1)

    total = len(all_content)
    if total == 0:
        print("\n⛔ HİÇBİR İÇERİK BULUNAMADI. Token'ı yenilemen gerekiyor.")
        return

    print(f"\n🚀 TOPLAM {total} BENZERSİZ İÇERİK BULUNDU! Linkler çekiliyor...")
    final_list = []
    for i, content in enumerate(all_content):
        full_data = get_stream_url(content)
        if full_data:
            if "profile_id" in full_data: del full_data["profile_id"]
            final_list.append(full_data)
        if (i + 1) % 20 == 0: print(f"   👍 {i+1} içerik tarandı... ({len(final_list)} başarılı)")
        time.sleep(0.05)

    with open("gain_full_archive.json", "w", encoding="utf-8") as f:
        json.dump(final_list, f, indent=4, ensure_ascii=False)
    save_as_m3u(final_list, "fanatik_gain.m3u")
    print("\n🏁 TÜM İŞLEMLER TAMAMLANDI!")

if __name__ == "__main__":
    main()
