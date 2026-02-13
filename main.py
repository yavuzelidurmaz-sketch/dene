import requests
import json
import time

# --- TOKEN (GÜNCEL TOKEN) ---
MANUAL_TOKEN = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJwcm9qZWN0SWQiOiIyZGE3a2Y4amYiLCJpZGVudGl0eSI6ImVuZHVzZXIiLCJhbm9ueW1vdXMiOmZhbHNlLCJ1c2VySWQiOiJkYzdlYzJhMC00NGNkLTQ5MGItOWI3ZS04ZTA2MDU2NGZhZTQiLCJjbGFpbXMiOnsiZnVsbE5hbWUiOiJBTMSwIFZBUk9MIiwicHJvZmlsZUlkIjoiZGM3ZWMyYTAtNDRjZC00OTBiLTliN2UtOGUwNjA1NjRmYWU0Iiwic3RhdHVzIjoiQUNUSVZFIn0sImlhdCI6MTc3MTAwOTAwMywiZXhwIjoxNzcxMDA5MzAzfQ.gUZb_BoGQgW3jlxXY0SvlVasAfEccdEGwrvqWwOfvYTJui20fLyu-AJfFbtwHRZUiKdbmHW6ZPrh4XStoQZvLr-J5ZijlsPTgGmRTCth4h5kCHvdVd2PWJLSK3I_fI7p-g2UY3P0vGZF6YTJhFTxbVJPSq0UlznZh2LwuH6hIniMmasJuZZeLLAabRs4QqRxnCZw1vJOfcJ3coCM6hanRcHtRZ_CoKM5aHpZdEhbkmqhps6f5NVmD7DxSUra1plZY0I7uOb9W3S7OK_la-hRr6wn9_girBhDMRYh8Ar1QzxOzm2aGlOHvaDMdh4LCKGSNIlhjTrIVPZuLj6kkcMMrA"

# --- AYARLAR ---
PROJECT_ID = "2da7kf8jf"
ADULT_PROFILE_ID = "URCMQDLDLXJLHLPFBAN0ZI9V"

