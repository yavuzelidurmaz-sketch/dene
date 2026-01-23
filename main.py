import requests
import json
import time

# --- YENİ TOKENI BURAYA YAPIŞTIR ---
MANUAL_TOKEN = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJwcm9qZWN0SWQiOiIyZGE3a2Y4amYiLCJpZGVudGl0eSI6ImVuZHVzZXIiLCJhbm9ueW1vdXMiOmZhbHNlLCJ1c2VySWQiOiJlNGMzYWY2Yi05YWQyLTQ3NDYtYTVlNC0yNGQ1ODQyNjZmYzMiLCJjbGFpbXMiOnsiZW1haWwiOiJmYXRtYW51cnJrcmttenoxODZAZ21haWwuY29tIiwiZnVsbE5hbWUiOiJwaXJ0aXN0YW4iLCJwcm9maWxlSWQiOiJVUkNNUURMRExYSkxITFBGQkFOMFpJOVYiLCJwcm9maWxlQXZhdGFyIjoiUCIsImlzS2lkUHJvZmlsZSI6ZmFsc2V9LCJzZXNzaW9uSWQiOiIyOTVhNWM4N2RlYTk0Y2FhOTcyOTZlYzY2OWNiYjBmZCIsImlhdCI6MTc2OTE5NjA1MywiZXhwIjoxNzcxNzg4MDUzfQ.yKLLAEotOL9BWz3oFDsVyos7zcfMxnPFgRJpmsn50B6IbBe3SMgeZo02X0ghZdz93xB5kUETdBlDRmt1QHzAJ_7z_4qOLukh-z2pnPeaImVT-fRZGjK4Ez--GjRS_sOdnXgNVIdzYkiEsqyVabi8wL46K0C-1oo5B9bJ7sjAxaadAAs4rFKQ-bKx-c1rKgOso31XArEn3zIo0bhjhuvuOECNwvVbDu5Dg2LcgqkbDRA8LQ37iDudkaAwF9jVnxTNHLzmrxMf6KwftzgdmkIoizrsThFw1vVJWXTdaXNXlS5ZbOvC-iQ3UH3gAk2Yjv6gDxk0YgvRRYsDE3vwNKrbeQ"

# --- AYARLAR ---
PROJECT_ID = "2da7kf8jf"
ADULT_PROFILE_ID = "URCMQDLDLXJLHLPFBAN0ZI9V"
KIDS_PROFILE_ID = "KIBPFC0Q9Z08Q1UMMJTO61NI"

# Hedefler
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
    """Sezon içindeki bölümleri sayfa sayfa çeker"""
    all_episodes = []
    page = 1
    while True:
        # Bölümleri de 100'er 100'er istiyoruz ki hata vermesin
        url = f"{BASE_API}/getProfileSeason/{profile_id}?seasonId={season_id}&titleId={title_id}&__culture=tr-tr&page={page}&pageSize=100"
        try:
            res = requests.get(url, headers=HEADERS)
            if res.status_code == 200:
                data = res.json()
                eps = data.get("episodes", [])
                if not eps:
                    break # Bölüm bitti
                all_episodes.extend(eps)
                page += 1
            else:
                break
        except:
            break
    return all_episodes

