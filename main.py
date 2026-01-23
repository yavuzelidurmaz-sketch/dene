import requests
import json
import time

# --- 1. ADIM: TARAYICIDAN ALDIĞIN TOKEN'I BURAYA YAPIŞTIR ---
# Token süresi dolduysa tarayıcıdan (F12 > Network) yenisini kopyala.
MANUAL_TOKEN = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJwcm9qZWN0SWQiOiIyZGE3a2Y4amYiLCJpZGVudGl0eSI6ImVuZHVzZXIiLCJhbm9ueW1vdXMiOmZhbHNlLCJ1c2VySWQiOiJlNGMzYWY2Yi05YWQyLTQ3NDYtYTVlNC0yNGQ1ODQyNjZmYzMiLCJjbGFpbXMiOnsiZW1haWwiOiJmYXRtYW51cnJrcmttenoxODZAZ21haWwuY29tIiwiZnVsbE5hbWUiOiJwaXJ0aXN0YW4iLCJwcm9maWxlSWQiOiJVUkNNUURMRExYSkxITFBGQkFOMFpJOVYiLCJwcm9maWxlQXZhdGFyIjoiUCIsImlzS2lkUHJvZmlsZSI6ZmFsc2V9LCJzZXNzaW9uSWQiOiJkMzdhMjlkMTMwOGE0NmRmOTA1NzQzZjg4ODdjZDliNiIsImlhdCI6MTc2OTE4NjUzMywiZXhwIjoxNzcxNzc4NTMzfQ.ci3CbqGQHVgUFIPs2PH_tR7CUTzN4HoKu3LY3zpFQztXlqZVgo_kXqp9A-6Pdn0G_R_BDtNC-sWS9eRzgka0KzlP228BGmZ87N_0wpxg1riHierd5LKIMZFNOJw-LkdQ3sFTWhGvD0zJm-lYYunh2gxtoWJXGVyuQYQSlt4xrPEMneUDbw-d0D2nVeJu_WVfkOPMFEC6bEmuFVIHgD6usMkd2_e9sr7mkt7GXwVBGuFJb9dK1p1nWb-KKXN7oIvf-eaxCbtAJ27Lja_NI-YlA8QjvwVsqnmf7qNuJpjJtorPSDvUcR6gp8oiZmzCw8zwJXoB79Xkmxlr0jnxDrTtIQ"

# --- URL'DEN BULDUĞUMUZ SABİTLER ---
PROJECT_ID = "2da7kf8jf"
PROFILE_ID = "URCMQDLDLXJLHLPFBAN0ZI9V" 

# 1. TÜM FİLMLERİ LİSTELEYEN URL (Senin Bulduğun)
CATEGORY_URL = f"https://api.gain.tv/{PROJECT_ID}/CALL/ProfileTitle/getPlaylistsByCategory/{PROFILE_ID}?slug=%2Ffilm&__culture=tr-tr"

# 2. TEKİL FİLM YAYININI ÇEKEN URL
PLAYBACK_URL_TEMPLATE = f"https://api.gain.tv/{PROJECT_ID}/CALL/ProfileTitle/getPlaybackInfo/{PROFILE_ID}/"

# HEADER (Tarayıcı Taklidi)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Content-Type": "application/json",
    "Accept": "application/json",
    "x-gain-platform": "web",
    "Origin": "https://www.gain.tv",
    "Referer": "https://www.gain.tv/"
}

