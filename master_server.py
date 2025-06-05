import http.server
import socketserver
import json
import logging
import time
from urllib.parse import urlparse, parse_qs
from typing import List, Dict, Any

# --- Setup Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
# --- End Logging Setup ---

PORT = 8001
HOST = "0.0.0.0" # Listen on all available interfaces
URL_FILE_PATH = "urls_to_crawl.txt" # File to store URLs

# Helper function to load URLs from file
def _load_urls_from_file() -> List[str]:
    urls = []
    try:
        with open(URL_FILE_PATH, 'r', encoding='utf-8') as f:
            for line in f:
                url = line.strip()
                if url:
                    urls.append(url)
        logger.info(f"Loaded {len(urls)} URLs from {URL_FILE_PATH}")
    except FileNotFoundError:
        logger.warning(f"URL file '{URL_FILE_PATH}' not found. Returning empty list of URLs. Please create the file with one URL per line.")
    except Exception as e:
        logger.error(f"Error loading URLs from {URL_FILE_PATH}: {e}", exc_info=True)
    return urls

# Stores the latest status of each connected machine
# Key: machine_name (str), Value: Dict[str, Any] (machine metrics + timestamp)
connected_machines_status: Dict[str, Dict[str, Any]] = {}

class MyHandler(http.server.SimpleHTTPRequestHandler):
    def _set_headers(self, status_code=200, content_type='application/json'):
        self.send_response(status_code)
        self.send_header('Content-type', content_type)
        self.end_headers()

    def do_GET(self):
        parsed_path = urlparse(self.path)
        path = parsed_path.path

        if path == "/get_urls_to_crawl":
            logger.info("Received GET request for /get_urls_to_crawl")
            urls = _load_urls_from_file() # Load URLs dynamically
            response_data = {"urls": urls, "message": f"Returning {len(urls)} URLs for crawling."}
            self._set_headers(200)
            self.wfile.write(json.dumps(response_data).encode('utf-8'))
        elif path == "/get_all_machines_status":
            logger.info("Received GET request for /get_all_machines_status")
            machines_list = list(connected_machines_status.values())
            response_data = {"machines": machines_list}
            self._set_headers(200)
            self.wfile.write(json.dumps(response_data).encode('utf-8'))
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"detail": "Not Found"}).encode('utf-8'))

    def do_POST(self):
        parsed_path = urlparse(self.path)
        path = parsed_path.path

        if path == "/update_machine_status":
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                status_update = json.loads(post_data.decode('utf-8'))
                
                # Validate required fields (basic validation)
                required_fields = ["machine_name", "total_storage_gb", "free_storage_gb", 
                                   "cpu_usage_percent", "memory_usage_percent", "crawling_status"]
                if not all(field in status_update for field in required_fields):
                    self._set_headers(400)
                    self.wfile.write(json.dumps({"detail": "Missing required fields"}).encode('utf-8'))
                    logger.warning(f"Received malformed status update: {status_update}")
                    return

                machine_name = status_update["machine_name"]
                status_update["last_updated"] = time.time() # Add timestamp
                connected_machines_status[machine_name] = status_update
                
                logger.info(f"Received status update from '{machine_name}'. Status: '{status_update['crawling_status']}'")
                response_data = {"message": f"Status received for machine '{machine_name}'."}
                self._set_headers(200)
                self.wfile.write(json.dumps(response_data).encode('utf-8'))
                
            except json.JSONDecodeError:
                self._set_headers(400)
                self.wfile.write(json.dumps({"detail": "Invalid JSON"}).encode('utf-8'))
                logger.warning("Received invalid JSON for status update.")
            except Exception as e:
                self._set_headers(500)
                self.wfile.write(json.dumps({"detail": f"Internal server error: {str(e)}"}).encode('utf-8'))
                logger.error(f"Error processing status update: {e}", exc_info=True)
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"detail": "Not Found"}).encode('utf-8'))

if __name__ == "__main__":
    Handler = MyHandler
    with socketserver.TCPServer((HOST, PORT), Handler) as httpd:
        logger.info(f"Serving Central Master Server at http://{HOST}:{PORT}")
        logger.info("Endpoints: /get_urls_to_crawl (GET), /update_machine_status (POST), /get_all_machines_status (GET)")
        httpd.serve_forever() 