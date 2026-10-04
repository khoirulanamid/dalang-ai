import os
import sys
import json
import time
import httpx
from datetime import datetime, timezone
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional
from playwright.sync_api import sync_playwright

@dataclass(frozen=True)
class Money:
    amount: float
    currency: str = "IDR"

    def __post_init__(self):
        if self.amount < 0:
            raise ValueError("Amount cannot be negative")
        if not self.currency or len(self.currency) != 3:
            raise ValueError("Currency must be a 3-letter ISO code")

@dataclass(frozen=True)
class ProductSpecification:
    name: str
    value: str

    def __post_init__(self):
        if not self.name.strip():
            raise ValueError("Specification name cannot be empty")

@dataclass(frozen=True)
class ProductMedia:
    url: str
    local_path: str
    is_cover: bool = False
    media_type: str = "image"

@dataclass
class ProductCampaignMetadata:
    item_id: str
    shop_id: str
    title: str
    description: str
    price: Money
    original_price: Optional[Money]
    discount_percentage: Optional[int]
    stock: int
    sold_count: Optional[str]
    rating_star: Optional[float]
    shop_name: Optional[str]
    shop_location: Optional[str]
    specifications: List[ProductSpecification]
    media_assets: List[ProductMedia]
    source_url: str
    canonical_url: str
    extracted_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item_id": self.item_id,
            "shop_id": self.shop_id,
            "title": self.title,
            "description": self.description,
            "price": {
                "amount": self.price.amount,
                "currency": self.price.currency,
                "formatted": f"{self.price.currency} {int(self.price.amount):,}"
            },
            "original_price": {
                "amount": self.original_price.amount,
                "currency": self.original_price.currency,
                "formatted": f"{self.original_price.currency} {int(self.original_price.amount):,}"
            } if self.original_price else None,
            "discount_percentage": self.discount_percentage,
            "stock": self.stock,
            "sold_count": self.sold_count,
            "rating_star": self.rating_star,
            "shop": {
                "name": self.shop_name,
                "location": self.shop_location
            },
            "specifications": [{"name": s.name, "value": s.value} for s in self.specifications],
            "media_assets": [
                {
                    "url": m.url,
                    "local_path": m.local_path,
                    "is_cover": m.is_cover,
                    "media_type": m.media_type
                } for m in self.media_assets
            ],
            "source_url": self.source_url,
            "canonical_url": self.canonical_url,
            "extracted_at": self.extracted_at
        }


def download_media_file(url: str, output_path: Path) -> bool:
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Referer": "https://shopee.co.id/"
        }
        with httpx.Client(timeout=30.0, follow_redirects=True, headers=headers) as client:
            resp = client.get(url)
            if resp.status_code == 200 and len(resp.content) > 1000:
                output_path.parent.mkdir(parents=True, exist_ok=True)
                output_path.write_bytes(resp.content)
                return True
    except Exception as e:
        print(f"Failed to download {url}: {e}", file=sys.stderr)
    return False


def crawl_shopee_product(short_url: str, output_images_dir: Path, output_metadata_path: Path):
    captured_responses = []

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-blink-features=AutomationControlled"
            ]
        )
        context = browser.new_context(
            viewport={"width": 1440, "height": 900},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        def handle_response(response):
            if any(endpoint in response.url for endpoint in ["/api/v4/item/get", "/api/v2/item/get", "/api/v4/pdp/get_pc", "api/v4/item/get_all"]):
                try:
                    data = response.json()
                    captured_responses.append({"url": response.url, "data": data})
                except Exception:
                    pass

        page.on("response", handle_response)

        print(f"Navigating to shortlink: {short_url}")
        page.goto(short_url, wait_until="domcontentloaded", timeout=60000)
        
        # Wait for redirect and dynamic rendering
        page.wait_for_timeout(7000)
        
        final_url = page.url
        print(f"Final resolved URL: {final_url}")
        
        # Scroll down gradually to trigger lazy-loaded specifications and images
        for scroll_y in [500, 1000, 1500, 2000, 1000, 0]:
            page.evaluate(f"window.scrollTo(0, {scroll_y})")
            page.wait_for_timeout(1000)

        # Extract DOM data if API not fully captured
        dom_title = ""
        dom_price = ""
        dom_specs = []
        dom_images = []
        dom_description = ""

        try:
            # Title
            title_elem = page.query_selector("div.attM6q, span._44qnta, h1, div.WBVL_7")
            if title_elem:
                dom_title = title_elem.inner_text().strip()
        except Exception:
            pass

        # Try to inspect page HTML or preloaded scripts
        page_html = page.content()
        Path("shopee_page_dump.html").write_text(page_html, encoding="utf-8")

        # Let's see if we captured API response
        api_data = None
        for item in captured_responses:
            d = item["data"].get("data") or item["data"]
            if isinstance(d, dict) and ("name" in d or "item" in d or "item_id" in d):
                api_data = d
                break

        print(f"Captured responses count: {len(captured_responses)}")
        if captured_responses:
            for i, r in enumerate(captured_responses):
                Path(f"api_response_{i}.json").write_text(json.dumps(r["data"], indent=2), encoding="utf-8")

        # Evaluate client-side data
        client_eval = page.evaluate("""() => {
            let res = {
                title: document.title,
                images: [],
                specs: [],
                price: null,
                sold: null,
                rating: null,
                desc: null
            };
            
            // Try extracting images from carousel or product gallery
            const imgEls = document.querySelectorAll('img');
            imgEls.forEach(img => {
                let src = img.src || img.getAttribute('src') || '';
                if (src.includes('susercontent.com') && !src.includes('profile') && !src.includes('avatar')) {
                    res.images.push(src);
                }
            });
            
            // Try extracting title
            const h1 = document.querySelector('h1, span._44qnta, div.attM6q, div.WBVL_7');
            if (h1) res.title = h1.innerText;

            // Try extracting price
            const priceEl = document.querySelector('div.pqTWkA, div.G27Shz, div._3n5z6N');
            if (priceEl) res.price = priceEl.innerText;

            // Try specs
            const specRows = document.querySelectorAll('div.page-product__item-wrapper, div.a11y-specs, div.k77Vo2, div.SK_i_K');
            specRows.forEach(row => {
                res.specs.push(row.innerText);
            });

            return res;
        }""")

        browser.close()

    return final_url, captured_responses, client_eval

if __name__ == "__main__":
    url = "https://s.shopee.co.id/6L4wk65TN6"
    img_dir = Path("workspace/product_images/sprint26")
    meta_path = Path("docs/sprint26_campaign.json")
    
    final_url, captured, client_eval = crawl_shopee_product(url, img_dir, meta_path)
    print("Evaluation done. Result summary:")
    print("Resolved URL:", final_url)
    print("Captured API count:", len(captured))
    print("Client eval title:", client_eval.get("title"))
    print("Client eval images found:", len(client_eval.get("images", [])))
