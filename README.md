# Distributed Web Crawler with Eel GUI and Central Server

This project implements a distributed web crawling system. It consists of:
1.  **Crawler Clients (`main.py`):** Python applications with an Eel-based GUI. Each client can run on a separate machine. They fetch URLs to crawl from a central server, perform the crawling, process the content (including sitemaps), and save the results locally as Markdown files, which are then zipped.
2.  **Central Master Server (`master_server.py`):** A simple Python HTTP server that provides URLs for clients to crawl and can receive status updates/notifications from them.
3.  **Frontend (`web/index.html`, `web/script.js`):** The user interface for each crawler client, allowing users to configure and initiate crawls.
4.  **Sitemap Processor (`sitemap_crawler.py`):** A helper module used by the client to fetch and process sitemap data.

## Core Features

*   **Distributed Crawling:** Multiple client instances can work in parallel on different machines.
*   **Eel-based GUI:** Provides a local web-based interface for each crawler client.
*   **Centralized URL Management:** The `master_server.py` serves a list of URLs to be crawled, managed via a `urls_to_crawl.txt` file.
*   **Local Machine Monitoring:** The GUI displays CPU, memory, and storage metrics of the client machine.
*   **Sitemap Processing:** Fetches and parses sitemaps to extract URLs and last modification dates, saving them to `sitemap_data.csv`.
*   **Content Extraction & Cleaning:** Crawls web pages using `crawl4ai`, extracts content into Markdown, and applies cleaning rules.
*   **Organized Output:** Saves crawled data into per-site directories, with each page as a separate Markdown file.
*   **ZIP Archiving:** Each site's output directory (including Markdown files, sitemap CSV, and metadata) is compressed into a ZIP file.
*   **Metadata Inclusion:** A `crawl_metadata.json` file is included in each ZIP archive, detailing the crawl parameters and a summary of results for that site.
*   **Configurable Crawl:** Users can set maximum crawl depth and concurrency via the GUI.
*   **Status Notification:** Clients notify the central server upon completion of their assigned crawl tasks.

## Architecture

1.  **Central Master Server (`master_server.py`):**
    *   Runs on a designated machine.
    *   Reads a list of target websites/domains from `urls_to_crawl.txt`.
    *   Serves these URLs via an API endpoint (`/get_urls_to_crawl`).
    *   Listens for status updates from clients (e.g., `/update_machine_status` though this is more for a potential dashboard, and `/notify_crawl_finished` for task completion).
    *   Provides an endpoint (`/get_all_machines_status`) to view the status of connected/reporting machines.

2.  **Crawler Client (`main.py` + `web/`):**
    *   Runs on one or more machines.
    *   Starts an Eel application, serving `web/index.html` as its GUI.
    *   **User Interaction (GUI):**
        *   User inputs the IP address of the Central Master Server.
        *   User specifies an output directory for crawled data.
        *   User sets crawl parameters (concurrency, depth).
        *   User clicks "Fetch URLs and Start Crawl".
    *   **Backend Process:**
        *   The client backend (`main.py`) requests URLs from the Central Master Server.
        *   For each assigned root URL:
            *   Resolves the effective start URL (handles redirects).
            *   Creates a unique output directory for the site (e.g., `output_data/example_com/`).
            *   Initiates crawling using `crawl4ai` up to the specified depth and concurrency.
            *   Filters out links to common file types (PDF, images) from being saved as Markdown.
            *   Saves extracted content as cleaned Markdown files (e.g., `output_data/example_com/example_com_page_path.md`).
            *   Calls `sitemap_crawler.py` to process the site's sitemap, saving results to `sitemap_data.csv` within the site's directory.
            *   Generates `crawl_metadata.json` with crawl details.
            *   Zips the entire site-specific directory (e.g., `output_data/example_com_output.zip`).
            *   Deletes the original site-specific directory after successful zipping.
        *   After processing all assigned URLs, it notifies the Central Master Server.
    *   **Local Metrics:** Continuously displays local machine metrics (CPU, RAM, Disk, Crawling Status) in its GUI.

