import os
import sys
import json
import time
import re
from pathlib import Path
from typing import Dict, Any, List, Optional
import httpx
from playwright.sync_api import sync_playwright

class ShopeeCrawler:
    def __init__(self, target_url: str, output_image_dir: Path, output_json_path: Path):
        self.target_url = target_url
        self.output_image_dir = output_image_dir
        self.output_json_path = output_json_path
        self.captured_item_data: Optional[Dict[str, Any]] = None
        self.captured_responses: List[Dict[str, Any]] = []

    def handle_response(self, response):
        try:
            url = response.url
            if "/api/v4/item/get" in url or "/api/v2/item/get" in url or "/api/v4/pdp/get_pc" in url:
                data = response.json()
                self.captured_responses.append({"url": url, "data": data})
                if "data" in data and ("item" in data["data"] or "name" in data["data"]):
                    self.captured_item_data = data["data"]
        except Exception:
            pass

    def run(self) -> Dict[str, Any]:
        self.output_image_dir.mkdir(parents=True, exist_ok=True)
        self.output_json_path.parent.mkdir(parents=True, exist_ok=True)

        extracted_metadata = {}

        with sync_playwright() as p:
            user_agent = (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            )
            browser = p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-dev-shm-usage"])
            context = browser.new_context(
                user_agent=user_agent,
                viewport={"width": 1920, "height": 1080},
                locale="id-ID"
            )
            page = context.new_page()
            page.on("response", self.handle_response)

            print(f"Navigating to: {self.target_url}")
            page.goto(self.target_url, wait_until="networkidle", timeout=60000)
            page.wait_for_timeout(5000)

            # Scroll down to trigger lazy loading of specifications and images
            for i in range(5):
                page.mouse.wheel(0, 800)
                page.wait_for_timeout(1000)

            final_url = page.url
            print(f"Final URL: {final_url}")

            # Extract from page DOM and scripts
            dom_data = page.evaluate("""() => {
                let title = document.querySelector('title') ? document.querySelector('title').innerText : '';
                let h1 = document.querySelector('h1') ? document.querySelector('h1').innerText : '';
                let productTitleElem = document.querySelector('div.vR6K34, span._44qnta, .product-briefing, h1');
                let productTitle = productTitleElem ? productTitleElem.innerText : (h1 || title);

                // Price extraction
                let priceElem = document.querySelector('div.G27akf, div.pqTWkA, .product-price, ._3n5NQx');
                let priceText = priceElem ? priceElem.innerText : '';

                // Specification extraction
                let specs = {};
                let specRows = document.querySelectorAll('div.page-product__item-info div, .items-center');
                document.querySelectorAll('label, span').forEach(el => {
                    let next = el.nextElementSibling;
                    if (next && el.innerText && el.innerText.length < 30 && next.innerText) {
                        specs[el.innerText.trim()] = next.innerText.trim();
                    }
                });

                // Images extraction
                let imgUrls = [];
                document.querySelectorAll('img').forEach(img => {
                    if (img.src && (img.src.includes('susercontent.com') || img.src.includes('shopeesz'))) {
                        imgUrls.push(img.src);
                    }
                });

                // Description
                let descElem = document.querySelector('div.page-product__description, div.product-detail, div.f7AU53');
                let description = descElem ? descElem.innerText : '';

                // JSON-LD
                let jsonLdScripts = Array.from(document.querySelectorAll('script[type="application/ld+json"]')).map(s => s.innerText);

                return {
                    title: productTitle,
                    price: priceText,
                    specs: specs,
                    imgUrls: imgUrls,
                    description: description,
                    jsonLdScripts: jsonLdScripts,
                    bodyText: document.body.innerText.slice(0, 4000)
                };
            }""")

            browser.close()

        # Parse captured API data or DOM data
        product_info = self._aggregate_product_info(dom_data, final_url)
        
        # Download images
        downloaded_images = self._download_images(product_info["image_urls"])
        product_info["local_images"] = downloaded_images

        # Save metadata to JSON
        with open(self.output_json_path, "w", encoding="utf-8") as f:
            json.dump(product_info, f, indent=2, ensure_ascii=False)
        print(f"Saved campaign metadata to {self.output_json_path}")

        # Also mirror to alternate path if needed
        alt_json = Path("docs/sprint30_campaign.json")
        if self.output_json_path.resolve() != alt_json.resolve():
            alt_json.parent.mkdir(parents=True, exist_ok=True)
            with open(alt_json, "w", encoding="utf-8") as f:
                json.dump(product_info, f, indent=2, ensure_ascii=False)

        return product_info

    def _aggregate_product_info(self, dom_data: Dict[str, Any], final_url: str) -> Dict[str, Any]:
        item = {}
        if self.captured_item_data:
            item = self.captured_item_data.get("item", self.captured_item_data)

        # Try to parse JSON-LD
        json_ld_obj = {}
        for script_str in dom_data.get("jsonLdScripts", []):
            try:
                parsed = json.loads(script_str)
                if isinstance(parsed, dict) and parsed.get("@type") == "Product":
                    json_ld_obj = parsed
                    break
            except Exception:
                pass

        # Extract title
        title = (
            item.get("name") 
            or json_ld_obj.get("name") 
            or dom_data.get("title", "").replace(" | Shopee Indonesia", "").strip()
        )

        # Extract description
        description = (
            item.get("description")
            or json_ld_obj.get("description")
            or dom_data.get("description", "")
        )

        # Extract price
        price = None
        currency = "IDR"
        if "offers" in json_ld_obj:
            offers = json_ld_obj["offers"]
            if isinstance(offers, dict):
                price = offers.get("price")
                currency = offers.get("priceCurrency", "IDR")
            elif isinstance(offers, list) and len(offers) > 0:
                price = offers[0].get("price")
                currency = offers[0].get("priceCurrency", "IDR")

        if not price and "price" in item:
            # Shopee API prices are usually scaled by 100,000
            raw_price = item.get("price")
            price = raw_price / 100000 if raw_price > 1000000 else raw_price

        raw_price_str = dom_data.get("price", "")

        # Extract specifications / attributes
        specifications = {}
        if "attributes" in item and isinstance(item["attributes"], list):
            for attr in item["attributes"]:
                name = attr.get("name")
                val = attr.get("value")
                if name and val:
                    specifications[name] = val
        
        # Merge with DOM specs
        for k, v in dom_data.get("specs", {}).items():
            if k not in specifications and len(k) > 1 and len(v) > 0:
                specifications[k] = v

        # Extract high-definition images
        image_ids_or_urls = []
        if "images" in item and isinstance(item["images"], list):
            for img_id in item["images"]:
                image_ids_or_urls.append(f"https://down-id.img.susercontent.com/file/{img_id}")

        if not image_ids_or_urls and "image" in json_ld_obj:
            img = json_ld_obj["image"]
            if isinstance(img, list):
                image_ids_or_urls.extend(img)
            elif isinstance(img, str):
                image_ids_or_urls.append(img)

        for url in dom_data.get("imgUrls", []):
            if any(ext in url.lower() for ext in [".jpg", ".jpeg", ".png", ".webp"]) or "susercontent.com/file/" in url:
                # normalize Shopee CDN thumbnails to HD (remove _tn, _xs, etc.)
                clean_url = re.sub(r'_(?:tn|xs|m|sm|b).*?$', '', url)
                if clean_url not in image_ids_or_urls:
                    image_ids_or_urls.append(clean_url)

        # De-duplicate image URLs
        seen = set()
        clean_images = []
        for url in image_ids_or_urls:
            # Filter out non-product small icons
            if "shopeesz.com" in url and "favicon" in url:
                continue
            if url not in seen:
                seen.add(url)
                clean_images.append(url)

        return {
            "campaign_id": "sprint30",
            "source_shortlink": self.target_url,
            "final_url": final_url,
            "product_name": title,
            "price": price,
            "price_formatted": raw_price_str,
            "currency": currency,
            "specifications": specifications,
            "description": description,
            "image_urls": clean_images,
            "raw_dom_summary": {
                "body_preview": dom_data.get("bodyText", "")[:1000]
            }
        }

    def _download_images(self, image_urls: List[str]) -> List[str]:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0.0.0 Safari/537.36",
            "Referer": "https://shopee.co.id/"
        }
        downloaded = []
        with httpx.Client(timeout=30.0, headers=headers, follow_redirects=True) as client:
            for idx, img_url in enumerate(image_urls):
                try:
                    res = client.get(img_url)
                    if res.status_code == 200 and len(res.content) > 1000:
                        # Determine extension
                        content_type = res.headers.get("content-type", "")
                        ext = ".jpg"
                        if "png" in content_type:
                            ext = ".png"
                        elif "webp" in content_type:
                            ext = ".webp"
                        
                        file_name = f"product_image_{idx + 1:02d}{ext}"
                        target_file = self.output_image_dir / file_name
                        with open(target_file, "wb") as f:
                            f.write(res.content)
                        downloaded.append(str(target_file))
                        print(f"Downloaded: {target_file} ({len(res.content)} bytes)")
                except Exception as e:
                    print(f"Failed to download image {img_url}: {e}")
        return downloaded

if __name__ == "__main__":
    url = "https://s.shopee.co.id/80DBs5lgX2"
    # Ensure both workspace/product_images/sprint30 and relative product_images/sprint30 exist
    base_dir = Path(__file__).resolve().parent.parent
    output_img_dir = base_dir / "workspace" / "product_images" / "sprint30"
    output_json = base_dir / "docs" / "sprint30_campaign.json"

    crawler = ShopeeCrawler(
        target_url=url,
        output_image_dir=output_img_dir,
        output_json_path=output_json
    )
    result = crawler.run()
    print("Execution completed successfully.")
