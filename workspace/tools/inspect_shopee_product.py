import asyncio
import json
from playwright.async_api import async_playwright

async def inspect_details():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-blink-features=AutomationControlled",
                "--window-size=1920,1080"
            ]
        )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
            locale="id-ID",
            timezone_id="Asia/Jakarta",
        )
        await context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            window.navigator.chrome = { runtime: {} };
            Object.defineProperty(navigator, 'languages', { get: () => ['id-ID', 'id', 'en-US', 'en'] });
            Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
        """)

        page = await context.new_page()

        print("Navigating...")
        await page.goto("https://s.shopee.co.id/8AWbWHUOPx", wait_until="domcontentloaded")

        for _ in range(15):
            await page.wait_for_timeout(1000)
            if "product" in page.url and "verify" not in page.url:
                await page.wait_for_timeout(5000)
                break

        print("Page URL:", page.url)
        print("Page Title:", await page.title())

        # Scroll to load description and specs
        await page.evaluate("window.scrollBy(0, 1000)")
        await page.wait_for_timeout(2000)
        await page.evaluate("window.scrollBy(0, 1000)")
        await page.wait_for_timeout(2000)

        # Extract data from page
        data = await page.evaluate("""() => {
            const res = {};
            // Title
            const h1 = document.querySelector('h1') || document.querySelector('._44qnta') || document.querySelector('.WB8f5Q');
            res.title = h1 ? h1.innerText.trim() : document.title;

            // Price elements
            const priceEls = Array.from(document.querySelectorAll('div, span')).filter(el => {
                const text = el.innerText ? el.innerText.trim() : '';
                return text.startsWith('Rp') && text.length < 35 && el.children.length === 0;
            }).map(el => el.innerText.trim());
            res.prices_found = Array.from(new Set(priceEls));

            // Specs
            res.specs = {};
            const specLabels = document.querySelectorAll('label, ._0b72j6, .O94TvD, .G6u6EG label');
            // Try to find specification container
            const allElements = document.querySelectorAll('*');
            for (let el of allElements) {
                if (el.innerText && el.innerText.includes('Spesifikasi Produk')) {
                    res.spec_section_text = el.innerText.slice(0, 2000);
                    break;
                }
            }

            // Description
            for (let el of allElements) {
                if (el.innerText && el.innerText.includes('Deskripsi Produk')) {
                    res.desc_section_text = el.innerText.slice(0, 3000);
                    break;
                }
            }

            // All image sources
            const imgs = Array.from(document.querySelectorAll('img'))
                .map(i => i.src)
                .filter(src => src && (src.includes('susercontent.com') || src.includes('shopee.co.id')));
            res.images = Array.from(new Set(imgs));

            // Background images
            const bgEls = Array.from(document.querySelectorAll('*'))
                .map(el => window.getComputedStyle(el).backgroundImage)
                .filter(bg => bg && bg.includes('susercontent.com'))
                .map(bg => {
                    const match = bg.match(/url\\(["']?([^"']+)["']?\\)/);
                    return match ? match[1] : null;
                }).filter(Boolean);
            res.bg_images = Array.from(new Set(bgEls));

            return res;
        }""")

        with open("tools/extracted_dom_data.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"Title: {data.get('title')}")
        print(f"Prices found: {data.get('prices_found')}")
        print(f"Images count: {len(data.get('images', []))}")
        print(f"Bg images count: {len(data.get('bg_images', []))}")
        print(f"Spec section sample: {str(data.get('spec_section_text'))[:300]}")
        print(f"Desc section sample: {str(data.get('desc_section_text'))[:300]}")

        await page.screenshot(path="tools/shopee_product_view.png", full_page=True)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(inspect_details())
