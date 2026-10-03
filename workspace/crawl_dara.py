import asyncio
import os
import json
import httpx
from pathlib import Path
from playwright.async_api import async_playwright

WORKSPACE_DIR = Path("/root/storage/projects/dalang-ai/workspace")
OUTPUT_IMAGES_DIR = WORKSPACE_DIR / "product_images" / "dara_oneset"
DOCS_DIR = WORKSPACE_DIR / "docs"
CAMPAIGN_JSON = DOCS_DIR / "dara_oneset_campaign.json"

# Also ensure workspace/workspace/product_images/dara_oneset exists if needed
ALT_IMAGES_DIR = WORKSPACE_DIR / "workspace" / "product_images" / "dara_oneset"

SHORTLINK = "https://s.shopee.co.id/3qNaOVRWrP"

async def main():
    OUTPUT_IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    ALT_IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    # Find chromium executable
    exec_candidates = [
        "/root/.cache/ms-playwright/chromium-1243/chrome-linux/chrome",
        "/root/.cache/ms-playwright/chromium-1243/chrome-linux-arm64/chrome",
        "/root/.cache/ms-playwright/chromium-1234/chrome-linux/chrome",
        "/root/.cache/ms-playwright/chromium-1234/chrome-linux-arm64/chrome",
    ]
    executable_path = None
    for cand in exec_candidates:
        if os.path.exists(cand):
            executable_path = cand
            break

    print(f"Using executable: {executable_path}")

    # First resolve shortlink via httpx or playwright
    async with httpx.AsyncClient(follow_redirects=True) as client:
        try:
            resp = await client.get(SHORTLINK, headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"})
            print(f"HTTPX redirected URL: {resp.url}")
            target_url = str(resp.url)
        except Exception as e:
            print(f"HTTPX redirect failed: {e}")
            target_url = SHORTLINK

    async with async_playwright() as p:
        launch_kwargs = {
            "headless": True,
            "args": ["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"]
        }
        if executable_path:
            launch_kwargs["executable_path"] = executable_path

        browser = await p.chromium.launch(**launch_kwargs)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800}
        )
        page = await context.new_page()

        print(f"Navigating to {SHORTLINK}...")
        try:
            await page.goto(SHORTLINK, wait_until="networkidle", timeout=30000)
        except Exception as e:
            print(f"Navigation note: {e}")

        await page.wait_for_timeout(5000)
        current_url = page.url
        print(f"Current page URL: {current_url}")
        title = await page.title()
        print(f"Page title: {title}")

        # Save screenshot for debugging
        await page.screenshot(path="dara_crawl_debug.png")

        # Let's inspect page content
        content = await page.content()
        with open("dara_page.html", "w", encoding="utf-8") as f:
            f.write(content)

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
