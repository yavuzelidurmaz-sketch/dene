import requests
import json
import time

# --- ÇOK ÖNEMLİ: KODU ÇALIŞTIRMADAN HEMEN ÖNCE YENİ TOKEN AL ---
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
    """Sezon içindeki tüm bölümleri çeker"""
    # pageSize=500 ekleyerek tüm bölümleri zorluyoruz
    url = f"{BASE_API}/getProfileSeason/{profile_id}?seasonId={season_id}&titleId={title_id}&__culture=tr-tr&pageSize=500"
    try:
        res = requests.get(url, headers=HEADERS)
        if res.status_code == 200:
            return res.json().get("episodes", [])
    except:
        pass
    return []

def get_contents(target):
    """Ana sayfadaki tüm rafları ve içindekileri tarar"""
    # pageSize=500 ekleyerek vitrindeki her şeyi almaya çalışıyoruz
    url = f"{BASE_API}/getPlaylistsByCategory/{target['profile_id']}?{target['param']}&__culture=tr-tr&pageSize=500"
    print(f"\n🌍 '{target['name']}' bölümü taranıyor...")
    
    contents = []
    processed_ids = set() # Aynı videoyu tekrar eklememek için
    
    try:
        res = requests.get(url, headers=HEADERS)
        if res.status_code != 200:
            print(f"   ❌ Erişim Hatası (Token Süresi Dolmuş!): {res.status_code}")
            return []
            
        playlists = res.json().get("playlists", [])
        print(f"   📦 {len(playlists)} farklı raf bulundu. Detaylı tarama başlıyor...")

        for playlist in playlists:
            shelf_name = playlist.get("title", "Genel") # Örn: "Aksiyon", "Komedi"
            items = playlist.get("items", [])
            
            # print(f"      📂 Raf: {shelf_name} ({len(items)} içerik)")
            
            for item in items:
                title_id = item.get("titleId")
                video_id = item.get("videoContentId")
                name = item.get("name") or item.get("title")
                poster = item.get("logoImageUrl") or item.get("posterImageUrl")
                seasons = item.get("seasons", [])

                # Tekrarları önle (Eğer daha önce işlediysek geç)
                if title_id in processed_ids: continue
                processed_ids.add(title_id)

                # --- AKILLI KATEGORİLENDİRME ---
                
                # 1. DİZİ / PROGRAM İSE (Sezonu varsa)
                if seasons:
                    for season in seasons:
                        episodes = get_episodes(title_id, season.get("id"), target['profile_id'])
                        for ep in episodes:
                            ep_num = ep.get("episode", 0)
                            ep_name = ep.get("name", "")
                            full_title = f"{ep_num}. Bölüm - {ep_name}"
                            
                            # GRUPLAMA: "Gain - Dizi | Ayak İşleri"
                            # Kids ise: "Gain - Kids | Kral Şakir"
                            prefix = "Kids" if target['name'] == "Kids" else target['name']
                            group_name = f"Gain - {prefix} | {name}"

                            contents.append({
                                "id": ep.get("videoContentId"),
                                "title": full_title,
                                "group": group_name,
                                "poster": poster,
                                "profile_id": target['profile_id']
                            })

                # 2. FİLM İSE (Sezonu yoksa)
                elif video_id:
                    # GRUPLAMA: "Gain - Film | Aksiyon"
                    # Kids ise: "Gain - Kids | Filmler"
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
                            
        print(f"   ✅ '{target['name']}' bölümünden {len(contents)} video listeye eklendi.")
        return contents

    except Exception as e:
        print(f"🔥 Kritik Hata: {e}")
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
    print(f"\n📺 M3U dosyası oluşturuluyor: {filename}...")
    # Kategorilere göre sıralayalım ki listede düzgün dursun
    data.sort(key=lambda x: x["group"])
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for item in data:
            # M3U Formatı
            f.write(f'#EXTINF:-1 group-title="{item["group"]}" tvg-logo="{item["poster"]}", {item["title"]}\n')
            f.write('#EXTVLCOPT:http-user-agent=Mozilla/5.0\n')
            f.write(f"{item['stream_url']}\n")
    print("✅ M3U Hazır! Dosyayı indirip kullanabilirsin.")

def main():
    if "BURAYA" in MANUAL_TOKEN:
        print("⛔ Lütfen YENİ Token'ı girmeyi unutma!")
        return

    all_videos = []
    
    for target in TARGETS:
        items = get_contents(target)
        all_videos.extend(items)
        time.sleep(1) # Nezaket beklemesi

    total = len(all_videos)
    if total == 0:
        print("\n⛔ LİSTE BOŞ GELDİ! Token süren dolmuş. Lütfen F12 -> Network'ten YENİ TOKEN al.")
        return

    print(f"\n🚀 TOPLAM {total} İÇERİK İÇİN LİNKLER ÇEKİLİYOR...")
    print("   (Bu işlem içerik sayısına göre biraz sürebilir, lütfen bekle...)")
    
    final_list = []
    for i, video in enumerate(all_videos):
        full_data = get_stream_url(video)
        if full_data:
            # Gereksiz veriyi temizle
            del full_data["profile_id"]
            final_list.append(full_data)
        
        # Her 25 videoda bir bilgi ver
        if (i+1) % 25 == 0: 
            print(f"   👍 {i+1}/{total} tamamlandı... ({len(final_list)} başarılı)")
        
        time.sleep(0.01) # Çok hızlı istek atıp banlanmamak için

    # Yedek JSON kaydı
    with open("gain_full_archive.json", "w", encoding="utf-8") as f:
        json.dump(final_list, f, indent=4, ensure_ascii=False)
    
    # Asıl M3U kaydı
    save_m3u(final_list)
    print("\n🏁 OPERASYON BAŞARIYLA TAMAMLANDI!")

if __name__ == "__main__":
    main()
