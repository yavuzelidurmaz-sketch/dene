import requests
import json
import time

# --- TOKEN (GÜNCEL TOKEN'I BURAYA YAPIŞTIR) ---
MANUAL_TOKEN = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9..." # Kendi token'ını buraya yapıştır

# --- AYARLAR ---
PROJECT_ID = "2da7kf8jf"
ADULT_PROFILE_ID = "URCMQDLDLXJLHLPFBAN0ZI9V"
KIDS_PROFILE_ID = "KIBPFC0Q9Z08Q1UMMJTO61NI"

# Taranacak Ana Kategoriler
TARGETS = [
    {"name": "Film", "profile_id": ADULT_PROFILE_ID, "param": "slug=%2Ffilm"},
    {"name": "Dizi", "profile_id": ADULT_PROFILE_ID, "param": "slug=%2Fdizi"},
    {"name": "Program", "profile_id": ADULT_PROFILE_ID, "param": "slug=%2Fprogram"},
    {"name": "Belgesel", "profile_id": ADULT_PROFILE_ID, "param": "slug=%2Fbelgesel"},
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
    """
    Bir dizinin/programın spesifik sezonundaki tüm bölümleri çeker.
    """
    url = f"{BASE_API}/getProfileSeason/{profile_id}?seasonId={season_id}&titleId={title_id}&__culture=tr-tr"
    try:
        res = requests.get(url, headers=HEADERS)
        if res.status_code == 200:
            return res.json().get("episodes", [])
    except:
        pass
    return []

def get_full_playlist_items(playlist_id, profile_id):
    """
    YENİ: Bir rafın (Slider) içindeki TÜM içerikleri çeker (Pagination Logic).
    Sayfadaki görünen 10 tane ile yetinmez, 'Tümünü Gör' yapmış gibi hepsini çeker.
    """
    all_items = []
    page = 0
    page_size = 100  # Tek seferde 100 içerik iste
    
    while True:
        # getPlaylistItems endpoint'i rafın tamamını verir
        url = f"{BASE_API}/getPlaylistItems/{profile_id}?playlistId={playlist_id}&page={page}&pageSize={page_size}&__culture=tr-tr"
        try:
            res = requests.get(url, headers=HEADERS)
            if res.status_code != 200:
                break
                
            data = res.json()
            items = data.get("items", [])
            
            if not items:
                break
                
            all_items.extend(items)
            
            # Eğer gelen içerik sayısı sayfa limitinden azsa son sayfadayız demektir
            if len(items) < page_size:
                break
                
            page += 1
            time.sleep(0.2) # API'yi boğmamak için minik bekleme
            
        except Exception as e:
            print(f"   ⚠️ Raf detay hatası: {e}")
            break
            
    return all_items

def get_contents(target):
    """
    Ana kategori sayfasındaki rafları bulur ve her rafı derinlemesine tarar.
    """
    url = f"{BASE_API}/getPlaylistsByCategory/{target['profile_id']}?{target['param']}&__culture=tr-tr"
    print(f"\n🌍 KATEGORİ TARANIYOR: '{target['name']}'...")

    contents = []
    processed_ids = set() # Aynı içerik farklı raflarda olabilir, tekrar eklemeyelim

    try:
        res = requests.get(url, headers=HEADERS)
        if res.status_code != 200:
            print(f"   ❌ Erişim Hatası (Token kontrol et): {res.status_code}")
            return []

        # Ana sayfadaki rafları (Sliderları) al
        playlists = res.json().get("playlists", [])
        print(f"   📦 {len(playlists)} adet raf (kategori başlığı) bulundu.")

        for playlist in playlists:
            playlist_name = playlist.get("name", "Bilinmeyen Raf")
            playlist_id = playlist.get("id")
            
            if not playlist_id:
                continue

            print(f"      📂 Raf Taranıyor: {playlist_name}...")
            
            # BU RAFIN İÇİNDEKİ HER ŞEYİ ÇEK (Limitsiz)
            items = get_full_playlist_items(playlist_id, target['profile_id'])
            
            for item in items:
                title_id = item.get("titleId")
                video_id = item.get("videoContentId")
                name = item.get("name") or item.get("title")
                poster = item.get("logoImageUrl") or item.get("posterImageUrl")
                seasons = item.get("seasons", [])
                
                # Çift kayıt engelleme
                if title_id in processed_ids: 
                    continue
                processed_ids.add(title_id)

                # --- MANTIK: SEZON VARSA DİZİDİR, YOKSA FİLMDİR ---

                # 1. DİZİLER VE PROGRAMLAR (Sezon Yapısı Olanlar)
                if seasons:
                    # print(f"         Found Series/Program: {name}") # İstersen logu aç
                    for season in seasons:
                        episodes = get_episodes(title_id, season.get("id"), target['profile_id'])
                        for ep in episodes:
                            # Bölüm adını oluştur
                            season_num = ep.get("seasonNumber", 1)
                            episode_num = ep.get("episode", 0)
                            ep_name = ep.get("name", "")
                            
                            full_title = f"{name} - S{season_num}E{episode_num} - {ep_name}"
                            
                            contents.append({
                                "id": ep.get("videoContentId"),
                                "title": full_title,
                                "group": f"Gain - {target['name']} (Diziler)", 
                                "poster": poster,
                                "profile_id": target['profile_id']
                            })

                # 2. FİLMLER VE TEKİL VİDEOLAR
                elif video_id:
                    contents.append({
                        "id": video_id,
                        "title": name,
                        "group": f"Gain - {target['name']} (Filmler)",
                        "poster": poster,
                        "profile_id": target['profile_id']
                    })

        print(f"   ✅ '{target['name']}' kategorisinden toplam {len(contents)} benzersiz video kuyruğa alındı.")
        return contents

    except Exception as e:
        print(f"🔥 Kritik Hata: {e}")
        return []

def get_stream_url(content):
    """
    Video ID'si ile oynatma linkini (MPD/HLS) alır.
    """
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

def save_m3u(data, filename="fanatik_gain_full.m3u"):
    print(f"\n📺 M3U Dosyası Yazılıyor: {filename}...")
    with open(filename, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for item in data:
            # Grup ismini düzenle
            group = item.get("group", "Gain Genel")
            title = item.get("title", "Bilinmeyen İçerik")
            poster = item.get("poster", "")
            url = item.get("stream_url", "")
            
            f.write(f'#EXTINF:-1 group-title="{group}" tvg-logo="{poster}", {title}\n')
            f.write('#EXTVLCOPT:http-user-agent=Mozilla/5.0\n')
            f.write(f"{url}\n")
    print("✅ M3U Hazır! İyi seyirler.")

def main():
    if "eyJ" not in MANUAL_TOKEN:
        print("⛔ Lütfen geçerli bir TOKEN girin!")
        return

    all_videos = []
    
    # Tüm kategorileri gez
    for target in TARGETS:
        items = get_contents(target)
        all_videos.extend(items)
        time.sleep(1) # Kategoriler arası bekleme

    total = len(all_videos)
    if total == 0:
        print("\n⛔ HİÇ İÇERİK BULUNAMADI. Token süresi dolmuş veya hatalı olabilir.")
        return

    print(f"\n🚀 TOPLAM {total} VİDEO İÇİN LİNKLER ÜRETİLİYOR (Biraz sürebilir)...")

    final_list = []
    # Linkleri tek tek çöz
    for i, video in enumerate(all_videos):
        full_data = get_stream_url(video)
        if full_data:
            # Gereksiz datayı temizle
            if "profile_id" in full_data: del full_data["profile_id"]
            final_list.append(full_data)
        
        # İlerleme çubuğu
        if (i+1) % 50 == 0: 
            print(f"   👍 {i+1}/{total} işlendi...")
        
        # API Limitine takılmamak için çok kısa bekleme
        time.sleep(0.02)

    # JSON Yedeği
    with open("gain_archive_full.json", "w", encoding="utf-8") as f:
        json.dump(final_list, f, indent=4, ensure_ascii=False)

    # M3U Oluştur
    save_m3u(final_list)
    print(f"\n🏁 İŞLEM TAMAM! Toplam {len(final_list)} içerik listeye eklendi.")

if __name__ == "__main__":
    main()
