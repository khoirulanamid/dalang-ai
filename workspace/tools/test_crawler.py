import json
import os
import sys
import time
from playwright.sync_api import sync_playwright

def crawl(url):
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

        api_responses = []

        def on_response(res):
            try:
                if any(x in res.url for x in ["api/v4/pdp", "api/v4/item", "api/v2/item"]):
                    print(f"Captured: {res.url}")
                    try:
                        api_responses.append({"url": res.url, "data": res.json()})
                    except Exception:
                        pass
            except Exception:
                pass

        page.on("response", on_response)

        print(f"Going to {url}...")
        page.goto(url, wait_until="commit", timeout=45000)
        
        # Wait until redirection completes
        for _ in range(15):
            time.sleep(1)
            cur_url = page.url
            if "shopee.co.id" in cur_url and cur_url != url:
                print(f"Redirected to: {cur_url}")
                break
        
        # Now wait for domcontentloaded / load
        try:
            page.wait_for_load_state("load", timeout=15000)
        except Exception as e:
            print("load state timeout:", e)

        print(f"Current URL: {page.url}")
        print(f"Title: {page.title()}")

        # Sleep a few seconds to let PDP API trigger
        time.sleep(5)

        # Check captured APIs
        print(f"Captured {len(api_responses)} item/pdp API responses")

        # Let's inspect page content
        body_text = page.inner_text("body")
        print(f"Body text length: {len(body_text)}")
        print("Body text preview:\n", body_text[:1000])

        # Also let's try page.evaluate fetch if not captured
        if not api_responses:
            print("Trying in-page fetch for PDP...")
            res_json = page.evaluate("""async () => {
                try {
                    const r = await fetch('/api/v4/pdp/get_pc?item_id=43032631708&shop_id=1667221136');
                    return await r.json();
                } catch(e) {
                    return {error: e.toString()};
                }
            }""")
            print("In-page fetch result keys:", list(res_json.keys()) if isinstance(res_json, dict) else res_json)
            if isinstance(res_json, dict) and "data" in res_json:
                api_responses.append({"url": "in-page", "data": res_json})

        # Save HTML or inspect DOM
        with open("page_dump.html", "w", encoding="utf-8") as f:
            f.write(page.content())

        browser.close()
        return api_responses, body_text

if __name__ == "__main__":
    crawl("https://s.shopee.co.id/3qNaOVRWrP")