def get_all_movies_from_category():
    """Film sayfasındaki tüm kategorileri ve içindeki filmleri bulur"""
    auth_headers = HEADERS.copy()
    auth_headers["Authorization"] = f"Bearer {MANUAL_TOKEN}"
    
    print(f"🌍 Tüm film listesi indiriliyor...")
    
    try:
        response = requests.get(CATEGORY_URL, headers=auth_headers)
        
        if response.status_code != 200:
            print(f"❌ Liste alınamadı! Hata Kodu: {response.status_code}")
            return []

        data = response.json()
        if not data.get("Success"):
            print(f"❌ API Hatası: {data.get('Message')}")
            return []

        # Gain yapısında filmler "Widgets" içinde durur
        widgets = data.get("Result", {}).get("Widgets", [])
        
        movie_list = []
        processed_ids = set() # Aynı filmi iki kere kaydetmemek için

        print(f"📦 {len(widgets)} farklı kategori bulundu. İçerikler ayıklanıyor...")

        for widget in widgets:
            category_name = widget.get("Title", "Diğer")
            assets = widget.get("Assets", [])
            
            for asset in assets:
                movie_id = asset.get("Id")
                title = asset.get("Title")
                
                # Sadece film olanları al (Dizileri atlayabiliriz veya dahil edebiliriz)
                if movie_id and movie_id not in processed_ids:
                    # Poster resmini bulmaya çalışalım
                    images = asset.get("Images", [])
                    poster = images[0].get("Url") if images else None

                    movie_list.append({
                        "id": movie_id,
                        "title": title,
                        "category": category_name,
                        "poster": poster
                    })
                    processed_ids.add(movie_id)
        
        print(f"✅ Toplam {len(movie_list)} adet benzersiz film bulundu!")
        return movie_list

    except Exception as e:
        print(f"🔥 Liste Hatası: {e}")
        return []

def get_stream_url(movie):
    """Bulunan her film için yayın linkini çeker"""
    params = {
        "videoContentId": movie["id"], 
        "packageType": "Dash",
        "__culture": "tr-tr"
    }
    
    auth_headers = HEADERS.copy()
    auth_headers["Authorization"] = f"Bearer {MANUAL_TOKEN}"
    
    try:
        # print(f"   📡 {movie['title']} için link çekiliyor...") 
        response = requests.get(PLAYBACK_URL_TEMPLATE, headers=auth_headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("Success"):
                result = data.get("Result", {})
                
                # Film nesnesine linkleri ekle
                movie["stream_url"] = result.get("Url")
                movie["license_url"] = result.get("LicenseUrl")
                
                return movie
            else:
                return None # API hatası (Yetki yok vs.)
        else:
            return None # HTTP hatası
    except Exception:
        return None

def main():
    if "BURAYA" in MANUAL_TOKEN:
        print("⛔ Lütfen Token'ı girmeyi unutma! Kodun başındaki MANUAL_TOKEN kısmını düzenle.")
        return

    # 1. ADIM: Listeyi Çek
    all_movies = get_all_movies_from_category()
    
    if not all_movies:
        print("⚠️ Hiç film bulunamadı. Token süresi dolmuş olabilir.")
        # Yine de boş dosya oluştur ki GitHub hata vermesin
        with open("gain_movies.json", "w", encoding="utf-8") as f:
            f.write("[]")
        return

    # 2. ADIM: Detayları Çek (Sınır koymuyorum, hepsini çekecek)
    print(f"\n🚀 {len(all_movies)} film için yayın linkleri toplanıyor...")
    print("   (Bu işlem film sayısına göre 1-2 dakika sürebilir, lütfen bekle...)")
    
    final_list = []
    
    for i, movie in enumerate(all_movies): 
        full_movie_data = get_stream_url(movie)
        
        if full_movie_data:
            final_list.append(full_movie_data)
        
        # Her 20 filmde bir durum güncellemesi yap
        if (i + 1) % 20 == 0:
            print(f"   👍 {i + 1} film tarandı... ({len(final_list)} başarılı)")
        
        # Sunucuyu yormamak için çok kısa bekleme
        time.sleep(0.1)

    # 3. ADIM: Kaydet
    print(f"\n💾 {len(final_list)} film başarıyla 'gain_movies.json' dosyasına kaydediliyor...")
    with open("gain_movies.json", "w", encoding="utf-8") as f:
        json.dump(final_list, f, indent=4, ensure_ascii=False)
    print("🏁 İŞLEM TAMAMLANDI! Dosyayı indirebilirsin.")

if __name__ == "__main__":
    main()
