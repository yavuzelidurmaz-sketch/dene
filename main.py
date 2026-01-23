import requests
import json
import time

# --- TOKEN (MUTLAKA YENİ VE GEÇERLİ OLMALI) ---
MANUAL_TOKEN = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJwcm9qZWN0SWQiOiIyZGE3a2Y4amYiLCJpZGVudGl0eSI6ImVuZHVzZXIiLCJhbm9ueW1vdXMiOmZhbHNlLCJ1c2VySWQiOiJlNGMzYWY2Yi05YWQyLTQ3NDYtYTVlNC0yNGQ1ODQyNjZmYzMiLCJjbGFpbXMiOnsiZW1haWwiOiJmYXRtYW51cnJrcmttenoxODZAZ21haWwuY29tIiwiZnVsbE5hbWUiOiJwaXJ0aXN0YW4iLCJwcm9maWxlSWQiOiJVUkNNUURMRExYSkxITFBGQkFOMFpJOVYiLCJwcm9maWxlQXZhdGFyIjoiUCIsImlzS2lkUHJvZmlsZSI6ZmFsc2V9LCJzZXNzaW9uSWQiOiIyOTVhNWM4N2RlYTk0Y2FhOTcyOTZlYzY2OWNiYjBmZCIsImlhdCI6MTc2OTE5NjA1MywiZXhwIjoxNzcxNzg4MDUzfQ.yKLLAEotOL9BWz3oFDsVyos7zcfMxnPFgRJpmsn50B6IbBe3SMgeZo02X0ghZdz93xB5kUETdBlDRmt1QHzAJ_7z_4qOLukh-z2pnPeaImVT-fRZGjK4Ez--GjRS_sOdnXgNVIdzYkiEsqyVabi8wL46K0C-1oo5B9bJ7sjAxaadAAs4rFKQ-bKx-c1rKgOso31XArEn3zIo0bhjhuvuOECNwvVbDu5Dg2LcgqkbDRA8LQ37iDudkaAwF9jVnxTNHLzmrxMf6KwftzgdmkIoizrsThFw1vVJWXTdaXNXlS5ZbOvC-iQ3UH3gAk2Yjv6gDxk0YgvRRYsDE3vwNKrbeQ"

# --- SABİTLER ---
PROJECT_ID = "2da7kf8jf"
BASE_API = f"https://api.gain.tv/{PROJECT_ID}/CALL"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Content-Type": "application/json",
    "Authorization": f"Bearer {MANUAL_TOKEN}",
    "x-gain-platform": "web"
}

def get_my_profiles():
    """Token'a ait profil ID'lerini otomatik çeker"""
    print("👤 Profil bilgileri alınıyor...")
    # Kullanıcı profillerini çeken endpoint
    url = f"{BASE_API}/User/getProfiles?__culture=tr-tr"
    
    try:
        res = requests.get(url, headers=HEADERS)
        if res.status_code == 200:
            profiles = res.json().get("profiles", [])
            adult_id = None
            kids_id = None
            
            for p in profiles:
                if p.get("isKidProfile"):
                    kids_id = p.get("id")
                else:
                    adult_id = p.get("id") # İlk yetişkin profilini al
            
            print(f"   ✅ Yetişkin ID Bulundu: {adult_id}")
            print(f"   ✅ Çocuk ID Bulundu: {kids_id}")
            return adult_id, kids_id
        else:
            print(f"   ❌ Profil alınamadı. Hata kodu: {res.status_code}")
            print("   ⚠️ Token süresi dolmuş olabilir.")
            return None, None
    except Exception as e:
        print(f"   🔥 Profil hatası: {e}")
        return None, None

def get_episodes(title_id, season_id, profile_id):
    url = f"{BASE_API}/ProfileTitle/getProfileSeason/{profile_id}?seasonId={season_id}&titleId={title_id}&__culture=tr-tr&pageSize=200"
    try:
        res = requests.get(url, headers=HEADERS)
        if res.status_code == 200:
            return res.json().get("episodes", [])
    except:
        pass
    return []

def get_show_details(title_id, profile_id):
    url = f"{BASE_API}/ProfileTitle/getProfileTitle/{profile_id}?titleId={title_id}&__culture=tr-tr"
    try:
        res = requests.get(url, headers=HEADERS)
        if res.status_code == 200:
            return res.json()
    except:
        pass
    return {}

