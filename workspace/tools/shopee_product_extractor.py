import asyncio
import json
import logging
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
import httpx
from playwright.async_api import async_playwright, BrowserContext, Page, Response

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("ShopeeProductExtractor")


class ProductMedia:
    def __init__(self, media_id: str, url: str, local_path: Optional[str] = None):
        self.media_id = media_id
        self.url = url
        self.local_path = local_path

    def to_dict(self) -> Dict[str, Any]:
        return {
            "media_id": self.media_id,
            "url": self.url,
            "local_path": self.local_path
        }


class ProductSpecification:
    def __init__(self, name: str, value: str):
        if not name or not value:
            raise ValueError("Specification name and value cannot be empty")
        self.name = name.strip()
        self.value = value.strip()

    def to_dict(self) -> Dict[str, str]:
        return {
            "name": self.name,
            "value": self.value
        }


class ShopeeProductDetail:
    def __init__(
        self,
        item_id: str,
        shop_id: str,
        title: str,
        price_min: float,
        price_max: float,
        currency: str,
        original_price: Optional[float],
        discount: Optional[str],
        description: str,
        specifications: List[ProductSpecification],
        images: List[ProductMedia],
        source_url: str,
        final_url: str,
        stock: Optional[int] = None,
        rating_star: Optional[float] = None,
        rating_count: Optional[int] = None,
        sold_count: Optional[int] = None,
        extracted_at: Optional[str] = None,
    ):
        self.item_id = item_id
        self.shop_id = shop_id
        self.title = title
        self.price_min = price_min
        self.price_max = price_max
        self.currency = currency
        self.original_price = original_price
        self.discount = discount
        self.description = description
        self.specifications = specifications
        self.images = images
        self.source_url = source_url
        self.final_url = final_url
        self.stock = stock
        self.rating_star = rating_star
        self.rating_count = rating_count
        self.sold_count = sold_count
        self.extracted_at = extracted_at or datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item_id": self.item_id,
            "shop_id": self.shop_id,
            "title": self.title,
            "price": {
                "currency": self.currency,
                "current_min": self.price_min,
                "current_max": self.price_max,
                "original": self.original_price,
                "discount": self.discount
            },
            "stock": self.stock,
            "rating": {
                "star": self.rating_star,
                "count": self.rating_count
            },
            "sold_count": self.sold_count,
            "description": self.description,
            "specifications": [s.to_dict() for s in self.specifications],
            "images": [img.to_dict() for img in self.images],
            "source_url": self.source_url,
            "final_url": self.final_url,
            "extracted_at": self.extracted_at
        }


