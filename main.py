import requests
import json
import time

# --- TOKEN (GÜNCEL TOKEN'I BURAYA YAPIŞTIR) ---
MANUAL_TOKEN = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJwcm9qZWN0SWQiOiIyZGE3a2Y4amYiLCJpZGVudGl0eSI6ImVuZHVzZXIiLCJhbm9ueW1vdXMiOmZhbHNlLCJ1c2VySWQiOiJlNGMzYWY2Yi05YWQyLTQ3NDYtYTVlNC0yNGQ1ODQyNjZmYzMiLCJjbGFpbXMiOnsiZnVsbE5hbWUiOiJNZXJ0IFNlcmthbiIsInByb2ZpbGVJZCI6ImU0YzNhZjZiLTlhZDItNDc0Ni1hNWU0LTI0ZDU4NDI2NmZjMyIsInN0YXR1cyI6IkFDVElWRSJ9LCJzZXNzaW9uSWQiOiI0YWYzODNjZGM2ZmY0MGQ1ODcwNjMyM2M3ZDU2MDMxYSIsImlhdCI6MTc2OTE4NDM3OCwiZXhwIjoxNzcxNzc2Mzc4fQ.gKxehjzWnPQNzfr8ZbnhoQ3NPjqkRIoZYiMzK3QRs1dhXMRUGdIq8Fgi5BlChASeL6sxo-BE2bh7ZjxNu_RDI6aLpbMrIFNXbZAOdY0cRyrU_TEfRdEVceM9z_DoHkHNVVYhiAOled05dBVVZuspuHFLHd-KSB-S5etuLaXYZ6qYzopnAf-23MaHzatn8sUqS3E5ZKTqj5fUQqLbs8nM00R7StNBiPefXmnj2JCFirC9_ZdSUTA1UkES7GR078nPBfrK8wp3xSNhwUs-Z-lWzj4wUaBpLheL3IplSKNcysz5TKjo_kHrrWUjapf5jD3LrCWZLo90_Ucj1RV0CzAZqQ"

# --- AYARLAR ---
PROJECT_ID = "2da7kf8jf"
ADULT_PROFILE_ID = "URCMQDLDLXJLHLPFBAN0ZI9V"
KIDS_PROFILE_ID = "KIBPFC0Q9Z08Q1UMMJTO61NI"

