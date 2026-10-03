import json
import time
from playwright.sync_api import sync_playwright

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path='/usr/bin/chromium',
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
            ]
        )
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 900},
            locale="id-ID"
        )
        page = context.new_page()

        # Let's inspect redirect
        print("Opening shortlink...")
        try:
            page.goto("https://s.shopee.co.id/3qNaOVRWrP", wait_until="domcontentloaded", timeout=45000)
        except Exception as e:
            print("Goto domcontentloaded error:", e)

        print("Current URL:", page.url)
        # Give it time to follow JS redirects and render
        for i in range(10):
            time.sleep(2)
            print(f"Step {i}: URL = {page.url}, Title = {page.title()}")
            if "dara" in page.title().lower() or "shopee" in page.title().lower():
                break

        print("Finished waiting. Final URL:", page.url)
        print("Page Title:", page.title())

        # Safely try to get content
        for _ in range(5):
            try:
                content = page.content()
                with open("rendered_page.html", "w", encoding="utf-8") as f:
                    f.write(content)
                print("Successfully wrote rendered_page.html, size:", len(content))
                break
            except Exception as e:
                print("Content read retry:", e)
                time.sleep(2)

        browser.close()

if __name__ == "__main__":
    run()
