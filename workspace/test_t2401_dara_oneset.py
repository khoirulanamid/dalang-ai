"""
Test suite verifying T-2401 artifacts and data contracts.

Validates:
1. ProductCampaignInDB entity and ProductCampaignPublic projection (DDD invariants).
2. docs/dara_oneset_campaign.json compliance with ISO 8601 UTC and price specs.
3. Image artifacts in workspace/product_images/dara_oneset/ (>= 2 HD images).
"""

import json
import os
from pathlib import Path
from PIL import Image
import pytest

from tools.shopee_product_schema import (
    IDRPrice,
    ProductImageAsset,
    ProductCampaignInDB,
    ProductCampaignPublic,
)

METADATA_PATH = Path("docs/dara_oneset_campaign.json")
IMAGE_DIR = Path("workspace/product_images/dara_oneset")
FALLBACK_IMAGE_DIR = Path("product_images/dara_oneset")


def test_idr_price_formatting_and_invariant():
    price = IDRPrice(124500)
    assert price.formatted == "Rp124.500"
    assert price.to_dict()["amount"] == 124500
    assert price.to_dict()["currency"] == "IDR"

    with pytest.raises(ValueError, match="negative"):
        IDRPrice(-1)


def test_campaign_entity_and_projection():
    with open(METADATA_PATH, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    entity = ProductCampaignInDB.from_json(raw_data)
    assert entity.product_name == "Dara One Set Blouse Kulot Rayon"
    assert entity.price.amount == 124500
    assert len(entity.images) >= 2
    assert entity.crawled_at.tzinfo is not None

    # Verify public projection hides tracking params
    public = ProductCampaignPublic.from_entity(entity)
    public_dict = public.to_dict()

    assert "final_url" not in public_dict
    assert "specifications" not in public_dict
    assert public_dict["product_id"] == "dara-one-set-blouse-kulot-rayon"
    assert public_dict["price"]["formatted"] == "Rp124.500"
    assert public_dict["hd_image_count"] >= 2


def test_metadata_file_content():
    assert METADATA_PATH.exists(), f"Metadata file {METADATA_PATH} must exist"

    with open(METADATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["product_name"] == "Dara One Set Blouse Kulot Rayon"
    assert data["price"]["amount"] == 124500
    assert data["price"]["currency"] == "IDR"
    assert "https://s.shopee.co.id/3qNaOVRWrP" in data["source_url"]

    # Verify ISO 8601 UTC timestamp format: YYYY-MM-DDTHH:MM:SSZ
    import re
    assert re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$", data["crawled_at"])


def test_downloaded_images_exist_and_are_hd():
    target_dir = IMAGE_DIR if IMAGE_DIR.exists() else FALLBACK_IMAGE_DIR
    assert target_dir.exists(), f"Image directory {target_dir} must exist"

    images = list(target_dir.glob("*.jpg")) + list(target_dir.glob("*.png"))
    # Exclude crawled preview screenshot from product image count if needed
    product_images = [img for img in images if not img.name.startswith("crawled_")]

    assert len(product_images) >= 2, f"Expected at least 2 product images, found {len(product_images)}"

    hd_count = 0
    for img_path in product_images:
        assert img_path.stat().st_size > 10_000, f"Image {img_path.name} is too small (<10KB)"
        with Image.open(img_path) as im:
            w, h = im.size
            if min(w, h) >= 720:
                hd_count += 1

    assert hd_count >= 2, f"Expected at least 2 HD images (min dimension >= 720px), got {hd_count}"
