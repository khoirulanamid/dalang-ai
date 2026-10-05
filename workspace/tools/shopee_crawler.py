from dataclasses import dataclass, field
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import sys
from typing import Any, Dict, List, Optional
import httpx
from playwright.sync_api import sync_playwright, Response

@dataclass(frozen=True)
class PriceRange:
    currency: str
    original_min: float
    original_max: float
    current_min: float
    current_max: float

    def __post_init__(self):
        if self.current_min < 0 or self.current_max < 0:
            raise ValueError("Price values must be non-negative")
        if self.current_min > self.current_max:
            raise ValueError("Minimum price cannot exceed maximum price")

@dataclass(frozen=True)
class ProductSpecification:
    name: str
    value: str

@dataclass(frozen=True)
class ProductMedia:
    image_id: str
    url: str
    local_path: Optional[str] = None

@dataclass
class ProductDetails:
    item_id: str
    shop_id: str
    title: str
    price: PriceRange
    description: str
    specifications: List[ProductSpecification]
    media_items: List[ProductMedia]
    canonical_url: str
    source_url: str
    extracted_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_projection(self) -> Dict[str, Any]:
        return {
            "item_id": self.item_id,
            "shop_id": self.shop_id,
            "title": self.title,
            "canonical_url": self.canonical_url,
            "source_url": self.source_url,
            "price": {
                "currency": self.price.currency,
                "original_min": self.price.original_min,
                "original_max": self.price.original_max,
                "current_min": self.price.current_min,
                "current_max": self.price.current_max,
                "display_price": f"{self.price.currency} {int(self.price.current_min):,}".replace(",", "."),
            },
            "description": self.description,
            "specifications": [
                {"name": s.name, "value": s.value} for s in self.specifications
            ],
            "media": [
                {
                    "image_id": m.image_id,
                    "url": m.url,
                    "local_path": m.local_path,
                }
                for m in self.media_items
            ],
            "extracted_at": self.extracted_at,
        }