# Taranacak Kategoriler (ANA SAYFA EKLENDİ)
TARGETS = [
    # HTML Analizine göre Ana Sayfa (Keşfet) rotası /kesfet şeklindedir.
    {"name": "Keşfet (Ana Sayfa)", "profile_id": ADULT_PROFILE_ID, "param": "slug=%2Fkesfet"},
    {"name": "Film", "profile_id": ADULT_PROFILE_ID, "param": "slug=%2Ffilm"},
    {"name": "Dizi", "profile_id": ADULT_PROFILE_ID, "param": "slug=%2Fdizi"},
    {"name": "Program", "profile_id": ADULT_PROFILE_ID, "param": "slug=%2Fprogram"},
    {"name": "Belgesel", "profile_id": ADULT_PROFILE_ID, "param": "slug=%2Fbelgesel"}, # Genelde ayrı olabilir, ekledim.
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
    # pagination size artırıldı
    url = f"{BASE_API}/getProfileSeason/{profile_id}?seasonId={season_id}&titleId={title_id}&__culture=tr-tr&pageSize=100"
    try:
        res = requests.get(url, headers=HEADERS)
        if res.status_code == 200:
            return res.json().get("episodes", [])
    except:
        pass
    return []

def get_contents(target):
    """Kategoriyi tarar (Filtresiz Mod + Slider Desteği)"""
    # pageSize=500 ekleyerek slider içindeki tüm içerikleri almaya zorluyoruz
    url = f"{BASE_API}/getPlaylistsByCategory/{target['profile_id']}?{target['param']}&__culture=tr-tr&pageSize=500"
    print(f"\n🌍 '{target['name']}' taranıyor...")

    contents = []
    # processed_ids global kümede tutulmalı ki sayfalar arası tekrar olmasın,
    # ancak fonksiyon yapısı gereği burada liste bazlı dönüyoruz. 
    # Duplicate kontrolü main fonksiyonunda veya burada set ile yapılabilir.
    
    try:
        res = requests.get(url, headers=HEADERS)
        if res.status_code != 200:
            print(f"   ❌ Erişim Hatası ({target['name']}): {res.status_code}")
            return []

        playlists = res.json().get("playlists", [])
        print(f"   📦 {len(playlists)} adet raf/slider bulundu. Analiz ediliyor...")

        for playlist in playlists:
            # Slider başlığını al (örn: "Yeni Çıkanlar", "Popüler Diziler")
            playlist_name = playlist.get("name", "Genel")
            
            items = playlist.get("items", [])
            print(f"      👉 Raf: {playlist_name} ({len(items)} içerik)")

            for item in items:
                title_id = item.get("titleId")
                video_id = item.get("videoContentId")
                name = item.get("name") or item.get("title")
                poster = item.get("logoImageUrl") or item.get("posterImageUrl")
                seasons = item.get("seasons", [])
                
                # İçerik Tipi Belirleme ve İşleme
                
                # 1. TİP: DİZİ (Sezon bilgisi varsa)
                if seasons:
                    # Dizi olduğu için loglayalım ama detayları sonra çekeceğiz
                    for season in seasons:
                        episodes = get_episodes(title_id, season.get("id"), target['profile_id'])
                        for ep in episodes:
                            # Bölüm adını ve numarasını düzgün formatla
                            ep_num = ep.get('episode', 0)
                            season_num = ep.get('season', 1) # API'den geliyorsa al, yoksa 1
                            ep_name = ep.get('name', '')
                            
                            full_title = f"{name} - S{season_num}B{ep_num} - {ep_name}"
                            
                            contents.append({
                                "id": ep.get("videoContentId"),
                                "title_id": title_id, # Tekrar kontrolü için
                                "title": full_title,
                                "group": f"Gain Dizi - {name}", 
                                "poster": poster,
                                "profile_id": target['profile_id']
                            })

                # 2. TİP: FİLM veya TEK BÖLÜMLÜK İÇERİK
                elif video_id:
                    group_name = "Gain Film" if target['name'] == "Film" else f"Gain {target['name']}"
                    # Eğer slider içinden geldiyse ve kategori belliyse onu kullan
                    if "Film" in playlist_name: group_name = "Gain Film"
                    if "Belgesel" in playlist_name: group_name = "Gain Belgesel"

                    contents.append({
                        "id": video_id,
                        "title_id": title_id, # Tekrar kontrolü için
                        "title": name,
                        "group": group_name,
                        "poster": poster,
                        "profile_id": target['profile_id']
                    })

        print(f"   ✅ '{target['name']}' tamamlandı. Toplam bulunan aday: {len(contents)}")
        return contents

    except Exception as e:
        print(f"🔥 Hata: {e}")
        return []

def get_stream_url(content):
    """Videoların gerçek izleme linkini (MPD/HLS) çeker"""
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

    all_raw_items = []
    
    # Tüm kategorileri gez
    for target in TARGETS:
        items = get_contents(target)
        all_raw_items.extend(items)
        time.sleep(1) # API spam engellemek için bekleme

    # --- TEKRAR EDEN İÇERİKLERİ TEMİZLE ---
    # Aynı içerik hem "Keşfet" hem "Film" altında gelebilir.
    # ID'ye göre benzersizleştirme yapıyoruz.
    unique_items = {}
    print("\n🧹 Tekrar eden içerikler temizleniyor...")
    for item in all_raw_items:
        # Anahtar olarak video ID kullanıyoruz
        unique_id = item['id']
        if unique_id not in unique_items:
            unique_items[unique_id] = item
    
    final_processing_list = list(unique_items.values())
    total = len(final_processing_list)
    
    if total == 0:
        print("\n⛔ HİÇ İÇERİK YOK. Token süresi dolmuş olabilir.")
        return

    print(f"\n🚀 TOPLAM {total} BENZERSİZ İÇERİK İÇİN LİNKLER ÇEKİLİYOR...")

    ready_list = []
    for i, video in enumerate(final_processing_list):
        full_data = get_stream_url(video)
        if full_data:
            # Gereksiz alanları temizle
            if "profile_id" in full_data: del full_data["profile_id"]
            if "title_id" in full_data: del full_data["title_id"]
            
            ready_list.append(full_data)
            
            # İlerleme çubuğu benzeri çıktı
            percent = (i + 1) / total * 100
            if (i+1) % 5 == 0 or (i+1) == total:
                print(f"   👍 %{percent:.1f} tamamlandı ({i+1}/{total}) - {full_data['title']}")
        
        time.sleep(0.05)

    # JSON Kaydet
    with open("gain_full_archive.json", "w", encoding="utf-8") as f:
        json.dump(ready_list, f, indent=4, ensure_ascii=False)

    # M3U Kaydet
    save_m3u(ready_list)
    print("\n🏁 MUTLU SON! Dosyalar hazır.")

if __name__ == "__main__":
    main()
