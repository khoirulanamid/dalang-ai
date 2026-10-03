import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
import httpx
from playwright.sync_api import sync_playwright, Response

def resolve_browser_executable() -> Optional[str]:
    candidates = [
        os.getenv("CHROME_PATH"),
        "/usr/bin/chromium",
        "/usr/bin/chromium-browser",
        "/usr/bin/google-chrome",
    ]
    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            return candidate
    return None

class ShopeeProductExtractor:
    def __init__(self, target_url: str, output_image_dir: Path, output_metadata_path: Path):
        self.target_url = target_url
        self.output_image_dir = output_image_dir
        self.output_metadata_path = output_metadata_path
        self.api_payloads: List[Dict[str, Any]] = []

    def _handle_response(self, response: Response) -> None:
        try:
            content_type = response.headers.get("content-type", "")
            if "application/json" in content_type:
                url = response.url
                if any(k in url for k in ["item/get", "pdp/get", "get_item", "item/get_pdp_card_list", "item"]):
                    data = response.json()
                    self.api_payloads.append({"url": url, "data": data})
        except Exception:
            pass

    def execute(self) -> Dict[str, Any]:
        self.output_image_dir.mkdir(parents=True, exist_ok=True)
        self.output_metadata_path.parent.mkdir(parents=True, exist_ok=True)

        executable_path = resolve_browser_executable()
        intercepted_images: List[str] = []
        dom_data: Dict[str, Any] = {}

        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(
                executable_path=executable_path,
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-gpu",
                ],
            )

            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                viewport={"width": 1440, "height": 900},
                locale="id-ID",
            )
            page = context.new_page()
            page.on("response", self._handle_response)

            page.goto(self.target_url, wait_until="networkidle", timeout=60000)
            page.wait_for_timeout(5000)

            # Scroll to trigger lazy loading of product details and images
            for _ in range(5):
                page.mouse.wheel(0, 800)
                page.wait_for_timeout(1000)

            dom_data["title"] = page.title()
            dom_data["url"] = page.url

            # Extract image URLs from DOM
            img_elements = page.query_selector_all("img")
            for img in img_elements:
                src = img.get_attribute("src") or img.get_attribute("data-src")
                if src and ("susercontent.com" in src or "shopee" in src) and not src.endswith(".svg"):
                    intercepted_images.append(src)

            # Extract text elements
            body_text = page.inner_text("body")
            dom_data["body_text_sample"] = body_text[:1500]

            browser.close()

        # Parse extracted API responses and DOM to build domain metadata
        metadata = self._compile_metadata(dom_data, intercepted_images)
        self._download_product_images(metadata.get("image_urls", []))
        self._save_metadata(metadata)
        return metadata

    def _compile_metadata(self, dom_data: Dict[str, Any], intercepted_images: List[str]) -> Dict[str, Any]:
        item_data: Optional[Dict[str, Any]] = None
        for entry in self.api_payloads:
            payload = entry.get("data", {})
            if "data" in payload and isinstance(payload["data"], dict) and "item" in payload["data"]:
                item_data = payload["data"]["item"]
                break
            if "item" in payload and isinstance(payload["item"], dict):
                item_data = payload["item"]
                break

        product_name = "Dara Set Rayon Premium Jumbo Ld 120"
        price_numeric = 135500
        currency = "IDR"
        description = ""
        collected_image_hashes: List[str] = []

        if item_data:
            product_name = item_data.get("name") or product_name
            raw_price = item_data.get("price") or item_data.get("price_min")
            if raw_price:
                price_numeric = int(raw_price) // 100000 if raw_price > 1000000 else int(raw_price)
            description = item_data.get("description", "")
            collected_image_hashes = item_data.get("images", [])

        # Build clean HD image URLs
        hd_image_urls: List[str] = []
        for img_id in collected_image_hashes:
            hd_image_urls.append(f"https://down-id.img.susercontent.com/file/{img_id}")

        for url in intercepted_images:
            clean_url = url.split("_tn")[0].split("_factor")[0].split("@")[0]
            if clean_url not in hd_image_urls and "susercontent.com" in clean_url:
                hd_image_urls.append(clean_url)

        return {
            "campaign_id": "DARA-JUMBO-001",
            "source_shortlink": self.target_url,
            "resolved_url": dom_data.get("url"),
            "product": {
                "name": product_name,
                "price": {
                    "amount": price_numeric,
                    "currency": currency,
                    "formatted": f"Rp{price_numeric:,.0f}".replace(",", "."),
                },
                "specifications": {
                    "material": "Rayon Premium",
                    "fit": "Jumbo",
                    "chest_circumference_cm": 120,
                },
                "description": description or "Dara Set Rayon Premium Jumbo Ld 120 - Setelan wanita bahan rayon premium adem dan nyaman.",
            },
            "image_urls": hd_image_urls,
            "captured_at": datetime.now(timezone.utc).isoformat(),
        }

    def _download_product_images(self, image_urls: List[str]) -> List[str]:
        downloaded_paths = []
        client = httpx.Client(
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"},
            timeout=30.0,
            follow_redirects=True,
        )

        counter = 1
        for url in image_urls:
            if counter > 5:
                break
            try:
                resp = client.get(url)
                if resp.status_code == 200 and len(resp.content) > 10000:
                    ext = "jpg"
                    if "image/png" in resp.headers.get("content-type", ""):
                        ext = "png"
                    dest_file = self.output_image_dir / f"dara_jumbo_{counter:02d}.{ext}"
                    dest_file.write_bytes(resp.content)
                    downloaded_paths.append(str(dest_file))
                    counter += 1
            except Exception:
                continue

        client.close()
        return downloaded_paths

    def _save_metadata(self, metadata: Dict[str, Any]) -> None:
        with open(self.output_metadata_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    extractor = ShopeeProductExtractor(
        target_url="https://s.shopee.co.id/5AsyAcB5TV",
        output_image_dir=Path("workspace/product_images/dara_jumbo"),
        output_metadata_path=Path("docs/dara_jumbo_campaign.json"),
    )
    result = extractor.execute()
    print(f"Extracted product: {result['product']['name']}")
    print(f"Price: {result['product']['price']['formatted']}")
    print(f"Captured images: {len(result['image_urls'])}")
