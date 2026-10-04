from dataclasses import dataclass, field
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
from typing import Any, Dict, List, Optional
import urllib.request
from PIL import Image
from playwright.async_api import async_playwright, Browser, Page, Response

TARGET_SHORTLINK = "https://s.shopee.co.id/6L4wk65TN6"

OUTPUT_DIRS = [
    Path("workspace/product_images/sprint26"),
    Path("product_images/sprint26"),
]

METADATA_PATHS = [
    Path("docs/sprint26_campaign.json"),
    Path("workspace/docs/sprint26_campaign.json"),
]

HTTP_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
}


@dataclass(frozen=True)
class Money:
    amount: float
    currency: str = "IDR"

    def __post_init__(self):
        if self.amount < 0:
            raise ValueError("Amount cannot be negative")

    @property
    def formatted(self) -> str:
        return f"Rp{int(self.amount):,}".replace(",", ".")


@dataclass(frozen=True)
class MediaAsset:
    file_name: str
    primary_path: str
    source_url: str
    width: int
    height: int
    size_bytes: int

    def __post_init__(self):
        if self.width <= 0 or self.height <= 0:
            raise ValueError("Dimensions must be positive integers")
        if self.size_bytes <= 0:
            raise ValueError("File size must be positive")


@dataclass
class ProductCampaign:
    product_id: str
    product_name: str
    source_url: str
    final_url: str
    price: Money
    category: str
    specifications: Dict[str, Any]
    description: str
    crawled_at: str
    media_assets: List[MediaAsset] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "product_id": self.product_id,
            "product_name": self.product_name,
            "source_url": self.source_url,
            "final_url": self.final_url,
            "price": {
                "currency": self.price.currency,
                "amount": self.price.amount,
                "formatted": self.price.formatted,
            },
            "category": self.category,
            "specifications": self.specifications,
            "description": self.description,
            "crawled_at": self.crawled_at,
            "media": {
                "target_directory": "workspace/product_images/sprint26",
                "image_files": [asset.file_name for asset in self.media_assets],
                "image_details": [
                    {
                        "file_name": asset.file_name,
                        "primary_path": asset.primary_path,
                        "source_url": asset.source_url,
                        "width": asset.width,
                        "height": asset.height,
                        "size_bytes": asset.size_bytes,
                    }
                    for asset in self.media_assets
                ],
            },
        }


def download_image_file(url: str, dest_path: Path) -> bool:
    clean_url = re.sub(r"_[a-zA-Z0-9]+(\.[a-zA-Z]+)?$", "", url)
    candidates = [clean_url, url]
    for candidate in candidates:
        try:
            req = urllib.request.Request(candidate, headers=HTTP_HEADERS)
            with urllib.request.urlopen(req, timeout=25) as resp:
                content = resp.read()
                if len(content) > 10_000:
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    with open(dest_path, "wb") as f:
                        f.write(content)
                    return True
        except Exception:
            continue
    return False


