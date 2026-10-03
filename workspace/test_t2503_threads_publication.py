"""
Unit tests for Task T-2503: Publikasikan status Threads
Verify automation tool, product assets, live screenshots, and content standards compliance.
"""
from pathlib import Path
from PIL import Image
import sys

# Import the actual post variables from the tool
sys.path.insert(0, ".")
from tools.post_threads_dara_jumbo import POST_1, POST_2

def test_product_image_hd_exists():
    img_path = Path("product_images/dara_jumbo/dara_jumbo_1.jpg")
    assert img_path.exists(), "Product HD image must exist"
    assert img_path.stat().st_size > 100 * 1024, "Image must be HD (>100KB)"
    with Image.open(img_path) as im:
        assert im.width >= 500 and im.height >= 500, "Image dimensions must be at least 500x500"

def test_live_screenshot_exists_and_valid():
    paths = [
        Path("threads_dara_jumbo_live.png"),
        Path("workspace/threads_dara_jumbo_live.png")
    ]
    found = False
    for p in paths:
        if p.exists():
            found = True
            assert p.stat().st_size > 10 * 1024, f"Screenshot {p} must be > 10KB"
            with Image.open(p) as im:
                assert im.width > 0 and im.height > 0
    assert found, "Live screenshot must exist in at least one expected workspace path"

def test_threads_posting_script_compliance():
    combined_copy = f"{POST_1}\n{POST_2}".lower()
    
    # Standard compliance checks
    forbidden_claims = ["aku sudah pakai", "saya sudah pakai", "aku udah pake", "beneran tahan seharian di bibir aku"]
    for claim in forbidden_claims:
        assert claim not in combined_copy, f"Forbidden claim found in copy: {claim}"

    # Must contain key spec elements and link
    assert "120" in combined_copy, "Must mention LD 120"
    assert "https://s.shopee.co.id/" in POST_2, "Must include Shopee affiliate link"
    
    # Hashtags count check (3-5 hashtags)
    hashtags = [word for word in POST_2.split() if word.startswith("#")]
    assert 3 <= len(hashtags) <= 5, f"Hashtag count must be between 3 and 5, got {len(hashtags)}"
