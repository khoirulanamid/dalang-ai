import json
import os
import sys
import time
from playwright.sync_api import sync_playwright

def crawl():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path="/usr/bin/chromium",
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-blink-features=AutomationControlled",
            ]
        )
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={"width": 1366, "height": 768},
            locale="id-ID",
        )
        page = context.new_page()

        api_responses = {}

        def on_response(res):
            try:
                url = res.url
                if any(x in url for x in ["api/v4/pdp", "api/v4/item", "api/v2/item"]):
                    print(f"Captured: {url}")
                    try:
                        api_responses[url] = res.json()
                    except Exception as e:
                        pass
            except Exception:
                pass

        page.on("response", on_response)

        target = "https://s.shopee.co.id/3qNaOVRWrP"
        print(f"Navigating to {target}")
        page.goto(target, wait_until="commit", timeout=45000)

        # Wait until URL contains /product/
        for i in range(30):
            time.sleep(1)
            cur = page.url
            if "/product/" in cur:
                print(f"Reached product page at second {i}: {cur}")
                break

        # Wait for page to stabilize
        print("Waiting for network idle or 10 seconds...")
        try:
            page.wait_for_load_state("networkidle", timeout=15000)
        except Exception:
            pass
        
        time.sleep(5)

        print(f"Current URL: {page.url}")
        print(f"Title: {page.title()}")

        print(f"Total API responses captured: {len(api_responses)}")
        for k in api_responses:
            print("API URL:", k)
            with open("api_response.json", "w", encoding="utf-8") as f:
                json.dump(api_responses[k], f, indent=2)

        # Check DOM text
        try:
            body_text = page.inner_text("body")
            print("Body text snippet (first 1000 chars):")
            print(body_text[:1000])
            with open("body_text.txt", "w", encoding="utf-8") as f:
                f.write(body_text)
        except Exception as e:
            print("Error getting body text:", e)

        # Get images
        images = page.evaluate("""() => {
            const list = [];
            document.querySelectorAll('img').forEach(img => {
                if (img.src) list.push(img.src);
            });
            return list;
        }""")
        print(f"Found {len(images)} images in DOM")
        with open("dom_images.json", "w", encoding="utf-8") as f:
            json.dump(images, f, indent=2)

        browser.close()

if __name__ == "__main__":
    crawl()
