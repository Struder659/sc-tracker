import os
import time
import yt_dlp
import traceback
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config import *



#TARGET_PROFILE_URL = "https://soundcloud.com/youruser/tracks"
#CHECK_INTERVAL = 30
#DOWNLOAD_FOLDER = os.path.join(os.getcwd(), "output")
#ARCHIVE_FILE = os.path.join(os.getcwd(), "archive.txt")
#LOG_FILE = os.path.join(os.getcwd(), "tracker_debug.log")

def log(message, level="INFO", to_file=True, to_console=True, end='\n'):
    now = datetime.now()
    time_console = now.strftime('%H:%M:%S')
    time_file = now.strftime('%Y-%m-%d %H:%M:%S')
    
    console_msg = f"[{time_console}] {message}"
    file_msg = f"[{time_file}] [{level}] {message}\n"

    if to_console:
        print(console_msg, end=end)

    if to_file:
        try:
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(file_msg)
        except Exception:
            pass

def print_ban():
    BANNER = r"""                                               
     _____ _____    _____         _   _             
    |   __|     |  |  _  |___ ___| |_|_|_ _ ___ ___ 
    |__   |   --|  |     |  _|  _|   | | | | -_|  _|
    |_____|_____|  |__|__|_| |___|_|_|_|\_/|___|_|  
        """
    print(BANNER)

def get_latest_track_url(profile_url):
    ydl_opts = {
        'quiet': True,
        'extract_flat': True,  
        'playlistend': 1,     
        'ignoreerrors': True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(profile_url, download=False)
            if 'entries' in info and len(info['entries']) > 0:
                return info['entries'][0]['url']
    except Exception as e:
        log(f"Error getting track list: {e}", level="ERROR")
    return None

def download_with_selenium(sc_url):
    site_url = "https://soundloadmate.com/enA1/"
    os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)
    log(f"--> Start Downloading: {sc_url}")

    options = Options()
    options.add_argument("--headless=new") 
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--log-level=3")
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    options.add_experimental_option("prefs", {
        "download.default_directory": DOWNLOAD_FOLDER,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    })

    driver = webdriver.Chrome(options=options)
    download_success = False

    try:
        driver.get(site_url)
        
        log("Selenium: Input URL...")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "url")))
        driver.find_element(By.ID, "url").send_keys(sc_url)
        time.sleep(0.5)

        driver.execute_script("arguments[0].click();", driver.find_element(By.ID, "send"))

        log("Selenium: Waiting for conversion...")
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.abuttons.mb-0 button.button.is-download')))
        second_btn = driver.find_element(By.CSS_SELECTOR, 'div.abuttons.mb-0 button.button.is-download')
        driver.execute_script("arguments[0].click();", second_btn)

        log("Selenium: Waiting for final link...")
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.abuttons a.button.is-download.is-fullwidth')))
        final_link = driver.find_element(By.CSS_SELECTOR, 'div.abuttons a.button.is-download.is-fullwidth')
        
        existing_files = set(os.listdir(DOWNLOAD_FOLDER))
        
        log("Selenium: Downloading...")
        driver.execute_script("arguments[0].click();", final_link)

        downloaded_file = None
        start_time = time.time()
        while time.time() - start_time < 60:
            current_files = os.listdir(DOWNLOAD_FOLDER)
            for file in current_files:
                if file not in existing_files and file.endswith('.mp3') and not file.endswith('.crdownload'):
                    downloaded_file = file
                    break
            if downloaded_file:
                break
            time.sleep(0.5)

        if downloaded_file:
            watermark = " - SoundLoadMate.com"
            full_path = os.path.join(DOWNLOAD_FOLDER, downloaded_file)
            if downloaded_file.endswith(watermark + ".mp3"):
                new_name = downloaded_file.replace(watermark, "")
                new_path = os.path.join(DOWNLOAD_FOLDER, new_name)
                os.rename(full_path, new_path)
                log(f"Success! Saved as: '{new_name}'")
            else:
                log(f"Success! Saved as: '{downloaded_file}'")
            download_success = True
        else:
            log("Timeout waiting for file.", level="ERROR")

    except Exception as e:
        log(f"Selenium Error: {e}", level="ERROR")
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(traceback.format_exc() + "\n")
    finally:
        driver.quit()
    
    return download_success

def main():
    print_ban()
    log("--- SCRIPT STARTED ---")
    log(f"Target: {TARGET_PROFILE_URL}")
    
    archived_urls = set()
    if os.path.exists(ARCHIVE_FILE):
        with open(ARCHIVE_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                archived_urls.add(line.strip())
    
    log(f"Loaded {len(archived_urls)} tracks from history.")

    try:
        while True:
            latest_url = get_latest_track_url(TARGET_PROFILE_URL)

            if latest_url:
                if latest_url not in archived_urls:
                    print()
                    log("Find the Track!", level="INFO")
                    log(f"Link: {latest_url}", level="INFO")
                    
                    if download_with_selenium(latest_url):
                        with open(ARCHIVE_FILE, 'a', encoding='utf-8') as f:
                            f.write(latest_url + "\n")
                        archived_urls.add(latest_url)
                        log("Added to archive.")
                    else:
                        log("Failed to download.", level="ERROR")
                else:
                    log("No new tracks...", to_file=False, end='\r')
            else:
                 log("Unable to check profile...", to_file=False, end='\r')

            time.sleep(CHECK_INTERVAL)

    except KeyboardInterrupt:
        print()
        log("Exit by user.")

if __name__ == "__main__":
    main()