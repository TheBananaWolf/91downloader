import os
import sys
import time
import requests
import urllib3
import threading
import stat

# Suppress SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

# --- Configuration ---
def get_base_path():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))

BASE_PATH = get_base_path()
DOWNLOAD_PATH = os.path.join(BASE_PATH, '91_Videos')

if not os.path.exists(DOWNLOAD_PATH):
    os.makedirs(DOWNLOAD_PATH)

def download_process(page_url):
    print("\n[1/3] Starting automation engine...")
    
    driver = None
    try:
        mobile_emulation = { "deviceName": "iPhone X" }
        chrome_options = Options()
        chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)
        # Security arguments to prevent crashes
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument('--ignore-ssl-errors')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        # --- FIXED DRIVER INSTALLATION ---
        print("[Info] Installing Chrome Driver...")
        driver_path = ChromeDriverManager().install()
        
        # BUG FIX: If it selects the 'THIRD_PARTY_NOTICES' text file, force it to use the binary
        if "THIRD_PARTY_NOTICES" in driver_path:
            driver_dir = os.path.dirname(driver_path)
            driver_path = os.path.join(driver_dir, "chromedriver")
            print(f"[Fix] Corrected driver path to: {driver_path}")

        # Ensure the file is executable (Fix for 'Exec format error')
        try:
            st = os.stat(driver_path)
            os.chmod(driver_path, st.st_mode | stat.S_IEXEC)
        except Exception as e:
            print(f"[Warning] Could not set executable permission: {e}")

        service = Service(driver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)
        # ---------------------------------
        
        print(f"[Info] Opening: {page_url}")
        driver.get(page_url)
        
        print("\n" + "="*50)
        print(" ACTION REQUIRED: ")
        print(" Please click PLAY on the video in the Chrome window!")
        print("="*50 + "\n")
        
        video_src = None
        # Wait up to 60 seconds for the user to click play
        for i in range(60): 
            try:
                video_element = driver.find_element(By.TAG_NAME, 'video')
                src = video_element.get_attribute('src')
                
                if src and ("mp4" in src or "m3u8" in src) and not src.startswith("blob:"):
                    video_src = src
                    print(f"\r[Success] Video link found!", end="")
                    break
            except:
                pass
            print(f"\r[Waiting] Checking for video playback... {i}s", end="")
            time.sleep(1)
            
        print("") 
        
        if not video_src:
            raise Exception("Timeout: Did not detect video playing.")

        try:
            title = driver.title.replace("Chinese homemade video", "").replace("- 91 Porn", "").strip()
        except:
            title = "downloaded_video"
        
        safe_title = "".join([c for c in title if c.isalnum() or c in (' ', '-', '_')]).strip()
        if not safe_title: safe_title = f"video_{int(time.time())}"

        driver.quit()
        print(f"[2/3] Preparing download for: {safe_title}")

        # --- Download Logic ---
        final_path = os.path.join(DOWNLOAD_PATH, f"{safe_title}.mp4")
        headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1',
            'Referer': 'https://91porn.com/'
        }

        if ".m3u8" in video_src:
            print("[Info] M3U8 detected, downloading segments...")
            r = requests.get(video_src, headers=headers, verify=False, timeout=10)
            lines = r.text.split('\n')
            ts_urls = [line.strip() for line in lines if line and not line.startswith('#')]
            
            from urllib.parse import urljoin
            ts_urls = [urljoin(video_src, line) for line in ts_urls]
            
            with open(final_path, 'wb') as f: pass
            
            with requests.Session() as session:
                for i, ts in enumerate(ts_urls):
                    sys.stdout.write(f"\r[Downloading] Segment {i+1}/{len(ts_urls)}")
                    sys.stdout.flush()
                    try:
                        res = session.get(ts, headers=headers, verify=False, timeout=10)
                        with open(final_path, 'ab') as f:
                            f.write(res.content)
                    except:
                        pass
        else:
            print("[Info] MP4 detected, downloading directly...")
            with requests.get(video_src, headers=headers, stream=True, verify=False, timeout=30) as r:
                r.raise_for_status()
                total_size = int(r.headers.get('content-length', 0))
                downloaded = 0
                with open(final_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192): 
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            percent = downloaded / total_size * 100
                            sys.stdout.write(f"\r[Downloading] {percent:.1f}%")
                            sys.stdout.flush()

        print(f"\n\n[Done] File saved to:\n{final_path}")
        
    except Exception as e:
        if driver: 
            try: driver.quit()
            except: pass
        print(f"\n[Error] {e}")

if __name__ == "__main__":
    while True:
        print("\n" + "-"*30)
        url = input("Paste Video URL (or 'q' to quit): ").strip()
        if url.lower() == 'q':
            break
        if url:
            download_process(url)