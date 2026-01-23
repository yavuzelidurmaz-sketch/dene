import requests
import json
import time

# --- TOKEN (MUTLAKA YENİSİNİ ALIP YAPIŞTIR) ---
MANUAL_TOKEN = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJwcm9qZWN0SWQiOiIyZGE3a2Y4amYiLCJpZGVudGl0eSI6ImVuZHVzZXIiLCJhbm9ueW1vdXMiOmZhbHNlLCJ1c2VySWQiOiJlNGMzYWY2Yi05YWQyLTQ3NDYtYTVlNC0yNGQ1ODQyNjZmYzMiLCJjbGFpbXMiOnsiZW1haWwiOiJmYXRtYW51cnJrcmttenoxODZAZ21haWwuY29tIiwiZnVsbE5hbWUiOiJwaXJ0aXN0YW4iLCJwcm9maWxlSWQiOiJVUkNNUURMRExYSkxITFBGQkFOMFpJOVYiLCJwcm9maWxlQXZhdGFyIjoiUCIsImlzS2lkUHJvZmlsZSI6ZmFsc2V9LCJzZXNzaW9uSWQiOiIyOTVhNWM4N2RlYTk0Y2FhOTcyOTZlYzY2OWNiYjBmZCIsImlhdCI6MTc2OTE5NjA1MywiZXhwIjoxNzcxNzg4MDUzfQ.yKLLAEotOL9BWz3oFDsVyos7zcfMxnPFgRJpmsn50B6IbBe3SMgeZo02X0ghZdz93xB5kUETdBlDRmt1QHzAJ_7z_4qOLukh-z2pnPeaImVT-fRZGjK4Ez--GjRS_sOdnXgNVIdzYkiEsqyVabi8wL46K0C-1oo5B9bJ7sjAxaadAAs4rFKQ-bKx-c1rKgOso31XArEn3zIo0bhjhuvuOECNwvVbDu5Dg2LcgqkbDRA8LQ37iDudkaAwF9jVnxTNHLzmrxMf6KwftzgdmkIoizrsThFw1vVJWXTdaXNXlS5ZbOvC-iQ3UH3gAk2Yjv6gDxk0YgvRRYsDE3vwNKrbeQ"

# --- AYARLAR ---
PROJECT_ID = "2da7kf8jf"
ADULT_PROFILE_ID = "URCMQDLDLXJLHLPFBAN0ZI9V"
KIDS_PROFILE_ID = "KIBPFC0Q9Z08Q1UMMJTO61NI"

# Taranacak Kategoriler
TARGETS = [
    {"name": "Film", "profile_id": ADULT_PROFILE_ID, "param": "slug=%2Ffilm"},
    {"name": "Dizi", "profile_id": ADULT_PROFILE_ID, "param": "slug=%2Fdizi"},
    {"name": "Program", "profile_id": ADULT_PROFILE_ID, "param": "slug=%2Fprogram"},
    {"name": "Kids", "profile_id": KIDS_PROFILE_ID, "param": "categoryName=MAIN-PAGE"}
]

BASE_API = f"https://api.gain.tv/{PROJECT_ID}/CALL/ProfileTitle"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Content-Type": "application/json",
    "Authorization": f"Bearer {MANUAL_TOKEN}",
    "x-gain-platform": "web"
}

def get_episodes(title_id, season_id, profile_id):
    """Sezon içindeki bölümleri çeker"""
    url = f"{BASE_API}/getProfileSeason/{profile_id}?seasonId={season_id}&titleId={title_id}&__culture=tr-tr"
    try:
        res = requests.get(url, headers=HEADERS)
        if res.status_code == 200:
            return res.json().get("episodes", [])
    except:
        pass
    return []

