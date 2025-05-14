import time
from fastapi import FastAPI
from playwright.sync_api import sync_playwright

app = FastAPI()

def get_threads(query: str):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(f'https://www.threads.net/{query}')
        time.sleep(3)  # ждём, пока загрузятся данные

        posts = page.query_selector_all('.post-class')  # Замените на актуальный селектор

        result = []
        for post in posts:
            text = post.text_content()
            result.append(text)

        browser.close()
    return result

@app.get("/threads")
def read_threads(query: str):
    try:
        threads = get_threads(query)
        return {"threads": threads}
    except Exception as e:
        return {"error": str(e)}