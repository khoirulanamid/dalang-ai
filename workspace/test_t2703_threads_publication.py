"""
Unit tests for Task T-2703: Publikasikan status Threads
Verify automation tool, product assets, live screenshots, and content standards compliance for Sprint 27.
"""
from pathlib import Path
from PIL import Image
import sys

# Import post variables from tool
sys.path.insert(0, ".")
from tools.post_threads_sprint27 import POST_1, POST_2

def test_product_image_hd_exists():
    img_path = Path("product_images/sprint27/sprint27_product_1.jpg")
    if not img_path.exists():
        img_path = Path("/root/storage/projects/dalang-ai/workspace/product_images/sprint27/sprint27_product_1.jpg")
    assert img_path.exists(), "Product HD image must exist"
    assert img_path.stat().st_size > 10 * 1024, "Image must have valid size (>10KB)"
    with Image.open(img_path) as im:
        assert im.width >= 500 and im.height >= 500, "Image dimensions must be at least 500x500"

def test_live_screenshot_exists_and_valid():
    paths = [
        Path("threads_sprint27_live.png"),
        Path("workspace/threads_sprint27_live.png"),
        Path("/root/storage/projects/dalang-ai/workspace/threads_sprint27_live.png"),
        Path("/root/storage/projects/dalang-ai/threads_sprint27_live.png"),
    ]
    found = False
    for p in paths:
        if p.exists():
            found = True
            assert p.stat().st_size > 10 * 1024, f"Screenshot {p} must be > 10KB"
            with Image.open(p) as im:
                assert im.width > 0 and im.height > 0
    assert found, "Live screenshot must exist in workspace/threads_sprint27_live.png or root"

def test_threads_content_standards_compliance():
    combined_copy = f"{POST_1}\n{POST_2}".lower()
    
    # Anti-fabrication compliance (Mandatory rule: no first-person personal claims)
    forbidden_claims = [
        "aku sudah pakai", "aku udah pake", "aku pakai", "saya pakai",
        "pengalaman pribadi saya", "beneran tahan di tangan aku"
    ]
    for claim in forbidden_claims:
        assert claim not in combined_copy, f"Forbidden claim found in copy: {claim}"

    # Must contain key spec elements and link
    assert "dual" in combined_copy or "lige" in combined_copy, "Must mention product specifications"
    assert "https://s.shopee.co.id/" in POST_2, "Must include Shopee affiliate link"
    
    # Hashtags count check (3-5 hashtags)
    hashtags = [word for word in POST_2.split() if word.startswith("#")]
    assert 3 <= len(hashtags) <= 5, f"Hashtag count must be between 3 and 5, got {len(hashtags)}"
