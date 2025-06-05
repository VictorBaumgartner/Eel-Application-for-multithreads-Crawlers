# remote_server.py on the 192.168.0.43 machine
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from typing import List, Dict, Any
import logging

# --- Setup Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
# --- End Logging Setup ---

app = FastAPI(
    title="Remote URL Provider and Notification Server",
    description="Provides URLs for crawling and receives crawl completion notifications.",
    version="1.0.0"
)

# In a real application, these URLs would come from a database, a queue, or a more dynamic source.
# For demonstration, we'll provide a static list.
example_urls_to_crawl = [
    "http://quotes.toscrape.com/page/1/",
    "http://quotes.toscrape.com/page/2/",
    "https://www.scrapingbee.com/blog/",
    "https://www.dataquest.io/blog/",
    "https://example.com" # A simple example site
]

# A simple model for the notification payload
class CrawlNotification(BaseModel):
    status: str # e.g., "successfully_processed", "finished_with_issues"
    machine_name: str # The name of the machine that finished crawling

@app.get("/get_urls_to_crawl", response_model=Dict[str, Any], summary="Get a list of URLs to be crawled")
async def get_urls_to_crawl():
    """
    Returns a list of URLs that the client application should crawl.
    """
    logger.info(f"Received request for URLs. Providing {len(example_urls_to_crawl)} URLs.")
    return {"urls": example_urls_to_crawl, "message": f"Returning {len(example_urls_to_crawl)} URLs for crawling."}

@app.post("/notify_crawl_finished", summary="Receive notification when a crawl process is finished")
async def notify_crawl_finished(notification: CrawlNotification):
    """
    Receives a notification from a client application when it has finished a crawl job.
    """
    logger.info(f"Received crawl completion notification from machine '{notification.machine_name}'. Status: '{notification.status}'.")
    # In a real scenario, you would process this notification,
    # e.g., update a database, log completion, trigger next steps.
    return {"message": f"Notification received for machine '{notification.machine_name}'. Status: '{notification.status}'."}

if __name__ == "__main__":
    logger.info("Starting Remote Server application...")
    logger.info("Navigate to http://192.168.0.43:8000/docs for interactive API documentation (Swagger UI).")
    # Listen on 0.0.0.0 to make it accessible from other machines on the network.
    # Replace 192.168.0.43 with your actual server's IP address if running on a different machine.
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")