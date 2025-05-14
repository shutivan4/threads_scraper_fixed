from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from playwright.sync_api import sync_playwright
import time

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to the AI threads scraper API!"}

@app.get("/threads")
def get_threads(query: str):
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()
            page.goto(f"https://www.threads.net/search?q={query}")
            time.sleep(5)  # Ждём загрузки страницы

            print("🔍 Страница загружена. HTML:")
            print(page.content())

            posts = page.locator("div[role='article']").all_text_contents()
            posts = [post.strip() for post in posts if post.strip()]

            browser.close()

            if not posts:
                return JSONResponse(status_code=500, content={"detail": "No posts found. Selectors may have changed."})

            return {"status": "success", "query": query, "results": posts[:10]}
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return JSONResponse(status_code=500, content={"detail": "An error occurred during scraping."})