def get_contents_by_category(profile_id, category_slug, category_name):
    """Belirtilen kategorideki rafları tarar"""
    if not profile_id:
        return []

    print(f"\n🌍 '{category_name}' kategorisi taranıyor...")
    
    # Kategori parametresini ayarla
    if category_name == "Kids":
        param = "categoryName=MAIN-PAGE"
    else:
        param = f"slug=%2F{category_slug}"

    url = f"{BASE_API}/ProfileTitle/getPlaylistsByCategory/{profile_id}?{param}&__culture=tr-tr"

    contents = []
    processed_ids = set()

    try:
        res = requests.get(url, headers=HEADERS)
        if res.status_code != 200:
            print(f"   ❌ {category_name} Erişilemedi (Hata: {res.status_code})")
            return []

        playlists = res.json().get("playlists", [])
        print(f"   📦 {len(playlists)} adet raf bulundu.")

        for playlist in playlists:
            items = playlist.get("items", [])
            for item in items:
                title_id = item.get("titleId")
                video_id = item.get("videoContentId")
                name = item.get("name") or item.get("title")
                poster = item.get("logoImageUrl") or item.get("posterImageUrl")

                unique_key = title_id if title_id else video_id
                if not unique_key or unique_key in processed_ids:
                    continue
                processed_ids.add(unique_key)

                # Dizi/Film Ayrımı
                is_series = False
                seasons = []

                if title_id:
                    details = get_show_details(title_id, profile_id)
                    seasons = details.get("seasons", [])
                    if seasons:
                        is_series = True
                    if not video_id:
                        video_id = details.get("videoContentId")

                if is_series:
                    # Dizi
                    for season in seasons:
                        episodes = get_episodes(title_id, season.get("id"), profile_id)
                        for ep in episodes:
                            full_title = f"{name} - S{season.get('seasonNum',1)}B{ep.get('episode',0)} - {ep.get('name','')}"
                            contents.append({
                                "id": ep.get("videoContentId"),
                                "title": full_title,
                                "group": f"Gain - {name}",
                                "poster": poster,
                                "profile_id": profile_id
                            })
                elif video_id:
                    # Film/Program Tek Bölüm
                    contents.append({
                        "id": video_id,
                        "title": name,
                        "group": f"Gain - {category_name}",
                        "poster": poster,
                        "profile_id": profile_id
                    })

        print(f"   ✅ '{category_name}' bitti. ({len(contents)} içerik)")
        return contents

    except Exception as e:
        print(f"🔥 Hata: {e}")
        return []

def get_stream_url(content):
    url = f"{BASE_API}/ProfileTitle/getPlaybackInfo/{content['profile_id']}/"
    params = {"videoContentId": content["id"], "packageType": "Dash", "__culture": "tr-tr"}
    try:
        res = requests.get(url, headers=HEADERS, params=params)
        if res.status_code == 200:
            pb_url = res.json().get("currentVideoContent", {}).get("playbackUrl")
            if pb_url:
                content["stream_url"] = pb_url
                return content
    except:
        pass
    return None

def save_m3u(data):
    filename = "gain_archive.m3u"
    print(f"\n📺 {filename} kaydediliyor...")
    with open(filename, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for item in data:
            if "stream_url" in item:
                f.write(f'#EXTINF:-1 group-title="{item["group"]}" tvg-logo="{item["poster"]}", {item["title"]}\n')
                f.write('#EXTVLCOPT:http-user-agent=Mozilla/5.0\n')
                f.write(f"{item['stream_url']}\n")
    print("✅ Dosya hazır!")

def main():
    if "BURAYA" in MANUAL_TOKEN:
        print("⛔ Lütfen TOKEN yapıştırın!")
        return

    # 1. OTOMATİK PROFİL BULMA (Manuel girişe gerek yok)
    adult_id, kids_id = get_my_profiles()
    
    if not adult_id:
        print("⛔ Geçerli bir profil bulunamadı. Token hatalı.")
        return

    # 2. HEDEFLERİ OLUŞTUR
    targets = [
        {"slug": "dizi", "name": "Dizi", "pid": adult_id},
        {"slug": "film", "name": "Film", "pid": adult_id},
        {"slug": "program", "name": "Program", "pid": adult_id},
        {"slug": "belgesel", "name": "Belgesel", "pid": adult_id}
    ]
    if kids_id:
        targets.append({"slug": "kids", "name": "Kids", "pid": kids_id})

    all_videos = []

    # 3. TARAMA
    for t in targets:
        items = get_contents_by_category(t["pid"], t["slug"], t["name"])
        all_videos.extend(items)
        time.sleep(1)

    total = len(all_videos)
    print(f"\n🚀 TOPLAM {total} İÇERİK BULUNDU. Linkler çekiliyor...")

    if total == 0:
        return

    # 4. LİNKLERİ AL
    final_list = []
    for i, video in enumerate(all_videos):
        full_data = get_stream_url(video)
        if full_data:
            del full_data["profile_id"]
            final_list.append(full_data)
        
        if (i+1) % 20 == 0: print(f"   👍 {i+1}/{total} tamamlandı...")
        time.sleep(0.05)

    save_m3u(final_list)

if __name__ == "__main__":
    main()
