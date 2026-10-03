"""
Shopee product data contract and DDD-aligned schema for campaign metadata.

Domain: E-commerce Product Catalog
Bounded Context: Campaign Asset Management

Separates storage model (ProductCampaignInDB) from public projection (ProductCampaignPublic)
to prevent accidental exposure of internal crawl metadata.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


# Value Objects

@dataclass(frozen=True)
class IDRPrice:
    """Immutable value object representing a price in Indonesian Rupiah."""
    amount: int

    def __post_init__(self) -> None:
        if self.amount < 0:
            raise ValueError("Price amount cannot be negative.")

    @property
    def formatted(self) -> str:
        return f"Rp{self.amount:,.0f}".replace(",", ".")

    def to_dict(self) -> dict:
        return {
            "currency": "IDR",
            "amount": self.amount,
            "formatted": self.formatted,
        }


@dataclass(frozen=True)
class ProductImageAsset:
    """Immutable value object representing a downloaded product image."""
    file_name: str
    local_path: str
    source_url: str
    size_kb: int
    width_px: int
    height_px: int

    def __post_init__(self) -> None:
        if not self.file_name:
            raise ValueError("Image file_name must not be empty.")
        if not self.source_url.startswith("https://"):
            raise ValueError("Image source_url must use HTTPS.")
        if self.size_kb <= 0:
            raise ValueError("Image size_kb must be positive.")

    @property
    def is_hd(self) -> bool:
        # HD threshold: at least 720px on the shorter side
        return min(self.width_px, self.height_px) >= 720

    def to_dict(self) -> dict:
        return {
            "file_name": self.file_name,
            "path": self.local_path,
            "source_url": self.source_url,
            "size_kb": self.size_kb,
            "resolution": f"{self.width_px}x{self.height_px}",
            "is_hd": self.is_hd,
        }


# Entity

@dataclass
class ProductCampaignInDB:
    """
    Storage-layer entity for a crawled Shopee product campaign.

    Retains full crawl metadata including final redirect URL and internal
    tracking parameters — not for direct API exposure.
    """
    product_id: str
    product_name: str
    source_url: str
    final_url: str
    price: IDRPrice
    category: str
    images: list[ProductImageAsset]
    crawled_at: datetime
    status: str = "active"
    specifications: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.product_id:
            raise ValueError("product_id must not be empty.")
        if not re.match(r"^https?://", self.source_url):
            raise ValueError("source_url must be a valid HTTP/HTTPS URL.")
        if self.crawled_at.tzinfo is None:
            raise ValueError("crawled_at must be timezone-aware (UTC).")
        if len(self.images) < 2:
            raise ValueError("A campaign must have at least 2 product images.")
        if self.status not in ("active", "archived", "draft"):
            raise ValueError(f"Invalid status: {self.status}")

    @property
    def hd_images(self) -> list[ProductImageAsset]:
        return [img for img in self.images if img.is_hd]

    @classmethod
    def from_json(cls, data: dict) -> "ProductCampaignInDB":
        """Deserialize from the campaign JSON metadata file."""
        price = IDRPrice(amount=data["price"]["amount"])

        images = []
        for img_data in data.get("images", []):
            resolution = img_data.get("resolution", "0x0")
            if "x" in resolution:
                w, h = map(int, resolution.split("x"))
            else:
                # Legacy format: resolution stored as label string like "HD"
                w, h = 1024, 1024

            images.append(ProductImageAsset(
                file_name=img_data["file_name"],
                local_path=img_data["path"],
                source_url=img_data["source_url"],
                size_kb=img_data.get("size_kb", 0),
                width_px=w,
                height_px=h,
            ))

        crawled_at_str = data["crawled_at"]
        crawled_at = datetime.fromisoformat(crawled_at_str.replace("Z", "+00:00"))

        return cls(
            product_id=data["product_id"],
            product_name=data["product_name"],
            source_url=data["source_url"],
            final_url=data.get("final_url", data["source_url"]),
            price=price,
            category=data.get("category", ""),
            images=images,
            crawled_at=crawled_at,
            status=data.get("status", "active"),
            specifications=data.get("specifications", {}),
        )


# Public Projection — safe for API/frontend exposure

@dataclass(frozen=True)
class ProductCampaignPublic:
    """
    Read-only projection of ProductCampaignInDB for external consumers.

    Strips internal crawl metadata (final_url with tracking params, raw specs)
    and exposes only campaign-relevant fields.
    """
    product_id: str
    product_name: str
    source_url: str
    price: IDRPrice
    category: str
    hd_image_count: int
    image_paths: list[str]
    crawled_at_iso: str
    status: str

    @classmethod
    def from_entity(cls, entity: ProductCampaignInDB) -> "ProductCampaignPublic":
        return cls(
            product_id=entity.product_id,
            product_name=entity.product_name,
            source_url=entity.source_url,
            price=entity.price,
            category=entity.category,
            hd_image_count=len(entity.hd_images),
            image_paths=[img.local_path for img in entity.images],
            crawled_at_iso=entity.crawled_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
            status=entity.status,
        )

    def to_dict(self) -> dict:
        return {
            "product_id": self.product_id,
            "product_name": self.product_name,
            "source_url": self.source_url,
            "price": self.price.to_dict(),
            "category": self.category,
            "hd_image_count": self.hd_image_count,
            "image_paths": self.image_paths,
            "crawled_at": self.crawled_at_iso,
            "status": self.status,
        }
