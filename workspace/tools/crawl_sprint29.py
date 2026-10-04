import json
import time
import httpx
from playwright.sync_api import sync_playwright

def inspect_shopee():
    url = "https://s.shopee.co.id/8AWbWHUOPx"
    print(f"Opening shortlink: {url}")
    
    captured_data = {}
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
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

        def handle_response(response):
            try:
                res_url = response.url
                if any(k in res_url for k in ["item/get", "pdp/get_pc", "get_detail", "get_item"]):
                    print(f"Captured network response URL: {res_url}")
                    ct = response.headers.get("content-type", "")
                    if "json" in ct:
                        try:
                            data = response.json()
                            captured_data[res_url] = data
                        except Exception as e:
                            print("Error parsing json from response:", e)
            except Exception:
                pass

        page.on("response", handle_response)
        
        try:
            page.goto(url, timeout=45000)
        except Exception as e:
            print("Goto error:", e)
            
        print("Page URL after goto:", page.url)
        
        # Wait for navigation to complete
        for i in range(15):
            time.sleep(2)
            curr_url = page.url
            curr_title = page.title()
            print(f"[{i}] URL: {curr_url} | Title: {curr_title}")
            if "shopee.co.id" in curr_url and "Loading" not in curr_title and curr_title != "Shopee":
                print("Found substantive title!")
                break
                
        time.sleep(3)
        
        # Check if we can fetch item details via page evaluate fetch (uses browser session / anti-bot cookies!)
        api_result = page.evaluate("""async () => {
            const urls = [
                'https://shopee.co.id/api/v4/item/get?itemid=24040756220&shopid=277711630',
                'https://shopee.co.id/api/v4/pdp/get_pc?item_id=24040756220&shop_id=277711630'
            ];
            const results = {};
            for (const u of urls) {
                try {
                    const res = await fetch(u, {
                        headers: {
                            'Accept': 'application/json',
                            'x-api-source': 'pc'
                        }
                    });
                    results[u] = await res.json();
                } catch(e) {
                    results[u] = { error: e.toString() };
                }
            }
            return results;
        }""")
        
        with open("fetched_api_result.json", "w", encoding="utf-8") as f:
            json.dump(api_result, f, indent=2)
            
        with open("captured_shopee_responses.json", "w", encoding="utf-8") as f:
            json.dump(captured_data, f, indent=2)
            
        try:
            ld_json = page.evaluate("""() => {
                const scripts = Array.from(document.querySelectorAll('script[type="application/ld+json"]'));
                return scripts.map(s => {
                    try { return JSON.parse(s.innerText); } catch(e) { return null; }
                }).filter(Boolean);
            }""")
            with open("shopee_ld_json.json", "w", encoding="utf-8") as f:
                json.dump(ld_json, f, indent=2)
        except Exception as e:
            print("Error ld_json:", e)

        page.screenshot(path="shopee_screen.png")
        print("Final title:", page.title())
        print("Final URL:", page.url)
        browser.close()

if __name__ == "__main__":
    inspect_shopee()