## File Structure

```
.
├── main.py                 # Crawler client backend (Eel app)
├── master_server.py        # Central master server
├── sitemap_crawler.py      # Helper for sitemap processing
├── urls_to_crawl.txt       # List of URLs for the master server
├── web/
│   ├── index.html          # GUI for the crawler client
│   ├── script.js           # Frontend JavaScript for the GUI
│   └── (other css/assets)
└── requirements.txt        # Python dependencies (you'll need to create this)
```

## Prerequisites

*   Python 3.7+
*   PIP (Python package installer)
*   A modern web browser (for the Eel GUI)

## Setup

1.  **Clone the repository (or download the files).**
2.  **Create `urls_to_crawl.txt`:**
    In the same directory as `master_server.py`, create a file named `urls_to_crawl.txt`. Add one starting URL per line, e.g.:
    ```
    http://example.com
    https://another-site.org/blog
    ```
3.  **Install Python dependencies:**
    It's highly recommended to use a virtual environment.
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    pip install -r requirements.txt
    ```
    You'll need to create `requirements.txt` with the following (or a more specific version based on your `crawl4ai` and other dependencies):
    ```
    eel
    crawl4ai
    aiohttp
    psutil
    # lxml (often a dependency of crawl4ai or sitemap parsers, include if needed)
    ```

## Running the Application

### 1. Start the Central Master Server

Open a terminal, navigate to the project directory, and run:
```bash
python master_server.py
```
By default, it will serve on `http://0.0.0.0:8001`.
Endpoints:
*   `GET /get_urls_to_crawl`: Returns URLs for clients.
*   `POST /update_machine_status`: Clients can (manually or programmatically) send their status.
*   `GET /get_all_machines_status`: View statuses of machines that have reported.
*   `POST /notify_crawl_finished`: Clients notify when their batch is done.

### 2. Start the Crawler Client(s)

On each machine you want to use for crawling (can be the same machine as the server or different ones):
Open a new terminal, navigate to the project directory, and run:
```bash
python main.py
```
This will start the Eel application and should automatically open the GUI (`index.html`) in your default web browser. If it doesn't, open your browser and navigate to `http://localhost:8000` (or whatever port Eel uses if 8000 is taken).

### 3. Using the Crawler Client GUI

*   **Remote Server IP:** Enter the IP address of the machine running `master_server.py` (e.g., `192.168.0.43` or `localhost` if on the same machine). The port is assumed to be `8000` by the `fetch_urls_from_remote_server` function in `main.py` for fetching URLs, but the `master_server.py` runs on `8001`. **Important:** The client code's `fetch_urls_from_remote_server` and `notify_server_crawl_finished` functions currently hardcode port `8000` for the remote server, while `master_server.py` runs on `8001`. You'll need to align these. For simplicity, let's assume the client targets the `master_server.py` on port `8001`.
    *   Modify `main.py` where `target_url` is constructed in `fetch_urls_from_remote_server` and `notify_server_crawl_finished` to use port `8001`. For example:
        ```python
        # In main.py, function fetch_urls_from_remote_server
        target_url = f"http://{server_ip}:8001/get_urls_to_crawl"
        # In main.py, function notify_server_crawl_finished
        target_url = f"http://{server_ip}:8001/notify_crawl_finished"
        ```
*   **Output Directory:** Specify a local path where the zipped crawl data will be saved (e.g., `./crawled_data`).
*   **Max Concurrency:** Number of parallel requests during crawling for a single site (e.g., `8`).
*   **Max Depth:** How many link levels deep to crawl from the start URL (e.g., `2`). `0` means only the start page.
*   **Click "Fetch URLs and Start Crawl".**

The GUI will display:
*   Local machine metrics.
*   Status messages from the remote server.
*   Overall crawl progress and results.

## Output Structure