class ShopeeCrawlerService:
    USER_AGENT = (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    )

    def __init__(self, target_url: str, output_image_dir: str, output_metadata_path: str):
        self.target_url = target_url
        self.output_image_dir = Path(output_image_dir)
        self.output_metadata_path = Path(output_metadata_path)
        self.captured_api_data: Optional[Dict[str, Any]] = None

    async def _handle_response(self, response: Response):
        url = response.url
        # Catch Shopee item get API or pdp API
        if any(api_key in url for api_key in ["/api/v4/item/get", "/api/v2/item/get", "api/v4/pdp/get_item_info", "/api/v4/pdp/get_pc"]):
            try:
                data = await response.json()
                if "data" in data or "item" in data:
                    logger.info(f"Captured Shopee API response from: {url}")
                    self.captured_api_data = data
            except Exception as e:
                logger.debug(f"Failed to parse json from {url}: {e}")

    async def extract_product_data(self) -> ShopeeProductDetail:
        async with async_playwright() as p:
            logger.info("Launching Playwright browser...")
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-blink-features=AutomationControlled",
                    "--disable-infobars",
                    "--window-size=1920,1080"
                ]
            )

            context: BrowserContext = await browser.new_context(
                user_agent=self.USER_AGENT,
                viewport={"width": 1920, "height": 1080},
                locale="id-ID",
                timezone_id="Asia/Jakarta",
                extra_http_headers={
                    "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
                }
            )

            page: Page = await context.new_page()
            page.on("response", self._handle_response)

            logger.info(f"Navigating to initial URL: {self.target_url}")
            try:
                await page.goto(self.target_url, wait_until="networkidle", timeout=45000)
            except Exception as e:
                logger.warning(f"Initial navigation completed with notice: {e}")

            # Let page settle and dynamic scripts finish loading
            await asyncio.sleep(5)

            final_url = page.url
            logger.info(f"Reached final URL: {final_url}")

            # Check if login popup appears and dismiss it if possible
            try:
                close_btn = await page.query_selector("button:has-text('Nanti Saja'), button:has-text('Later'), .shopee-modal__close-btn, [aria-label='close']")
                if close_btn:
                    await close_btn.click()
                    await asyncio.sleep(1)
            except Exception:
                pass

            # Scroll down slowly to trigger lazy loading of images and specifications
            for scroll_step in range(1, 6):
                await page.evaluate(f"window.scrollTo(0, {scroll_step * 500})")
                await asyncio.sleep(1)

            # Try to extract data from captured API first if available
            product_detail = await self._parse_from_api_or_dom(page, final_url)
            await browser.close()
            return product_detail

    async def _parse_from_api_or_dom(self, page: Page, final_url: str) -> ShopeeProductDetail:
        # Check API payload
        if self.captured_api_data:
            data = self.captured_api_data.get("data") or self.captured_api_data.get("item")
            if data:
                return await self._parse_from_item_dict(data, final_url, page)

        # Fallback to page DOM extraction
        logger.info("Extracting product information directly from DOM and scripts...")
        return await self._parse_from_page_dom(page, final_url)

    async def _parse_from_item_dict(self, data: Dict[str, Any], final_url: str, page: Page) -> ShopeeProductDetail:
        item_id = str(data.get("itemid") or data.get("item_id") or "")
        shop_id = str(data.get("shopid") or data.get("shop_id") or "")
        title = data.get("name") or data.get("title") or ""
        
        # Price is typically in 100,000 units in Shopee API or directly integer
        raw_price = data.get("price", 0)
        price_min = data.get("price_min", raw_price)
        price_max = data.get("price_max", raw_price)
        raw_before_discount = data.get("price_before_discount", 0)

        # Normalize price (Shopee prices in API are often multiplied by 100,000)
        if price_min > 10000000 and price_min % 100000 == 0:
            price_min = price_min / 100000.0
            price_max = price_max / 100000.0
            raw_before_discount = raw_before_discount / 100000.0

        currency = data.get("currency", "IDR")
        discount = data.get("discount")
        description = data.get("description", "")
        stock = data.get("stock")

        # Ratings
        item_rating = data.get("item_rating", {})
        rating_star = item_rating.get("rating_star")
        rating_count = None
        if item_rating.get("rating_count"):
            counts = item_rating.get("rating_count")
            rating_count = sum(counts) if isinstance(counts, list) else int(counts)
        sold_count = data.get("historical_sold") or data.get("sold")

        # Attributes / Specifications
        specs: List[ProductSpecification] = []
        attrs = data.get("attributes") or []
        for attr in attrs:
            name = attr.get("name")
            value = attr.get("value")
            if name and value:
                specs.append(ProductSpecification(name=str(name), value=str(value)))

        # Images
        image_ids = data.get("images") or []
        media_list: List[ProductMedia] = []
        for img_id in image_ids:
            if img_id:
                img_url = f"https://down-id.img.susercontent.com/file/{img_id}"
                media_list.append(ProductMedia(media_id=img_id, url=img_url))

        # If DOM has more specs or info, merge them
        dom_specs = await self._extract_specs_from_dom(page)
        if not specs and dom_specs:
            specs = dom_specs

        return ShopeeProductDetail(
            item_id=item_id,
            shop_id=shop_id,
            title=title,
            price_min=float(price_min),
            price_max=float(price_max),
            currency=currency,
            original_price=float(raw_before_discount) if raw_before_discount else None,
            discount=discount,
            description=description,
            specifications=specs,
            images=media_list,
            source_url=self.target_url,
            final_url=final_url,
            stock=stock,
            rating_star=float(rating_star) if rating_star is not None else None,
            rating_count=rating_count,
            sold_count=sold_count
        )

    async def _extract_specs_from_dom(self, page: Page) -> List[ProductSpecification]:
        specs: List[ProductSpecification] = []
        try:
            # Query standard Shopee specification rows
            spec_elements = await page.query_selector_all("div.e8duaM, div._2h2wv3, div.product-detail-spec-item, div.O0cUMZ")
            for elem in spec_elements:
                label_el = await elem.query_selector("label, span:first-child, div:first-child")
                value_el = await elem.query_selector("div, span:last-child, a")
                if label_el and value_el:
                    l_text = (await label_el.inner_text()).strip()
                    v_text = (await value_el.inner_text()).strip()
                    if l_text and v_text and l_text != v_text:
                        specs.append(ProductSpecification(name=l_text, value=v_text))
        except Exception as e:
            logger.warning(f"Error extracting specs from DOM: {e}")
        return specs

    async def _parse_from_page_dom(self, page: Page, final_url: str) -> ShopeeProductDetail:
        # Extract item_id and shop_id from URL
        # e.g., https://shopee.co.id/product/12345/67890 or https://shopee.co.id/Nama-Produk-i.12345.67890
        item_id = ""
        shop_id = ""
        match_i = re.search(r"-i\.(\d+)\.(\d+)", final_url)
        if match_i:
            shop_id = match_i.group(1)
            item_id = match_i.group(2)
        else:
            match_prod = re.search(r"/product/(\d+)/(\d+)", final_url)
            if match_prod:
                shop_id = match_prod.group(1)
                item_id = match_prod.group(2)

        # Extract title
        title = ""
        title_el = await page.query_selector("div._44qnta, h1, span.fAInvO, div.WBVL_7")
        if title_el:
            title = (await title_el.inner_text()).strip()
        if not title:
            title = await page.title()
            title = re.sub(r"\|.*Shopee.*$", "", title).strip()

        # Extract price
        price_min = 0.0
        price_max = 0.0
        price_el = await page.query_selector("div.G274f8, div.pqTWkA, div._3n5NQx, div._2v0Hgx")
        price_text = await price_el.inner_text() if price_el else ""
        if not price_text:
            body_text = await page.inner_text("body")
            m_price = re.search(r"Rp([\d\.\,]+)\s*(?:-\s*Rp([\d\.\,]+))?", body_text)
            if m_price:
                price_text = m_price.group(0)

        if price_text:
            cleaned_numbers = [float(p.replace(".", "").replace(",", ".")) for p in re.findall(r"[\d\.\,]+", price_text) if p.replace(".", "").isdigit()]
            if cleaned_numbers:
                price_min = min(cleaned_numbers)
                price_max = max(cleaned_numbers)

        # Extract original price & discount
        orig_price = None
        disc_el = await page.query_selector("div.text-xs.font-bold, div.percent")
        discount = await disc_el.inner_text() if disc_el else None

        # Extract description
        desc_el = await page.query_selector("div.f7a57a, div._2u0cEc, div.product-detail-description, div.page-product__description")
        description = (await desc_el.inner_text()).strip() if desc_el else ""

        # Extract specs
        specs = await self._extract_specs_from_dom(page)

        # Extract images from carousel or gallery
        media_list: List[ProductMedia] = []
        seen_images = set()

        # Check DOM img tags
        img_elements = await page.query_selector_all("img")
        for img in img_elements:
            src = await img.get_attribute("src") or await img.get_attribute("data-src")
            if src and any(cdn in src for cdn in ["susercontent.com/file/", "shopee.co.id/file/"]):
                # Normalize to high resolution version (strip _tn or resize params)
                base_img = re.sub(r"_tn$", "", src)
                base_img = re.sub(r"@.*$", "", base_img)
                file_id_match = re.search(r"/file/([a-zA-Z0-9_-]+)", base_img)
                if file_id_match:
                    file_id = file_id_match.group(1)
                    if file_id not in seen_images and len(file_id) > 10:
                        seen_images.add(file_id)
                        hd_url = f"https://down-id.img.susercontent.com/file/{file_id}"
                        media_list.append(ProductMedia(media_id=file_id, url=hd_url))

        return ShopeeProductDetail(
            item_id=item_id,
            shop_id=shop_id,
            title=title,
            price_min=price_min,
            price_max=price_max,
            currency="IDR",
            original_price=orig_price,
            discount=discount,
            description=description,
            specifications=specs,
            images=media_list,
            source_url=self.target_url,
            final_url=final_url
        )

    async def download_images(self, media_list: List[ProductMedia]) -> List[ProductMedia]:
        self.output_image_dir.mkdir(parents=True, exist_ok=True)
        downloaded_media: List[ProductMedia] = []

        headers = {
            "User-Agent": self.USER_AGENT,
            "Referer": "https://shopee.co.id/",
            "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8"
        }

        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True, headers=headers) as client:
            for idx, media in enumerate(media_list, start=1):
                filename = f"product_img_{idx:02d}_{media.media_id[:12]}.jpg"
                file_path = self.output_image_dir / filename

                logger.info(f"Downloading image {idx}/{len(media_list)}: {media.url}")
                try:
                    resp = await client.get(media.url)
                    if resp.status_code == 200 and len(resp.content) > 1000:
                        file_path.write_bytes(resp.content)
                        logger.info(f"Saved: {file_path} ({len(resp.content)} bytes)")
                        media.local_path = str(file_path)
                        downloaded_media.append(media)
                    else:
                        logger.warning(f"Download failed with status {resp.status_code} for {media.url}")
                except Exception as e:
                    logger.error(f"Error downloading {media.url}: {e}")

        return downloaded_media

    def save_metadata(self, product_detail: ShopeeProductDetail):
        self.output_metadata_path.parent.mkdir(parents=True, exist_ok=True)
        payload = product_detail.to_dict()
        with open(self.output_metadata_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
        logger.info(f"Metadata saved successfully to {self.output_metadata_path}")


async def main():
    target_url = sys.argv[1] if len(sys.argv) > 1 else "https://s.shopee.co.id/80DBs5lgX2"
    
    # Dual write / ensure proper directory mapping
    primary_image_dir = "product_images/sprint30"
    primary_meta_path = "docs/sprint30_campaign.json"

    # Also handle workspace/ prefix if invoked from parent root
    if not os.path.exists("product_images") and os.path.exists("workspace"):
        primary_image_dir = "workspace/product_images/sprint30"
        primary_meta_path = "workspace/docs/sprint30_campaign.json"

    crawler = ShopeeCrawlerService(
        target_url=target_url,
        output_image_dir=primary_image_dir,
        output_metadata_path=primary_meta_path
    )

    logger.info(f"Starting extraction for URL: {target_url}")
    detail = await crawler.extract_product_data()
    logger.info(f"Extracted Title: {detail.title}")
    logger.info(f"Found {len(detail.images)} images. Commencing HD downloads...")
    await crawler.download_images(detail.images)
    crawler.save_metadata(detail)

    # If running from inside workspace, also sync to workspace/product_images and docs/ for downstream compatibility
    extra_dirs = ["workspace/product_images/sprint30", "../workspace/product_images/sprint30"]
    extra_meta = ["docs/sprint30_campaign.json", "../docs/sprint30_campaign.json"]

    for d in extra_dirs:
        try:
            target_p = Path(d)
            if target_p.resolve() != Path(primary_image_dir).resolve():
                target_p.mkdir(parents=True, exist_ok=True)
                for f in Path(primary_image_dir).glob("*.jpg"):
                    (target_p / f.name).write_bytes(f.read_bytes())
        except Exception:
            pass

    for m in extra_meta:
        try:
            mp = Path(m)
            if mp.resolve() != Path(primary_meta_path).resolve():
                mp.parent.mkdir(parents=True, exist_ok=True)
                mp.write_bytes(Path(primary_meta_path).read_bytes())
        except Exception:
            pass

    print("Extraction and synchronization complete.")


if __name__ == "__main__":
    asyncio.run(main())
