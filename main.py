from fastapi import FastAPI
from playwright.sync_api import sync_playwright
import os
import logging

app = FastAPI()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.get("/")
async def read_root():
    return {"message": "Welcome to the AI threads scraper API!"}

@app.get("/threads")
async def get_threads(query: str):
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(f"https://www.threads.net/search?q={query}")
            page.wait_for_timeout(3000)  # Ждём загрузки контента

            posts = page.locator("article")
            result = []
            count = posts.count()
            for i in range(min(10, count)):
                el = posts.nth(i)
                text = el.locator("span").all_inner_texts()
                author = el.locator("a").first.inner_text()
                url = el.locator("a").first.get_attribute("href")
                result.append({
                    "author": author,
                    "text": " ".join(text).strip(),
                    "url": f"https://www.threads.net{url}"
                })

            browser.close()
            return {"query": query, "posts": result}
    except Exception as e:
        logger.error(f"Error during scraping: {e}")
        return {"error": "An error occurred during scraping."}
