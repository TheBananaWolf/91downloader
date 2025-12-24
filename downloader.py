import tkinter as tk
from tkinter import messagebox
import threading
import os
import sys
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

# --- 1. 基础设置 ---
def get_base_path():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))

BASE_PATH = get_base_path()
DOWNLOAD_PATH = os.path.join(BASE_PATH, '91_Videos')

if not os.path.exists(DOWNLOAD_PATH):
    os.makedirs(DOWNLOAD_PATH)

def open_download_folder():
    try:
        os.startfile(DOWNLOAD_PATH)
    except:
        messagebox.showinfo("路径", DOWNLOAD_PATH)

# --- 2. 核心逻辑：浏览器自动化 ---
def download_process(page_url):
    status_label.config(text="步骤 1/3: 正在启动自动化浏览器...")
    
    driver = None
    try:
        # 设置 Chrome 伪装成 iPhone
        # 这一步非常关键！手机版网页的视频地址是明文的！
        mobile_emulation = { "deviceName": "iPhone X" }
        chrome_options = Options()
        chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)
        # 忽略证书错误
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument('--ignore-ssl-errors')
        
        # 自动安装驱动并启动
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        status_label.config(text="正在打开网页，请稍候...")
        driver.get(page_url)
        
        # 提示用户
        status_label.config(text="【重要】请在弹出的浏览器中，手动点击一下视频播放！")
        
        # 循环检测视频标签
        video_src = None
        for i in range(30): # 等待30秒，让用户去点播放
            try:
                # 手机版通常直接用 <video> 标签
                video_element = driver.find_element(By.TAG_NAME, 'video')
                src = video_element.get_attribute('src')
                
                if src and ("mp4" in src or "m3u8" in src):
                    video_src = src
                    print(f"抓取成功: {video_src}")
                    break
            except:
                pass
            time.sleep(1)
            
        if not video_src:
            raise Exception("30秒内未检测到播放，请确认视频是否已开始播放。")

        # 获取视频标题
        try:
            title = driver.title.replace("Chinese homemade video", "").replace("- 91 Porn", "").strip()
        except:
            title = "downloaded_video"
            
        safe_title = "".join([c for c in title if c.isalnum() or c in (' ', '-', '_')]).strip()

        # 关闭浏览器，任务完成
        driver.quit()
        status_label.config(text=f"已获取地址，准备下载: {safe_title}")

    except Exception as e:
        if driver: driver.quit()
        messagebox.showerror("抓取失败", f"自动化过程出错: {e}")
        reset_ui()
        return

    # --- 3. 下载部分 ---
    # 如果抓到的是 m3u8，用 requests 拼接；如果是 mp4，直接下载
    final_path = os.path.join(DOWNLOAD_PATH, f"{safe_title}.mp4")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1',
            'Referer': 'https://91porn.com/'
        }

        if ".m3u8" in video_src:
            # 下载 M3U8 逻辑
            status_label.config(text="检测到 M3U8，开始分片下载...")
            r = requests.get(video_src, headers=headers, verify=False)
            lines = r.text.split('\n')
            ts_urls = [line.strip() for line in lines if line and not line.startswith('#')]
            
            # 处理相对路径
            from urllib.parse import urljoin
            ts_urls = [urljoin(video_src, line) for line in ts_urls]
            
            with open(final_path, 'wb') as f:
                pass
                
            total = len(ts_urls)
            session = requests.Session()
            for i, ts in enumerate(ts_urls):
                status_label.config(text=f"下载中: {i+1}/{total}")
                res = session.get(ts, headers=headers, verify=False)
                with open(final_path, 'ab') as f:
                    f.write(res.content)
                    
        else:
            # 直接下载 MP4
            status_label.config(text="检测到 MP4，直接下载中...")
            with requests.get(video_src, headers=headers, stream=True, verify=False) as r:
                r.raise_for_status()
                with open(final_path, 'wb') as f:
                    downloaded = 0
                    total_size = int(r.headers.get('content-length', 0))
                    for chunk in r.iter_content(chunk_size=8192): 
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            percent = downloaded / total_size * 100
                            status_label.config(text=f"下载进度: {percent:.1f}%")

        status_label.config(text="完成！")
        messagebox.showinfo("成功", f"下载完成！\n{final_path}")
        
    except Exception as e:
        messagebox.showerror("下载错误", str(e))
    finally:
        reset_ui()

# --- GUI ---
def start_task():
    url = url_entry.get().strip()
    if not url: return
    download_button.config(state=tk.DISABLED)
    threading.Thread(target=download_process, args=(url,), daemon=True).start()

def reset_ui():
    download_button.config(state=tk.NORMAL)
    status_label.config(text="就绪")

root = tk.Tk()
root.title("Selenium 智能下载器")
root.geometry("500x250")

frame = tk.Frame(root, padx=20, pady=20)
frame.pack(fill=tk.BOTH)

tk.Label(frame, text="视频地址:", font=("Arial", 10)).pack(anchor=tk.W)
url_entry = tk.Entry(frame, width=60)
url_entry.pack(pady=5)

btn_frame = tk.Frame(frame)
btn_frame.pack(pady=15)
download_button = tk.Button(btn_frame, text="启动浏览器抓取", command=start_task, bg="#80deea", padx=10)
download_button.pack(side=tk.LEFT, padx=10)
tk.Button(btn_frame, text="打开文件夹", command=open_download_folder).pack(side=tk.LEFT)

status_label = tk.Label(frame, text="原理: 自动打开手机版网页 -> 提取播放地址 -> 下载")
status_label.pack(pady=10)

root.mainloop()