def get_contents(target):
    """Kategoriyi tarar (Filtresiz Mod)"""
    url = f"{BASE_API}/getPlaylistsByCategory/{target['profile_id']}?{target['param']}&__culture=tr-tr"
    print(f"\n🌍 '{target['name']}' taranıyor...")
    
    contents = []
    processed_ids = set()
    
    try:
        res = requests.get(url, headers=HEADERS)
        if res.status_code != 200:
            print(f"   ❌ Erişim Hatası (Token Eski olabilir): {res.status_code}")
            return []
            
        playlists = res.json().get("playlists", [])
        print(f"   📦 {len(playlists)} raf bulundu. Analiz ediliyor...")

        for playlist in playlists:
            items = playlist.get("items", [])
            for item in items:
                title_id = item.get("titleId")
                video_id = item.get("videoContentId")
                name = item.get("name") or item.get("title")
                poster = item.get("logoImageUrl") or item.get("posterImageUrl")
                seasons = item.get("seasons", [])

                if title_id in processed_ids: continue
                processed_ids.add(title_id)

                # --- YENİ MANTIK: TÜR İSMİNE BAKMA, İÇERİĞE BAK ---
                
                # 1. Eğer SEZON bilgisi varsa -> Bu bir DİZİDİR
                if seasons:
                    print(f"   🔎 Dizi Bulundu: {name}")
                    for season in seasons:
                        episodes = get_episodes(title_id, season.get("id"), target['profile_id'])
                        for ep in episodes:
                            full_title = f"{ep.get('episode', 0)}. Bölüm - {ep.get('name', '')}"
                            contents.append({
                                "id": ep.get("videoContentId"),
                                "title": full_title,
                                "group": f"Gain - {name}", # Dizi Adı Klasörü
                                "poster": poster,
                                "profile_id": target['profile_id']
                            })

                # 2. Eğer SEZON yoksa ama Video ID varsa -> Bu bir FİLMDİR
                elif video_id:
                    # Dizi kategorisindeysek ve tekil video geldiyse onu da alalım
                    contents.append({
                        "id": video_id,
                        "title": name,
                        "group": f"Gain - {target['name']}", # Film/Program Klasörü
                        "poster": poster,
                        "profile_id": target['profile_id']
                    })
                            
        print(f"   ✅ '{target['name']}' kategorisinden {len(contents)} video eklendi.")
        return contents

    except Exception as e:
        print(f"🔥 Hata: {e}")
        return []

def get_stream_url(content):
    url = f"{BASE_API}/getPlaybackInfo/{content['profile_id']}/"
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

def save_m3u(data, filename="fanatik_gain.m3u"):
    print(f"\n📺 M3U oluşturuluyor: {filename}...")
    with open(filename, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for item in data:
            f.write(f'#EXTINF:-1 group-title="{item["group"]}" tvg-logo="{item["poster"]}", {item["title"]}\n')
            f.write('#EXTVLCOPT:http-user-agent=Mozilla/5.0\n')
            f.write(f"{item['stream_url']}\n")
    print("✅ M3U Hazır!")

def main():
    if "BURAYA" in MANUAL_TOKEN:
        print("⛔ Token girmeyi unutma!")
        return

    all_videos = []
    for target in TARGETS:
        items = get_contents(target)
        all_videos.extend(items)
        time.sleep(1)

    total = len(all_videos)
    if total == 0:
        print("\n⛔ HİÇ İÇERİK YOK. Token süresi dolmuş olabilir.")
        return

    print(f"\n🚀 TOPLAM {total} VİDEO İÇİN LİNKLER ÇEKİLİYOR...")
    
    final_list = []
    for i, video in enumerate(all_videos):
        full_data = get_stream_url(video)
        if full_data:
            del full_data["profile_id"]
            final_list.append(full_data)
        if (i+1) % 10 == 0: print(f"   👍 {i+1}/{total} tamamlandı...")
        time.sleep(0.05)

    with open("gain_full_archive.json", "w", encoding="utf-8") as f:
        json.dump(final_list, f, indent=4, ensure_ascii=False)
    
    save_m3u(final_list)
    print("\n🏁 MUTLU SON! Dosyalar hazır.")

if __name__ == "__main__":
    main()
