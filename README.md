# 🕷️ Distributed Web Crawler with Eel GUI & Central Server 🖥️

This project implements a distributed web crawling system using Python and Eel. Clients fetch URLs from a central server, crawl them, process content (including sitemaps), and save zipped Markdown results.

## ✨ Core Features

*   🌐 **Distributed Crawling:** Multiple clients work in parallel.
*   🖥️ **Eel-based GUI:** Local web UI for each crawler client.
*   🔗 **Centralized URL Management:** Master server provides URLs from `urls_to_crawl.txt`.
*   📊 **Local Machine Monitoring:** GUI shows client's CPU, memory, and storage.
*   🗺️ **Sitemap Processing:** Extracts URLs & lastmod dates from sitemaps (`sitemap_data.csv`).
*   📄 **Content Extraction & Cleaning:** `crawl4ai` extracts content to clean Markdown.
*   🗃️ **Organized Output:** Zipped per-site directories with Markdown, sitemap CSV, and `crawl_metadata.json`.
*   ⚙️ **Configurable Crawl:** Set max depth and concurrency via GUI.
*   🔔 **Status Notification:** Clients inform the server on task completion.

## 🏗️ Architecture

1.  **👑 Central Master Server (`master_server.py`):**
    *   Serves URLs from `urls_to_crawl.txt` (e.g., `http://SERVER_IP:8001/get_urls_to_crawl`).
    *   Receives completion notifications (e.g., `http://SERVER_IP:8001/notify_crawl_finished`).

2.  **🤖 Crawler Client (`main.py` + `web/`):**
    *   Eel GUI (`web/index.html`) for user interaction.
    *   Fetches URLs, crawls sites, processes sitemaps, and saves zipped results.
    *   Sends completion status to the master server.

## 📁 File Structure

```
.
├── main.py                 # Crawler client
├── master_server.py        # Central server
├── sitemap_crawler.py      # Sitemap helper
├── urls_to_crawl.txt       # URLs for master server
├── web/
│   ├── index.html          # Client GUI
│   └── script.js           # Client JS
└── requirements.txt        # (Create this)
```

## 🛠️ Prerequisites

*   Python 3.7+
*   PIP (Python package installer)
*   Modern web browser

## 🚀 Setup

1.  **Clone/Download Files.**
2.  **Create `urls_to_crawl.txt`:** Next to `master_server.py`, add start URLs (one per line).
    ```
    http://example.com
    https://another-site.org
    ```
3.  **Install Dependencies (in a virtual environment):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # Windows: venv\Scripts\activate
    pip install -r requirements.txt
    ```
    **`requirements.txt` content:**
    ```
    eel
    crawl4ai
    aiohttp
    psutil
    # lxml (if needed by dependencies)
    ```

## ▶️ Running the Application

### 1. Start Central Master Server
```bash
python master_server.py
```
(Serves on `http://0.0.0.0:8001` by default)

### 2. Start Crawler Client(s)
```bash
python main.py
```
(Opens GUI in browser, usually `http://localhost:8000`)

### ⚠️ Align Server Ports!
The `master_server.py` runs on port **`8001`**. The client (`main.py`) needs to target this port.
**In `main.py`, ensure functions `fetch_urls_from_remote_server` and `notify_server_crawl_finished` use port `8001` for the `target_url`:**
```python
# Example in main.py
target_url = f"http://{server_ip}:8001/get_urls_to_crawl" # Port 8001
```

### 3. Use Client GUI
*   **Remote Server IP:** Enter IP of machine running `master_server.py`.
*   **Output Directory:** Where to save zipped results.
*   **Max Concurrency & Depth:** Set crawl parameters.
*   Click **"Fetch URLs and Start Crawl"**.

## 📦 Output Structure

For each site (e.g., `http://example.com`):
*   A ZIP file (e.g., `[output_dir]/example_com_output.zip`) containing:
    *   Markdown files for each crawled page.
    *   `sitemap_data.csv` (sitemap URLs & lastmod dates).
    *   `crawl_metadata.json` (crawl parameters, summary).

## 🔧 Key Config Points

*   **`main.py`:** `EXCLUDE_KEYWORDS`, `COMMON_HEADERS`. **Ensure remote server port is 8001.**
*   **`master_server.py`:** `PORT` (default 8001), `HOST`, `URL_FILE_PATH`.

## 💡 Potential Improvements

*   Live client status dashboard on the master server.
*   Dynamic URL assignment by the server.
*   Centralized logging.
*   Enhanced error handling & retries.
*   GUI options for pause/resume.