def get_contents(target):
    """Kategoriyi sayfa sayfa (Pagination) tarar"""
    print(f"\n🌍 '{target['name']}' bölümü taranıyor...")
    
    contents = []
    processed_ids = set()
    page = 1
    
    while True:
        # Sayfa sayfa istek (Her sayfada 20 içerik standarttır)
        url = f"{BASE_API}/getPlaylistsByCategory/{target['profile_id']}?{target['param']}&__culture=tr-tr&page={page}&pageSize=20"
        
        try:
            res = requests.get(url, headers=HEADERS)
            
            if res.status_code != 200:
                # 400/403 hatası varsa döngüyü kır
                if page == 1: 
                    print(f"   ❌ Hata Kodu: {res.status_code} (Token veya İstek Hatalı)")
                break
                
            data = res.json()
            playlists = data.get("playlists", [])
            
            # Eğer liste boşsa, bu kategorideki sayfalar bitmiş demektir
            if not playlists:
                # print(f"   ℹ️ Sayfa {page} boş, tarama bitti.")
                break
            
            # print(f"   📄 Sayfa {page} işleniyor... ({len(playlists)} raf)")

            items_found_on_page = 0
            for playlist in playlists:
                shelf_name = playlist.get("title", "Genel")
                items = playlist.get("items", [])
                
                for item in items:
                    title_id = item.get("titleId")
                    video_id = item.get("videoContentId")
                    name = item.get("name") or item.get("title")
                    poster = item.get("logoImageUrl") or item.get("posterImageUrl")
                    seasons = item.get("seasons", [])

                    if title_id in processed_ids: continue
                    processed_ids.add(title_id)
                    items_found_on_page += 1

                    # --- KATEGORİLENDİRME ---
                    if seasons: # Dizi/Program
                        # print(f"      🔎 Dizi: {name}")
                        for season in seasons:
                            episodes = get_episodes(title_id, season.get("id"), target['profile_id'])
                            for ep in episodes:
                                ep_num = ep.get("episode", 0)
                                ep_name = ep.get("name", "")
                                full_title = f"{ep_num}. Bölüm - {ep_name}"
                                
                                prefix = "Kids" if target['name'] == "Kids" else target['name']
                                group_name = f"Gain - {prefix} | {name}"

                                contents.append({
                                    "id": ep.get("videoContentId"),
                                    "title": full_title,
                                    "group": group_name,
                                    "poster": poster,
                                    "profile_id": target['profile_id']
                                })
                    elif video_id: # Film
                        if target['name'] == "Kids":
                            group_name = f"Gain - Kids | {shelf_name}"
                        elif target['name'] == "Film":
                            group_name = f"Gain - Film | {shelf_name}"
                        else:
                            group_name = f"Gain - {target['name']} | {shelf_name}"

                        contents.append({
                            "id": video_id,
                            "title": name,
                            "group": group_name,
                            "poster": poster,
                            "profile_id": target['profile_id']
                        })
            
            # Eğer bu sayfada hiç yeni içerik yoksa döngüyü bitir (Sonsuz döngü koruması)
            if items_found_on_page == 0 and page > 1:
                break
                
            page += 1 # Sonraki sayfaya geç
            time.sleep(0.2) # Sunucuyu yormamak için bekle

        except Exception as e:
            print(f"🔥 Kritik Hata: {e}")
            break

    print(f"   ✅ '{target['name']}' tamamlandı. Toplam {len(contents)} video bulundu.")
    return contents

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
    print(f"\n📺 M3U dosyası oluşturuluyor: {filename}...")
    data.sort(key=lambda x: x["group"])
    with open(filename, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for item in data:
            f.write(f'#EXTINF:-1 group-title="{item["group"]}" tvg-logo="{item["poster"]}", {item["title"]}\n')
            f.write('#EXTVLCOPT:http-user-agent=Mozilla/5.0\n')
            f.write(f"{item['stream_url']}\n")
    print("✅ M3U Hazır!")

def main():
    if "BURAYA" in MANUAL_TOKEN:
        print("⛔ Lütfen YENİ Token'ı girmeyi unutma!")
        return

    all_videos = []
    
    for target in TARGETS:
        items = get_contents(target)
        all_videos.extend(items)

    total = len(all_videos)
    if total == 0:
        print("\n⛔ LİSTE BOŞ GELDİ! Token hatalı olabilir veya sunucu cevap vermiyor.")
        return

    print(f"\n🚀 TOPLAM {total} İÇERİK İÇİN LİNKLER ÇEKİLİYOR...")
    
    final_list = []
    for i, video in enumerate(all_videos):
        full_data = get_stream_url(video)
        if full_data:
            del full_data["profile_id"]
            final_list.append(full_data)
        
        if (i+1) % 50 == 0: 
            print(f"   👍 {i+1}/{total} tamamlandı... ({len(final_list)} başarılı)")
        
        time.sleep(0.01)

    with open("gain_full_archive.json", "w", encoding="utf-8") as f:
        json.dump(final_list, f, indent=4, ensure_ascii=False)
    
    save_m3u(final_list)
    print("\n🏁 OPERASYON BAŞARIYLA TAMAMLANDI!")

if __name__ == "__main__":
    main()
