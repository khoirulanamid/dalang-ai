import json
import os
import re
import urllib.parse
from datetime import datetime, timezone
import httpx
from playwright.sync_api import sync_playwright

def find_chromium():
    candidates = [
        os.getenv("CHROME_PATH"),
        "/usr/bin/chromium",
        "/usr/bin/chromium-browser",
        "/usr/bin/google-chrome",
    ]
    for c in candidates:
        if c and os.path.exists(c):
            return c
    return None

def extract_and_download():
    url = "https://s.shopee.co.id/3qNaOVRWrP"
    dest_dir = "workspace/product_images/dara_oneset"
    os.makedirs(dest_dir, exist_ok=True)
    os.makedirs("docs", exist_ok=True)

    chromium_path = find_chromium()
    api_responses = []
    image_candidates = set()

    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path=chromium_path,
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--single-process",
            ]
        )
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 900}
        )
        page = context.new_page()

        def handle_response(response):
            try:
                content_type = response.headers.get("content-type", "")
                if "application/json" in content_type:
                    body = response.body()
                    data = json.loads(body)
                    api_responses.append({"url": response.url, "data": data})
                elif "image" in content_type:
                    image_candidates.add(response.url)
            except Exception:
                pass

        page.on("response", handle_response)

        print(f"Navigating to {url}...")
        page.goto(url, wait_until="networkidle", timeout=45000)
        page.wait_for_timeout(4000)

        final_url = page.url
        print(f"Final URL: {final_url}")
        page_title = page.title()
        print(f"Page Title: {page_title}")

        # Extract images from DOM
        dom_imgs = page.eval_on_selector_all(
            "img",
            "imgs => imgs.map(img => ({src: img.src, srcset: img.srcset, alt: img.alt, width: img.naturalWidth, height: img.naturalHeight}))"
        )

        # Look for background images
        bg_imgs = page.eval_on_selector_all(
            "[style*='background-image']",
            "elements => elements.map(el => el.style.backgroundImage)"
        )

        content = page.content()

        browser.close()

    print(f"Total API responses captured: {len(api_responses)}")
    print(f"DOM images captured: {len(dom_imgs)}")
    print(f"Background images captured: {len(bg_imgs)}")
    print(f"Image candidates captured: {len(image_candidates)}")

    with open("tools/crawl_debug.json", "w") as f:
        json.dump({
            "final_url": final_url,
            "page_title": page_title,
            "dom_imgs": dom_imgs,
            "bg_imgs": bg_imgs,
            "image_candidates": list(image_candidates),
            "api_urls": [r["url"] for r in api_responses]
        }, f, indent=2)

if __name__ == "__main__":
    extract_and_download()