class ShopeeCrawler:
    def __init__(self, output_dir: Path, metadata_paths: List[Path]):
        self.output_dir = output_dir
        self.metadata_paths = metadata_paths
        self.output_dir.mkdir(parents=True, exist_ok=True)
        for p in self.metadata_paths:
            p.parent.mkdir(parents=True, exist_ok=True)
        self.api_payloads: List[Dict[str, Any]] = []

    def _handle_response(self, response: Response):
        url = response.url
        if any(keyword in url for keyword in ["/api/v4/item/get", "/api/v2/item/get", "/api/v4/pdp/get_item"]):
            try:
                data = response.json()
                if data:
                    self.api_payloads.append(data)
            except Exception:
                pass

    def crawl_product(self, short_url: str) -> ProductDetails:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-blink-features=AutomationControlled",
                ],
            )
            context = browser.new_context(
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/123.0.0.0 Safari/537.36"
                ),
                viewport={"width": 1920, "height": 1080},
                locale="id-ID",
            )
            page = context.new_page()
            page.on("response", self._handle_response)

            page.goto(short_url, wait_until="networkidle", timeout=60000)
            page.wait_for_timeout(5000)

            final_url = page.url

            # Extract from captured API or page DOM
            product = self._parse_from_api_or_dom(page, short_url, final_url)
            browser.close()
            return product

    def _parse_from_api_or_dom(self, page, short_url: str, final_url: str) -> ProductDetails:
        item_data = None
        for payload in self.api_payloads:
            if "data" in payload and isinstance(payload["data"], dict):
                d = payload["data"]
                if "item" in d:
                    item_data = d["item"]
                    break
                elif "name" in d and ("price" in d or "price_min" in d):
                    item_data = d
                    break

        title = ""
        description = ""
        item_id = ""
        shop_id = ""
        price_min = 0.0
        price_max = 0.0
        orig_min = 0.0
        orig_max = 0.0
        specs: List[ProductSpecification] = []
        images: List[str] = []

        if item_data:
            title = item_data.get("name", "")
            description = item_data.get("description", "")
            item_id = str(item_data.get("itemid", ""))
            shop_id = str(item_data.get("shopid", ""))

            # Shopee API prices are usually scaled by 100000
            scale = 100000.0 if item_data.get("price", 0) > 10000000 else 1.0
            price_min = float(item_data.get("price_min", item_data.get("price", 0))) / scale
            price_max = float(item_data.get("price_max", item_data.get("price", 0))) / scale
            orig_min = float(item_data.get("price_min_before_discount", item_data.get("price_before_discount", price_min))) / scale
            orig_max = float(item_data.get("price_max_before_discount", item_data.get("price_before_discount", price_max))) / scale

            for attr in item_data.get("attributes", []):
                attr_name = attr.get("name", "")
                attr_val = attr.get("value", "")
                if attr_name and attr_val:
                    specs.append(ProductSpecification(name=str(attr_name), value=str(attr_val)))

            images = item_data.get("images", [])

        if not title:
            # Fallback DOM evaluation
            title = page.title()
            # Clean page title
            title = re.sub(r"\s*\|\s*Shopee Indonesia.*$", "", title).strip()

        if not description:
            try:
                desc_el = page.locator(".f8dp7t, .product-detail__description, .page-product__description").first
                if desc_el.count() > 0:
                    description = desc_el.text_content().strip()
            except Exception:
                pass

        if not specs:
            try:
                spec_rows = page.locator(".G27akf, .item-attribute, .e8lZp3").all()
                for row in spec_rows:
                    text = row.text_content().strip()
                    parts = text.split("\n")
                    if len(parts) >= 2:
                        specs.append(ProductSpecification(name=parts[0].strip(), value=parts[1].strip()))
            except Exception:
                pass

        if not images:
            try:
                img_els = page.locator("img").all()
                for img in img_els:
                    src = img.get_attribute("src") or ""
                    if "down-id.img.susercontent.com" in src or "cf.shopee.co.id/file" in src:
                        # Extract hash
                        match = re.search(r"/file/([a-zA-Z0-9_-]+)", src)
                        if match and match.group(1) not in images:
                            images.append(match.group(1))
            except Exception:
                pass

        # Parse ID from final URL if missing
        if not item_id or not shop_id:
            id_match = re.search(r"-i\.(\d+)\.(\d+)", final_url)
            if id_match:
                shop_id = shop_id or id_match.group(1)
                item_id = item_id or id_match.group(2)

        price = PriceRange(
            currency="IDR",
            original_min=orig_min if orig_min > 0 else price_min,
            original_max=orig_max if orig_max > 0 else price_max,
            current_min=price_min,
            current_max=price_max,
        )

        media_items = []
        for img_id in images:
            # HD image URL template
            hd_url = f"https://down-id.img.susercontent.com/file/{img_id}"
            media_items.append(ProductMedia(image_id=img_id, url=hd_url))

        return ProductDetails(
            item_id=item_id,
            shop_id=shop_id,
            title=title,
            price=price,
            description=description,
            specifications=specs,
            media_items=media_items,
            canonical_url=final_url,
            source_url=short_url,
        )

    def download_media(self, product: ProductDetails) -> ProductDetails:
        updated_media = []
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/123.0.0.0 Safari/537.36"
            ),
            "Referer": "https://shopee.co.id/",
        }

        with httpx.Client(headers=headers, timeout=30.0, follow_redirects=True) as client:
            for idx, media in enumerate(product.media_items):
                file_ext = "jpg"
                filename = f"product_{idx + 1:02d}_{media.image_id[:10]}.{file_ext}"
                target_path = self.output_dir / filename

                try:
                    res = client.get(media.url)
                    if res.status_code == 200:
                        target_path.write_bytes(res.content)
                        updated_media.append(
                            ProductMedia(
                                image_id=media.image_id,
                                url=media.url,
                                local_path=str(target_path),
                            )
                        )
                    else:
                        updated_media.append(media)
                except Exception as err:
                    print(f"Error downloading {media.url}: {err}", file=sys.stderr)
                    updated_media.append(media)

        product.media_items = updated_media
        return product

    def save_metadata(self, product: ProductDetails):
        projection = product.to_projection()
        payload_str = json.dumps(projection, indent=2, ensure_ascii=False)
        for p in self.metadata_paths:
            p.write_text(payload_str, encoding="utf-8")
        print(f"Metadata saved successfully across {len(self.metadata_paths)} targets.")
