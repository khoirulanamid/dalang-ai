import asyncio
import json
import os
import re
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from PIL import Image
from playwright.async_api import Browser, Page, Response, async_playwright

TARGET_SHORTLINK = "https://s.shopee.co.id/20vxzX4Fx0"
OUTPUT_DIRS = [
    Path("workspace/product_images/sprint28"),
    Path("product_images/sprint28"),
]
METADATA_PATHS = [
    Path("docs/sprint28_campaign.json"),
    Path("workspace/docs/sprint28_campaign.json"),
]

HTTP_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
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
                "target_directory": "workspace/product_images/sprint28",
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
                    x in url for x in ["avatar", "icon", "logo", "badge", "sprite"]
                ):
                    base_id = url.split("/file/")[-1].split("?")[0].split("@")[0]
                    base_id = re.sub(r"_[a-zA-Z0-9]+$", "", base_id)
                    if len(base_id) >= 20:
                        image_urls.append(f"https://down-id.img.susercontent.com/file/{base_id}")
            except Exception:
                pass

            if any(endpoint in url for endpoint in ["/api/v4/item/get", "/api/v4/pdp/get_pc", "api/v2/item/get", "/api/v4/pdp/get"]):
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

        await page.wait_for_timeout(10000)
        final_url = page.url
        print(f"Landed on: {final_url}")

        for _ in range(5):
            await page.mouse.wheel(0, 800)
            await page.wait_for_timeout(1200)

        dom_title = await page.title()
        try:
            title_elem = await page.query_selector("h1, ._44qnta, [class*='product-title'], [class*='title'], [class*='pdp-title']")
            if title_elem:
                text_val = (await title_elem.inner_text()).strip()
                if text_val:
                    dom_title = text_val
        except Exception:
            pass

        if intercepted_item_data:
            images = intercepted_item_data.get("images", [])
            for img_hash in images:
                if isinstance(img_hash, str) and len(img_hash) > 10:
                    if img_hash.startswith("http"):
                        image_urls.append(img_hash)
                    else:
                        image_urls.append(f"https://down-id.img.susercontent.com/file/{img_hash}")

        dom_img_elements = await page.query_selector_all("img")
        for elem in dom_img_elements:
            src = await elem.get_attribute("src")
            if src and ("down-id.img.susercontent.com/file/" in src or "cf.shopee.co.id/file/" in src):
                clean_src = src.split("?")[0].split("@")[0]
                clean_src = re.sub(r"_[a-zA-Z0-9]+$", "", clean_src)
                if not any(x in clean_src for x in ["avatar", "icon", "logo", "badge"]):
                    image_urls.append(clean_src)

        name = dom_title
        raw_price = 0.0
        category_name = "Fashion Muslim / Atasan Wanita"
        specifications: Dict[str, Any] = {}
        description = ""

        if intercepted_item_data:
            name = intercepted_item_data.get("title") or intercepted_item_data.get("name") or dom_title
            price_val = (
                intercepted_item_data.get("price")
                or intercepted_item_data.get("price_min")
                or intercepted_item_data.get("show_free_shipping_price")
            )
            if price_val:
                raw_price = float(price_val) / 100000.0 if float(price_val) > 1_000_000 else float(price_val)

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

        page_content = await page.content()
        if raw_price == 0:
            price_matches = re.findall(r"Rp\s*([\d\.]+)", page_content)
            if price_matches:
                valid_prices = []
                for p_str in price_matches:
                    try:
                        val = float(p_str.replace(".", ""))
                        if 1000 <= val <= 10_000_000:
                            valid_prices.append(val)
                    except ValueError:
                        continue
                if valid_prices:
                    raw_price = valid_prices[0]

        if not specifications:
            script_tags = await page.query_selector_all('script[type="application/ld+json"]')
            for script in script_tags:
                try:
                    text_content = await script.inner_text()
                    ld_data = json.loads(text_content)
                    if isinstance(ld_data, dict):
                        if "name" in ld_data and (not name or name == dom_title):
                            name = ld_data["name"]
                        if "description" in ld_data and not description:
                            description = ld_data["description"]
                        if "offers" in ld_data and raw_price == 0:
                            offers = ld_data["offers"]
                            if isinstance(offers, dict) and "price" in offers:
                                raw_price = float(offers["price"])
                            elif isinstance(offers, list) and len(offers) > 0 and "price" in offers[0]:
                                raw_price = float(offers[0]["price"])
                        for key, val in ld_data.items():
                            if key not in ["@context", "@type", "offers", "image", "name", "description"]:
                                if isinstance(val, dict):
                                    specifications[key] = val.get("name")
                                elif isinstance(val, str):
                                    specifications[key] = val
                except Exception:
                    pass

        if " | Shopee Indonesia" in name:
            name = name.replace(" | Shopee Indonesia", "").strip()

        # Let's save a screenshot and raw content for debugging if needed
        await page.screenshot(path="tools/sprint28_debug_screenshot.png")
        with open("tools/sprint28_debug_page.html", "w", encoding="utf-8") as f:
            f.write(page_content)
        if intercepted_item_data:
            with open("tools/sprint28_intercepted_api.json", "w", encoding="utf-8") as f:
                json.dump(intercepted_item_data, f, indent=2, ensure_ascii=False)

        await browser.close()

    clean_id = re.sub(r"[^a-zA-Z0-9]+", "-", name.lower()).strip("-")
    if not clean_id:
        clean_id = "sprint28-product"

    downloaded_assets: List[MediaAsset] = []
    seen_hashes = set()
    idx = 1

    for img_url in image_urls:
        url_hash = img_url.split("/")[-1]
        if url_hash in seen_hashes or len(url_hash) < 8:
            continue
        seen_hashes.add(url_hash)

        filename = f"sprint28_product_{idx}.jpg"
        primary_rel_path = f"workspace/product_images/sprint28/{filename}"
        local_target_1 = Path("workspace/product_images/sprint28") / filename
        local_target_2 = Path("product_images/sprint28") / filename

        success = download_image_file(img_url, local_target_1)
        if success:
            download_image_file(img_url, local_target_2)
            try:
                with Image.open(local_target_1) as im:
                    width, height = im.size
                size_bytes = local_target_1.stat().st_size
                asset = MediaAsset(
                    file_name=filename,
                    primary_path=primary_rel_path,
                    source_url=img_url,
                    width=width,
                    height=height,
                    size_bytes=size_bytes,
                )
                downloaded_assets.append(asset)
                idx += 1
            except Exception as e:
                print(f"Skipping corrupted image {filename}: {e}")
                if local_target_1.exists():
                    local_target_1.unlink()
                if local_target_2.exists():
                    local_target_2.unlink()

    now_iso = datetime.now(timezone.utc).isoformat()
    campaign = ProductCampaign(
        product_id=clean_id,
        product_name=name,
        source_url=TARGET_SHORTLINK,
        final_url=final_url,
        price=Money(amount=raw_price if raw_price > 0 else 50000.0),
        category=category_name,
        specifications=specifications,
        description=description,
        crawled_at=now_iso,
        media_assets=downloaded_assets,
    )

    campaign_dict = campaign.to_dict()
    for meta_path in METADATA_PATHS:
        meta_path.parent.mkdir(parents=True, exist_ok=True)
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(campaign_dict, f, indent=2, ensure_ascii=False)

    return campaign


if __name__ == "__main__":
    print("Starting crawler for Sprint 28...")
    res = asyncio.run(run_crawler())
    print(f"Extraction completed: {res.product_name} ({len(res.media_assets)} images)")
