# 91 Video Downloader

A Python-based GUI application that automates the process of extracting and downloading videos from 91xxxx web pages.

## Features

* **GUI Interface:** Built with `tkinter`, providing a simple window to input URLs and view status.
* **Mobile Emulation:** Automatically configures Chrome to masquerade as an iPhone X to expose direct video links.
* **Auto-Driver Management:** Uses `webdriver-manager` to automatically download and install the correct version of ChromeDriver.
* **Smart Extraction:**
    * Detects `video` tags automatically.
    * Handles both direct **MP4** downloads and **M3U8** stream merging.
* **Download Manager:**
    * Downloads files to a local `91_Videos` directory.
    * Supports resumable downloads (for MP4) and segment merging (for M3U8).
    * Sanitizes filenames automatically.

## Prerequisites

1.  **Python 3.x** installed.
2.  **Google Chrome** browser installed on your system.

## Installation

1.  Clone this repository or save the script file.
2.  Install the required dependencies using pip:

```bash
pip install -r requirements.txt
```
## Usage

1.  **Run the script:**
    ```bash
    python3 downloader.py
    ```

2.  **Enter URL:**
    Paste the target video page URL into the input field in the GUI.

3.  **Start Process:**
    Click the **"启动浏览器抓取"** (Start Browser Capture) button.

4.  **Important Manual Step:**
    * An automated Chrome window will open in "Mobile Mode".
    * **You must manually click the "Play" button on the video in that browser window.**
    * The script waits up to **30 seconds** for the video to start playing to capture the network source.

5.  **Download:**
    * Once the source is detected, the browser will close automatically.
    * The download will start immediately within the GUI.
    * Files are saved to the `91_Videos` folder in the same directory as the script.

## Directory Structure

```text
.
├── script.py            # The main application script
├── requirements.txt     # Python dependencies
└── 91_Videos/           # Auto-generated folder where videos are saved