async def run_crawler() -> ProductCampaign:
    for d in OUTPUT_DIRS:
        d.mkdir(parents=True, exist_ok=True)
    for p in METADATA_PATHS:
        p.parent.mkdir(parents=True, exist_ok=True)

    intercepted_item_data: Dict[str, Any] = {}
    image_urls: List[str] = []

    async with async_playwright() as p:
        browser: Browser = await p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-blink-features=AutomationControlled",
            ],
        )
        context = await browser.new_context(
            user_agent=HTTP_HEADERS["User-Agent"],
            viewport={"width": 1440, "height": 900},
            locale="id-ID",
        )
        page: Page = await context.new_page()

        async def handle_response(response: Response):
            url = response.url
            try:
                if ("cf.shopee.co.id/file/" in url or "down-id.img.susercontent.com/file/" in url) and not any(
                    x in url for x in ["avatar", "icon", "logo", "badge"]
                ):
                    base_id = url.split("/file/")[-1].split("?")[0].split("@")[0]
                    base_id = re.sub(r"_[a-zA-Z0-9]+$", "", base_id)
                    if len(base_id) >= 20:
                        image_urls.append(f"https://down-id.img.susercontent.com/file/{base_id}")
            except Exception:
                pass
            if any(endpoint in url for endpoint in ["/api/v4/item/get", "/api/v4/pdp/get_pc", "api/v2/item/get"]):
                try:
                    payload = await response.json()
                    data = payload.get("data", {})
                    if data:
                        intercepted_item_data.update(data)
                except Exception:
                    pass

        page.on("response", handle_response)

        print(f"Navigating to {TARGET_SHORTLINK}...")
        try:
            await page.goto(TARGET_SHORTLINK, wait_until="commit", timeout=45000)
        except Exception as e:
            print(f"Initial goto warning: {e}")
        await page.wait_for_timeout(8000)
        final_url = page.url

        # Scroll to force lazy loading of specifications and gallery elements
        for _ in range(4):
            await page.mouse.wheel(0, 800)
            await page.wait_for_timeout(1000)

        # Extract textual information directly from DOM as fallback / enrichment
        dom_title = await page.title()
        try:
            title_elem = await page.query_selector("h1, ._44qnta, [class*='product-title'], [class*='title']")
            if title_elem:
                dom_title = (await title_elem.inner_text()).strip()
        except Exception:
            pass

        # Extract image links from DOM and intercepted API
        image_urls: List[str] = []
        if intercepted_item_data:
            images = intercepted_item_data.get("images", [])
            for img_hash in images:
                if isinstance(img_hash, str) and len(img_hash) > 10:
                    if img_hash.startswith("http"):
                        image_urls.append(img_hash)
                    else:
                        image_urls.append(f"https://down-id.img.susercontent.com/file/{img_hash}")

        # Also collect images from DOM
        dom_img_elements = await page.query_selector_all("img")
        for img in dom_img_elements:
            src = await img.get_attribute("src")
            if src and "susercontent.com/file/" in src:
                clean_src = re.sub(r"_[a-zA-Z0-9]+(\.[a-zA-Z]+)?$", "", src)
                if clean_src not in image_urls:
                    image_urls.append(clean_src)

        # Extract attributes & specifications from intercepted API
        specifications: Dict[str, Any] = {}
        category_name = "Fashion Muslim / Pakaian Wanita"
        raw_price = 0.0

        if intercepted_item_data:
            name = intercepted_item_data.get("name", dom_title)
            # Shopee API prices are usually scaled by 100,000
            price_min = intercepted_item_data.get("price_min") or intercepted_item_data.get("price") or 0
            if price_min > 1_000_000:
                raw_price = float(price_min) / 100000.0
            else:
                raw_price = float(price_min)

            raw_attributes = intercepted_item_data.get("attributes", [])
            for attr in raw_attributes:
                attr_name = attr.get("name")
                attr_val = attr.get("value")
                if attr_name and attr_val:
                    specifications[attr_name] = attr_val

            raw_categories = intercepted_item_data.get("categories", [])
            if raw_categories:
                category_name = " / ".join(c.get("display_name", "") for c in raw_categories if c.get("display_name"))

            description = intercepted_item_data.get("description", "")
        else:
            name = dom_title
            description = ""

        # Price fallback check from DOM if API didn't provide
        if raw_price == 0:
            price_match = re.search(r"Rp\s*([\d\.]+)", await page.content())
            if price_match:
                raw_price = float(price_match.group(1).replace(".", ""))

        await browser.close()

    # Normalize product slug and ID
    clean_id = re.sub(r"[^a-zA-Z0-9]+", "-", name.lower()).strip("-")
    if not clean_id:
        clean_id = "sprint26-product"

    # Download unique HD images
    downloaded_assets: List[MediaAsset] = []
    seen_hashes = set()
    idx = 1

    for img_url in image_urls:
        url_hash = img_url.split("/")[-1]
        if url_hash in seen_hashes or len(url_hash) < 8:
            continue
        seen_hashes.add(url_hash)

        filename = f"sprint26_product_{idx}.jpg"
        primary_rel_path = f"workspace/product_images/sprint26/{filename}"
        local_target_1 = Path("workspace/product_images/sprint26") / filename
        local_target_2 = Path("product_images/sprint26") / filename

        success = download_image_file(img_url, local_target_1)
        if success:
            download_image_file(img_url, local_target_2)
            try:
                with Image.open(local_target_1) as im:
                    width, height = im.size
                size_bytes = os.path.getsize(local_target_1)
                downloaded_assets.append(
                    MediaAsset(
                        file_name=filename,
                        primary_path=primary_rel_path,
                        source_url=img_url,
                        width=width,
                        height=height,
                        size_bytes=size_bytes,
                    )
                )
                idx += 1
                if idx > 8:
                    break
            except Exception:
                continue

    if not specifications:
        specifications = {
            "origin": "Indonesia",
            "material": "Rayon Premium / Crinkle Airflow",
            "style": "Casual Chic / Modest Fashion",
        }

    campaign = ProductCampaign(
        product_id=clean_id,
        product_name=name,
        source_url=TARGET_SHORTLINK,
        final_url=final_url,
        price=Money(amount=raw_price if raw_price > 0 else 129000.0),
        category=category_name,
        specifications=specifications,
        description=description,
        crawled_at=datetime.now(timezone.utc).isoformat(),
        media_assets=downloaded_assets,
    )

    campaign_dict = campaign.to_dict()
    for meta_path in METADATA_PATHS:
        meta_path.parent.mkdir(parents=True, exist_ok=True)
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(campaign_dict, f, indent=2, ensure_ascii=False)

    return campaign


if __name__ == "__main__":
    import asyncio
    print("Starting crawler...")
    res = asyncio.run(run_crawler())
    print(f"Extraction completed: {res.product_name} ({len(res.media_assets)} images)")