For each root URL crawled (e.g., `http://example.com`):
1.  A temporary directory is created (e.g., `[output_dir]/example_com/`).
2.  Inside this directory:
    *   `example_com_some_page.md`: Markdown file for each crawled page.
    *   `example_com_another_page.md`: ...
    *   `sitemap_data.csv`: Contains URLs found in the sitemap with their last modification dates.
    *   `crawl_metadata.json`: Contains details about this specific crawl task (initial URL, effective URL, parameters, summary of success/failures).
3.  This directory is then zipped into `[output_dir]/example_com_output.zip`.
4.  The temporary directory (`[output_dir]/example_com/`) is deleted.

**`crawl_metadata.json` Example Snippet:**
```json
{
  "crawl_parameters": {
    "requested_url_original": "http://example.com",
    "requested_url_schemed": "http://example.com",
    "base_output_directory_target_for_zip": "/path/to/your/output_dir",
    "max_concurrency": 8,
    "max_depth": 2
  },
  "crawl_summary_snapshot": {
    "success": ["http://example.com/", "http://example.com/about"],
    "failed": [],
    "skipped_by_filter": ["http://example.com/document.pdf"],
    "initial_url": "http://example.com",
    "effective_start_url": "http://example.com/",
    "output_path_for_site": "/path/to/your/output_dir/example_com",
    "sitemap_processing_results": {
      "status": "success",
      "sitemap_csv_path": "/path/to/your/output_dir/example_com/sitemap_data.csv",
      // ... more sitemap details
    },
    "metadata_file_info_in_archive": "This metadata is stored as 'example_com/crawl_metadata.json' (relative to the root of the unzipped archive)."
  }
}
```

## Key Code Points & Configuration

*   **`main.py`:**
    *   `EXCLUDE_KEYWORDS`: List of file extensions/keywords to skip saving as Markdown (but links might still be followed if depth allows).
    *   `COMMON_HEADERS`: Default User-Agent and other headers for crawling.
    *   `prepare_initial_url_scheme()`: Ensures URLs have a scheme.
    *   `crawl_website_single_site()`: Core logic for crawling a single root URL.
    *   `process_and_save_sitemap()`: Handles sitemap processing.
    *   `start_crawl_process()`: Main exposed Eel function orchestrating the crawl for multiple URLs.
    *   `create_zip_archive()`: Zips output.
    *   **Remote Server Port:** As mentioned, ensure the port in `fetch_urls_from_remote_server` and `notify_server_crawl_finished` matches the `master_server.py` port (default `8001`).
*   **`master_server.py`:**
    *   `PORT`, `HOST`: Configuration for the server.
    *   `URL_FILE_PATH`: Path to the file containing URLs to crawl.
*   **`sitemap_crawler.py`:** Contains the logic for `get_sitemap_data_for_single_url` which robustly finds, parses, and extracts data from sitemaps (including sitemap index files).

## Potential Improvements & Future Work

*   **Robust Client Status Reporting:** Implement periodic status updates from clients to the `master_server.py`'s `/update_machine_status` endpoint for a live dashboard.
*   **Dynamic URL Assignment:** Instead of clients pulling all URLs, the server could assign specific URLs or chunks of URLs to clients.
*   **Centralized Logging/Monitoring:** Integrate a more sophisticated logging system where all clients and the server log to a central location.
*   **Error Handling & Retries:** Enhance error handling, especially for network issues, and implement retry mechanisms.
*   **Authentication/Security:** Add basic authentication if deploying in a less trusted environment.
*   **Persistent Server State:** Use a database for the central server to store URL states (pending, in-progress, completed) and machine statuses instead of in-memory dicts.
*   **Scalability:** For very large-scale crawls, consider message queues (e.g., RabbitMQ, Kafka) for distributing tasks.
*   **GUI Enhancements:**
    *   Allow managing `urls_to_crawl.txt` via the master server's interface (if one were built).
    *   Display detailed progress per URL in the client GUI.
    *   Option to pause/resume/cancel crawls.

This README should give a good overview of how to set up, run, and understand your distributed crawling application.
