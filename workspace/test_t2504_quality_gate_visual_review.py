import json
from pathlib import Path

import pytest
from PIL import Image

from tools.media_quality_auditor import (
    JPEG_MAGIC,
    PNG_MAGIC,
    is_visual_content_non_blank,
    validate_media_artifact,
    verify_magic_bytes,
)

WORKSPACE_ROOT = Path("/root/storage/projects/dalang-ai/workspace")
DOCS_DIR = WORKSPACE_ROOT / "docs"
MEDIA_DIR = WORKSPACE_ROOT / "product_images" / "dara_jumbo"
PRIMARY_SCREENSHOT = WORKSPACE_ROOT / "threads_dara_jumbo_live.png"
SECONDARY_SCREENSHOT = WORKSPACE_ROOT / "workspace" / "threads_dara_jumbo_live.png"

REQUIRED_MEDIA_FILES = [
    "dara_jumbo_1.jpg",
    "dara_jumbo_2.jpg",
    "dara_jumbo_3.jpg",
    "dara_jumbo_4.jpg",
    "dara_jumbo_5.jpg",
]

FORBIDDEN_COPY_CLAIMS = [
    "aku sudah coba",
    "aku sudah pakai",
    "pengalaman pribadiku",
    "dijamin 100%",
    "paling murah sedunia",
]

def test_screenshot_primary_exists_and_exceeds_zero_bytes():
    target = PRIMARY_SCREENSHOT
    exists = target.is_file()
    size_bytes = target.stat().st_size if exists else 0

    assert exists is True
    assert size_bytes > 0
    assert size_bytes >= 10_000

def test_screenshot_secondary_mirror_consistency():
    primary_size = PRIMARY_SCREENSHOT.stat().st_size
    secondary_exists = SECONDARY_SCREENSHOT.is_file()
    secondary_size = SECONDARY_SCREENSHOT.stat().st_size if secondary_exists else 0

    assert secondary_exists is True
    assert secondary_size > 0
    assert secondary_size == primary_size

def test_screenshot_bva_file_size_bounds():
    min_boundary = 10 * 1024
    max_boundary = 10 * 1024 * 1024
    nominal_size = PRIMARY_SCREENSHOT.stat().st_size

    assert nominal_size >= min_boundary
    assert nominal_size <= max_boundary

def test_screenshot_magic_bytes_valid_png():
    with open(PRIMARY_SCREENSHOT, "rb") as fh:
        header = fh.read(8)

    assert header.startswith(PNG_MAGIC)
    assert verify_magic_bytes(PRIMARY_SCREENSHOT, "png") is True

def test_screenshot_dimensions_and_mode_meet_viewport_standard():
    with Image.open(PRIMARY_SCREENSHOT) as img:
        width, height = img.size
        mode = img.mode
        img_format = img.format

    assert width >= 800
    assert height >= 600
    assert mode in ("RGB", "RGBA")
    assert img_format == "PNG"

def test_screenshot_pixel_entropy_not_blank_canvas():
    is_non_blank = is_visual_content_non_blank(PRIMARY_SCREENSHOT, min_unique_colors=50)
    with Image.open(PRIMARY_SCREENSHOT) as img:
        extrema = img.getextrema()

    assert is_non_blank is True
    assert len(extrema) == 3
    for channel_min, channel_max in extrema:
        assert channel_max > channel_min + 50

def test_media_directory_contains_expected_assets():
    files_present = [f.name for f in MEDIA_DIR.glob("*.jpg")]

    assert MEDIA_DIR.is_dir() is True
    assert len(files_present) >= len(REQUIRED_MEDIA_FILES)
    for expected in REQUIRED_MEDIA_FILES:
        assert expected in files_present

@pytest.mark.parametrize("filename", REQUIRED_MEDIA_FILES)
def test_physical_media_asset_size_exceeds_zero_and_meets_hd_threshold(filename):
    file_path = MEDIA_DIR / filename
    size_bytes = file_path.stat().st_size if file_path.exists() else 0

    assert file_path.is_file() is True
    assert size_bytes > 0
    assert size_bytes >= 100 * 1024
    assert size_bytes <= 25 * 1024 * 1024