# TARANACAK URL LISTESI (Verdiğin liste)
URL_LIST = [
    "https://www.gain.tv/title/hQyof14IbdNcTVu7OHLWoZCJ",
    "https://www.gain.tv/title/Tr2oTwNq",
    "https://www.gain.tv/title/L30ikc4W",
    "https://www.gain.tv/title/sP8PhTv8",
    "https://www.gain.tv/title/hdcl7L1y",
    "https://www.gain.tv/title/FurEqHws",
    "https://www.gain.tv/title/FurEqHws",
    "https://www.gain.tv/title/JCr0yrdY",
    "https://www.gain.tv/title/zdhHLHvv",
    "https://www.gain.tv/title/zdhHLHvv",
    "https://www.gain.tv/title/kjintH1d",
    "https://www.gain.tv/title/4SRrLDKa",
    "https://www.gain.tv/title/Xlvm5KTq",
    "https://www.gain.tv/title/GlYFMatd",
    "https://www.gain.tv/title/9NDpuuIE",
    "https://www.gain.tv/title/8xufVpt8",
    "https://www.gain.tv/title/6QzqkQmn",
    "https://www.gain.tv/title/wGPdXzFW",
    "https://www.gain.tv/title/KaGnXMiH",
    "https://www.gain.tv/title/2Hy4HDcLkFA74dqSuM47MP4X",
    "https://www.gain.tv/title/9e2mRuUzROpGg4V2pzt4uLoo",
    "https://www.gain.tv/title/22NHt7Wf",
    "https://www.gain.tv/title/hQyof14IbdNcTVu7OHLWoZCJ",
    "https://www.gain.tv/title/LPjAC8bM",
    "https://www.gain.tv/title/znmprjTj",
    "https://www.gain.tv/title/FurEqHws",
    "https://www.gain.tv/title/zdhHLHvv",
    "https://www.gain.tv/title/IbGkpsOA",
    "https://www.gain.tv/title/m49BOba5",
    "https://www.gain.tv/title/9p8vaJNC",
    "https://www.gain.tv/title/tofWGvScsrPFvGjdVQ6Tb67Z",
    "https://www.gain.tv/title/DlTasVLf1M5doUtov8BsIhH6",
    "https://www.gain.tv/title/VWDX8Hu2",
    "https://www.gain.tv/title/KSz7HGMt",
    "https://www.gain.tv/title/4xwIWjLOXVYLiFCCDy1pCnPz",
    "https://www.gain.tv/title/8xufVpt8",
    "https://www.gain.tv/title/VPAA4SmX",
    "https://www.gain.tv/title/s75PDkfD",
    "https://www.gain.tv/title/uH0K3YdI",
    "https://www.gain.tv/title/Xlvm5KTq",
    "https://www.gain.tv/title/uH0K3YdI",
    "https://www.gain.tv/title/m49BOba5",
    "https://www.gain.tv/title/8C6daVaPSC0Jf74c4R7KHEhC",
    "https://www.gain.tv/title/t6Ow4GiBwqMpw25qKZTNhx7A",
    "https://www.gain.tv/title/DlTasVLf1M5doUtov8BsIhH6",
    "https://www.gain.tv/title/GHX0qJlD",
    "https://www.gain.tv/title/hdcl7L1y",
    "https://www.gain.tv/title/zuW1GmfLF0aUCkAPQ40B26lb",
    "https://www.gain.tv/title/9e2mRuUzROpGg4V2pzt4uLoo",
    "https://www.gain.tv/title/dUnSGXekpKVREw448WFS2WCr",
    "https://www.gain.tv/title/dUnSGXekpKVREw448WFS2WCr",
    "https://www.gain.tv/title/G3VUoD3Jwvwtj8dUlTavmXIT",
    "https://www.gain.tv/title/NBcdBeKm",
    "https://www.gain.tv/title/hQyof14IbdNcTVu7OHLWoZCJ",
    "https://www.gain.tv/title/gu1x8JboSWYIEiWPZhznzOTo",
    "https://www.gain.tv/title/rjpJdKTfbCGtCCdavQAEK4vz",
    "https://www.gain.tv/title/4SRrLDKa",
    "https://www.gain.tv/title/FurEqHws",
    "https://www.gain.tv/title/cEmPxIrG",
    "https://www.gain.tv/title/8xufVpt8",
    "https://www.gain.tv/title/KApOnQZo",
    "https://www.gain.tv/title/h2PlvJAU",
    "https://www.gain.tv/title/JCr0yrdY",
    "https://www.gain.tv/title/U8H6C4YE",
    "https://www.gain.tv/title/VWDX8Hu2",
    "Https://www.gain.tv/title/hQyof14IbdNcTVu7OHLWoZCJ",
    "https://www.gain.tv/title/zdhHLHvv"
]

BASE_API = f"https://api.gain.tv/{PROJECT_ID}/CALL"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Content-Type": "application/json",
    "Authorization": f"Bearer {MANUAL_TOKEN}",
    "x-gain-platform": "web"
}

def extract_id(url):
    """URL'den ID'yi ayıklar (son slash sonrasını alır)"""
    url = url.strip()
    if not url: return None
    # Link sonundaki ID'yi al
    return url.split("/")[-1]

def get_episodes(title_id, season_id, profile_id):
    """Sezon içindeki bölümleri çeker"""
    url = f"{BASE_API}/ProfileTitle/getProfileSeason/{profile_id}?seasonId={season_id}&titleId={title_id}&__culture=tr-tr&pageSize=100"
    try:
        res = requests.get(url, headers=HEADERS)
        if res.status_code == 200:
            return res.json().get("episodes", [])
    except:
        pass
    return []

