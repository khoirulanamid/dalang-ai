import json
import os
import re
import sys
import httpx
from pathlib import Path
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

def run_crawler(url: str, output_img_dir: str, output_json_path: str):
    chromium_path = find_chromium()
    print(f"Using Chromium at: {chromium_path}")
    os.makedirs(output_img_dir, exist_ok=True)
    os.makedirs(os.path.dirname(output_json_path), exist_ok=True)

    captured_data = {}
    captured_images = []

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
            viewport={"width": 1280, "height": 800},
        )
        page = context.new_page()

        def handle_response(response):
            try:
                # Capture item detail API responses
                if "api/v4/item/get" in response.url or "api/v4/pdp/get_pc" in response.url:
                    data = response.json()
                    captured_data["pdp_api"] = data
                    print(f"Captured PDP API from {response.url}")
            except Exception:
                pass

        page.on("response", handle_response)

        print(f"Navigating to {url}...")
        try:
            page.goto(url, wait_until="networkidle", timeout=30000)
        except Exception as e:
            print(f"Navigation warning: {e}")

        final_url = page.url
        print(f"Final URL: {final_url}")

        # Wait a bit for dynamic contents
        page.wait_for_timeout(5000)

        # Try to extract page title and DOM info
        page_title = page.title()
        print(f"Page Title: {page_title}")

        # Check for scripts containing INITIAL_STATE or product data
        scripts = page.evaluate("""() => {
            const results = [];
            document.querySelectorAll('script').forEach(s => {
                if (s.textContent && (s.textContent.includes('item') || s.textContent.includes('Dara') || s.textContent.includes('124500') || s.textContent.includes('124.500'))) {
                    results.push(s.textContent.slice(0, 5000));
                }
            });
            return results;
        }""")

        # Extract images from DOM as well
        dom_images = page.evaluate("""() => {
            const imgs = [];
            document.querySelectorAll('img').forEach(img => {
                const src = img.src || img.getAttribute('data-src') || '';
                if (src && (src.includes('susercontent.com') || src.includes('shopee.co.id'))) {
                    imgs.push(src);
                }
            });
            return imgs;
        }""")
        print(f"Found {len(dom_images)} potential DOM images")

        # Extract text content from product detail section
        body_text = page.evaluate("() => document.body.innerText")

        browser.close()

    return {
        "final_url": final_url,
        "page_title": page_title,
        "captured_api": captured_data.get("pdp_api"),
        "dom_images": dom_images,
        "scripts_len": len(scripts),
        "scripts": scripts[:3],
        "body_preview": body_text[:2000] if body_text else ""
    }

if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else "https://s.shopee.co.id/3qNaOVRWrP"
    res = run_crawler(url, "product_images/dara_oneset", "docs/dara_oneset_campaign.json")
    print("Result keys:", list(res.keys()))
    print("Final URL:", res["final_url"])
    print("Page Title:", res["page_title"])
    if res.get("captured_api"):
        print("PDP API data keys:", res["captured_api"].keys())
    print("DOM images sample:", res["dom_images"][:5])
    print("Body text preview:\n", res["body_preview"][:500])