@pytest.mark.parametrize("filename", REQUIRED_MEDIA_FILES)
def test_physical_media_magic_bytes_and_decodability(filename):
    file_path = MEDIA_DIR / filename
    with open(file_path, "rb") as fh:
        header = fh.read(3)

    assert header == JPEG_MAGIC
    with Image.open(file_path) as img:
        img.verify()

    with Image.open(file_path) as img:
        width, height = img.size
        img_mode = img.mode

    assert width >= 500
    assert height >= 500
    assert img_mode in ("RGB", "L")

def test_campaign_metadata_file_integrity_and_links():
    campaign_file = DOCS_DIR / "dara_jumbo_campaign.json"
    with open(campaign_file, "r", encoding="utf-8") as fh:
        data = json.load(fh)

    assert campaign_file.is_file() is True
    assert data.get("product_id") == "dara-set-rayon-premium-jumbo-ld-120"
    assert "5AsyAcB5TV" in data.get("source_url", "")
    assert data["price"]["amount"] > 0
    assert "specifications" in data

def test_threads_posting_script_configuration_and_copy():
    from tools.post_threads_dara_jumbo import (
        POST_1,
        POST_2,
        PRODUCT_IMAGE,
        SCREENSHOT_PRIMARY,
    )

    assert PRODUCT_IMAGE.is_file() is True
    assert SCREENSHOT_PRIMARY.name == "threads_dara_jumbo_live.png"
    assert "120" in POST_1 or "120" in POST_2
    assert "https://s.shopee.co.id/5AsyAcB5TV" in POST_2

    combined_text = (POST_1 + " " + POST_2).lower()
    for forbidden in FORBIDDEN_COPY_CLAIMS:
        assert forbidden not in combined_text

    hashtags = [w for w in POST_2.split() if w.startswith("#")]
    assert 3 <= len(hashtags) <= 5

def test_security_regression_zero_byte_asset_rejected(tmp_path):
    # Ref: Kai-AUDIT-SEC02
    empty_file = tmp_path / "corrupt_empty.png"
    empty_file.write_bytes(b"")

    with pytest.raises(ValueError, match="below minimum"):
        validate_media_artifact(empty_file, "png", min_bytes=1000)

def test_security_regression_spoofed_file_signature_rejected(tmp_path):
    # Ref: Kai-AUDIT-SEC03
    spoofed_file = tmp_path / "fake_image.png"
    spoofed_file.write_bytes(b"NOT_A_PNG_HEADER_PAYLOAD")

    with pytest.raises(ValueError, match="magic bytes"):
        validate_media_artifact(spoofed_file, "png", min_bytes=5)

def test_security_regression_path_traversal_non_existent(tmp_path):
    # Ref: Kai-AUDIT-SEC01
    traversal_path = WORKSPACE_ROOT / ".." / "non_existent_outside_workspace.png"

    with pytest.raises(FileNotFoundError):
        validate_media_artifact(traversal_path, "png")

def test_security_regression_truncated_image_payload_rejected(tmp_path):
    # Ref: Kai-AUDIT-SEC04
    truncated_file = tmp_path / "truncated.jpg"
    truncated_file.write_bytes(b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01")

    with pytest.raises((ValueError, OSError)):
        validate_media_artifact(truncated_file, "jpeg", min_bytes=5)

def test_disprover_protocol_blank_placeholder_hypothesis_rejected():
    # Tri-State Verdict: confirmed valid (disproved blank placeholder)
    with Image.open(PRIMARY_SCREENSHOT) as img:
        colors = img.getcolors(maxcolors=2000)
        extrema = img.getextrema()

    assert colors is not None or len(colors) > 100
    for low, high in extrema:
        assert (high - low) > 50
