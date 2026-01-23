import requests
import json
import re
import time

# --- TOKEN (Taze token yapıştır) ---
MANUAL_TOKEN = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJwcm9qZWN0SWQiOiIyZGE3a2Y4amYiLCJpZGVudGl0eSI6ImVuZHVzZXIiLCJhbm9ueW1vdXMiOmZhbHNlLCJ1c2VySWQiOiJlNGMzYWY2Yi05YWQyLTQ3NDYtYTVlNC0yNGQ1ODQyNjZmYzMiLCJjbGFpbXMiOnsiZW1haWwiOiJmYXRtYW51cnJrcmttenoxODZAZ21haWwuY29tIiwiZnVsbE5hbWUiOiJwaXJ0aXN0YW4iLCJwcm9maWxlSWQiOiJVUkNNUURMRExYSkxITFBGQkFOMFpJOVYiLCJwcm9maWxlQXZhdGFyIjoiUCIsImlzS2lkUHJvZmlsZSI6ZmFsc2V9LCJzZXNzaW9uSWQiOiJkMzdhMjlkMTMwOGE0NmRmOTA1NzQzZjg4ODdjZDliNiIsImlhdCI6MTc2OTE4NjUzMywiZXhwIjoxNzcxNzc4NTMzfQ.ci3CbqGQHVgUFIPs2PH_tR7CUTzN4HoKu3LY3zpFQztXlqZVgo_kXqp9A-6Pdn0G_R_BDtNC-sWS9eRzgka0KzlP228BGmZ87N_0wpxg1riHierd5LKIMZFNOJw-LkdQ3sFTWhGvD0zJm-lYYunh2gxtoWJXGVyuQYQSlt4xrPEMneUDbw-d0D2nVeJu_WVfkOPMFEC6bEmuFVIHgD6usMkd2_e9sr7mkt7GXwVBGuFJb9dK1p1nWb-KKXN7oIvf-eaxCbtAJ27Lja_NI-YlA8QjvwVsqnmf7qNuJpjJtorPSDvUcR6gp8oiZmzCw8zwJXoB79Xkmxlr0jnxDrTtIQ"

# --- SABİTLER ---
PROJECT_ID = "2da7kf8jf"
PROFILE_ID = "URCMQDLDLXJLHLPFBAN0ZI9V" 

# HEADER (Tarayıcı gibi davranacağız)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "x-gain-platform": "web",
    "Origin": "https://www.gain.tv",
    "Referer": "https://www.gain.tv/"
}

def find_real_id_from_html(slug):
    """
    1. Adım: Video sayfasına (HTML) gidip kaynak kodunu indirir.
    2. Adım: Kaynak kodunun içinde gizli olan 'Gerçek ID'yi (GUID) bulur.
    """
    page_url = f"https://www.gain.tv/watch/{slug}"
    print(f"🌍 Sayfa Kaynağına Gidiliyor: {page_url}")
    
    # HTML isteği atıyoruz (Token'ı cookie veya header olarak ekleyelim garanti olsun)
    headers = HEADERS.copy()
    headers["Authorization"] = f"Bearer {MANUAL_TOKEN}"
    
    try:
        response = requests.get(page_url, headers=headers)
        if response.status_code == 200:
            html_content = response.text
            
            # --- DEDEKTİF KISMI: REGEX İLE ID ARAMA ---
            # Kaynak kodunda genellikle "contentId":"..." veya "id":"..." şeklinde geçer
            # GUID formatı: 8-4-4-4-12 karakterli (ör: 12345678-1234-1234-1234-1234567890ab)
            
            # 1. Deneme: contentId araması
            match = re.search(r'"contentId":"([a-f0-9-]{36})"', html_content)
            
            # 2. Deneme: id araması (daha genel)
            if not match:
                match = re.search(r'"id":"([a-f0-9-]{36})"', html_content)
            
            if match:
                real_id = match.group(1)
                print(f"🎉 GİZLİ ID BULUNDU: {real_id}")
                return real_id
            else:
                print("⚠️ Kaynak kodunda ID deseni bulunamadı.")
                # Belki de HTML'in bir kısmını ekrana basıp bakmak gerekir
                print(f"HTML Başlangıcı: {html_content[:500]}") 
                return None
        else:
            print(f"❌ Sayfa Açılamadı. Kod: {response.status_code}")
            return None
    except Exception as e:
        print(f"🔥 HTML Hatası: {e}")
        return None

def get_stream_url(real_id):
    """Gerçek ID'yi kullanarak API'den yayın linkini alır"""
    playback_url = f"https://api.gain.tv/{PROJECT_ID}/CALL/ProfileTitle/getPlaybackInfo/{PROFILE_ID}/"
    
    params = {
        "videoContentId": real_id, # Artık burası DOĞRU ID olacak
        "packageType": "Dash",
        "__culture": "tr-tr"
    }
    
    auth_headers = HEADERS.copy()
    auth_headers["Authorization"] = f"Bearer {MANUAL_TOKEN}"
    
    try:
        print(f"📡 API'ye soruluyor (ID: {real_id})...")
        response = requests.get(playback_url, headers=auth_headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("Success"):
                result = data.get("Result", {})
                stream_url = result.get("Url")
                license_url = result.get("LicenseUrl")
                
                print(f"✅✅ YAYIN LİNKİ ALINDI!")
                print(f"   🔗 LINK: {stream_url}")
                if license_url:
                    print(f"   🔑 LICENSE: {license_url}")
                return result
            else:
                print(f"❌ API Reddedildi: {data.get('Message')}")
                return None
        else:
            print(f"❌ HTTP Hatası: {response.status_code}")
            return None
    except Exception as e:
        print(f"🔥 API Hatası: {e}")
        return None

def main():
    if "BURAYA" in MANUAL_TOKEN:
        print("⛔ Token'ı güncellemeyi unutma!")
        return

    # Tarayıcıdaki Kısa Link (Slug)
    target_slug = "B294FGF3xvkT" 
    
    all_data = []

    # 1. Adım: Kaynak kodundan Gerçek ID'yi bul
    real_id = find_real_id_from_html(target_slug)
    
    # 2. Adım: Yayın linkini çek
    if real_id:
        data = get_stream_url(real_id)
        if data:
            all_data.append(data)

    print("\n💾 gain_data.json dosyası kaydediliyor...")
    with open("gain_data.json", "w", encoding="utf-8") as f:
        json.dump(all_data, f, indent=4, ensure_ascii=False)
    print("🏁 İşlem tamam.")

if __name__ == "__main__":
    main()