def process_specific_title(title_id):
    """Verilen Title ID için dizi/film ayrımı yapıp içerikleri döner"""
    url = f"{BASE_API}/ProfileTitle/getProfileTitle/{ADULT_PROFILE_ID}?titleId={title_id}&__culture=tr-tr"
    
    found_contents = []
    
    try:
        res = requests.get(url, headers=HEADERS)
        if res.status_code != 200:
            print(f"❌ Hata (ID: {title_id}): {res.status_code}")
            return []
        
        data = res.json()
        title_name = data.get("title") or data.get("name")
        poster = data.get("posterImageUrl") or data.get("logoImageUrl")
        seasons = data.get("seasons", [])
        
        # 1. TİP: DİZİ (Sezonları var)
        if seasons:
            print(f"   🎬 Dizi Bulundu: {title_name} ({len(seasons)} Sezon)")
            for season in seasons:
                s_num = season.get("season")
                print(f"      -> Sezon {s_num} bölümleri çekiliyor...")
                episodes = get_episodes(title_id, season.get("id"), ADULT_PROFILE_ID)
                
                for ep in episodes:
                    ep_num = ep.get('episode', 0)
                    ep_name = ep.get('name', '')
                    full_title = f"{title_name} - S{s_num}B{ep_num} - {ep_name}"
                    
                    found_contents.append({
                        "id": ep.get("videoContentId"),
                        "title": full_title,
                        "group": f"Gain Dizi - {title_name}",
                        "poster": poster
                    })
                    
        # 2. TİP: FİLM veya TEK VİDEO
        else:
            # Bazen videoContentId en dışta, bazen currentVideoContent içinde olabilir
            video_id = data.get("videoContentId")
            if not video_id and data.get("currentVideoContent"):
                video_id = data.get("currentVideoContent", {}).get("id")
            
            if video_id:
                print(f"   🎥 Film/Video Bulundu: {title_name}")
                found_contents.append({
                    "id": video_id,
                    "title": title_name,
                    "group": "Gain Film/Belgesel",
                    "poster": poster
                })
            else:
                print(f"   ⚠️ İçerik tipi belirlenemedi veya oynatılabilir video yok: {title_name}")

    except Exception as e:
        print(f"🔥 Hata (ID: {title_id}): {e}")
    
    return found_contents

def get_stream_url(content):
    """Videoların gerçek izleme linkini (MPD/HLS) çeker"""
    url = f"{BASE_API}/ProfileTitle/getPlaybackInfo/{ADULT_PROFILE_ID}/"
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

def save_m3u(data, filename="ozel_liste_gain.m3u"):
    print(f"\n📺 M3U oluşturuluyor: {filename}...")
    with open(filename, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for item in data:
            # Güvenli string işlemi
            title = item.get("title", "Bilinmeyen İçerik").replace('"', '')
            group = item.get("group", "Gain").replace('"', '')
            poster = item.get("poster", "")
            
            f.write(f'#EXTINF:-1 group-title="{group}" tvg-logo="{poster}", {title}\n')
            f.write('#EXTVLCOPT:http-user-agent=Mozilla/5.0\n')
            f.write(f"{item.get('stream_url', '')}\n")
    print("✅ M3U Dosyası Hazır!")

def main():
    if "BURAYA" in MANUAL_TOKEN:
        print("⛔ Token girmeyi unutma!")
        return

    # 1. URL Listesini Temizle ve ID'leri Çıkar (Tekrarları önlemek için Set kullanılır)
    unique_ids = set()
    for link in URL_LIST:
        tid = extract_id(link)
        if tid:
            unique_ids.add(tid)
    
    print(f"📋 Listede {len(URL_LIST)} link vardı.")
    print(f"✨ Tekrarlar temizlendi, taranacak benzersiz içerik sayısı: {len(unique_ids)}")
    print("-" * 50)

    # 2. Her bir ID için detayları çek
    all_ready_contents = []
    
    for i, title_id in enumerate(unique_ids):
        print(f"🔍 İşleniyor ({i+1}/{len(unique_ids)}): {title_id}")
        contents = process_specific_title(title_id)
        
        # Stream URL'lerini al
        for content in contents:
            stream_data = get_stream_url(content)
            if stream_data:
                all_ready_contents.append(stream_data)
        
        time.sleep(0.5) # API ban yememek için kısa bekleme

    if not all_ready_contents:
        print("\n⛔ Hiçbir içerik için link alınamadı. Token süresi dolmuş olabilir.")
        return

    # 3. Sonuçları Kaydet
    print(f"\n🚀 Toplam {len(all_ready_contents)} adet oynatılabilir video linki bulundu.")
    
    # JSON Kaydet
    with open("gain_ozel_liste.json", "w", encoding="utf-8") as f:
        json.dump(all_ready_contents, f, indent=4, ensure_ascii=False)

    # M3U Kaydet
    save_m3u(all_ready_contents)
    print("\n🏁 İŞLEM TAMAMLANDI. 'ozel_liste_gain.m3u' dosyasını kontrol et.")

if __name__ == "__main__":
    main()
