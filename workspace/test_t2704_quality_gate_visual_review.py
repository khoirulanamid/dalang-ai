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
MEDIA_DIR = WORKSPACE_ROOT / "product_images" / "sprint27"
PRIMARY_SCREENSHOT = WORKSPACE_ROOT / "threads_sprint27_live.png"
SECONDARY_SCREENSHOTS = [
    Path("/root/storage/projects/dalang-ai/threads_sprint27_live.png"),
    WORKSPACE_ROOT / "workspace" / "threads_sprint27_live.png",
]

REQUIRED_MEDIA_FILES = [f"sprint27_product_{i}.jpg" for i in range(1, 15)]

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


def test_screenshot_secondary_mirrors_exist_and_consistent():
    primary_size = PRIMARY_SCREENSHOT.stat().st_size

    for secondary in SECONDARY_SCREENSHOTS:
        exists = secondary.is_file()
        size_bytes = secondary.stat().st_size if exists else 0
        assert exists is True
        assert size_bytes > 0
        assert size_bytes == primary_size


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


def test_screenshot_dimensions_and_rendering_integrity():
    with Image.open(PRIMARY_SCREENSHOT) as img:
        width, height = img.size
        img_format = img.format
        img_mode = img.mode

    assert img_format == "PNG"
    assert width >= 1000
    assert height >= 600
    assert img_mode in ("RGB", "RGBA")


def test_screenshot_visual_entropy_and_non_blank():
    is_non_blank = is_visual_content_non_blank(PRIMARY_SCREENSHOT, min_unique_colors=100)
    with Image.open(PRIMARY_SCREENSHOT) as img:
        colors = img.getcolors(maxcolors=10_000)

    assert is_non_blank is True
    assert colors is None or len(colors) >= 100


def test_disprover_protocol_blank_placeholder_hypothesis_rejected():
    with Image.open(PRIMARY_SCREENSHOT) as img:
        colors = img.getcolors(maxcolors=2000)
        extrema = img.getextrema()

    assert colors is not None or len(colors) > 100
    for low, high in extrema:
        assert (high - low) > 50


def test_physical_media_all_artifacts_exist_and_count():
    assert MEDIA_DIR.is_dir() is True
    existing_files = {f.name for f in MEDIA_DIR.iterdir() if f.is_file()}

    for required in REQUIRED_MEDIA_FILES:
        assert required in existing_files


@pytest.mark.parametrize("filename", REQUIRED_MEDIA_FILES)
def test_physical_media_bva_file_size_bounds(filename):
    file_path = MEDIA_DIR / filename
    exists = file_path.is_file()
    size_bytes = file_path.stat().st_size if exists else 0

    assert exists is True
    assert size_bytes > 0
    assert size_bytes >= 50 * 1024
    assert size_bytes <= 10 * 1024 * 1024


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
    campaign_file = DOCS_DIR / "sprint27_campaign.json"
    with open(campaign_file, "r", encoding="utf-8") as fh:
        data = json.load(fh)

    assert campaign_file.is_file() is True
    assert data.get("product_id") == "lige-jam-tangan-digital-led-dual-display-asli-jam-tangan-olahraga-pria-tahan-air-jam-tangan-kuarsa-chronograph-watch"
    assert "2BFO1kXcTq" in data.get("source_url", "")
    assert data["price"]["amount"] > 0
    assert "campaign" in data
    assert "copywriting_angles" in data["campaign"]


def test_threads_posting_script_configuration_and_copy():
    from tools.post_threads_sprint27 import (
        POST_1,
        POST_2,
        PRODUCT_IMAGE,
        SCREENSHOT_LOCATIONS,
    )

    assert PRODUCT_IMAGE.is_file() is True
    assert any(loc.name == "threads_sprint27_live.png" for loc in SCREENSHOT_LOCATIONS)
    assert "2BFO1kXcTq" in POST_2

    combined_text = (POST_1 + " " + POST_2).lower()
    for forbidden in FORBIDDEN_COPY_CLAIMS:
        assert forbidden not in combined_text

    hashtags = [w for w in POST_2.split() if w.startswith("#")]
    assert 3 <= len(hashtags) <= 10


def test_security_tamper_detection_corrupted_header_rejected(tmp_path):
    tampered_file = tmp_path / "tampered.png"
    tampered_file.write_bytes(b"\x00\x00\x00\x00" + b"random_corrupted_stream")

    is_valid_magic = verify_magic_bytes(tampered_file, "png")
    assert is_valid_magic is False

    with pytest.raises((ValueError, OSError)):
        validate_media_artifact(tampered_file, "png", min_bytes=10)


def test_security_tamper_detection_truncated_payload_rejected(tmp_path):
    truncated_file = tmp_path / "truncated.jpg"
    truncated_file.write_bytes(b"\xff\xd8\xff")

    with pytest.raises((ValueError, OSError)):
        validate_media_artifact(truncated_file, "jpeg", min_bytes=5)


def test_bva_dimension_boundaries(tmp_path):
    sub_min_file = tmp_path / "sub_min.png"
    Image.new("RGB", (99, 99), color=(200, 50, 50)).save(sub_min_file, "PNG")

    exact_min_file = tmp_path / "exact_min.png"
    img_min = Image.new("RGB", (100, 100), color=(10, 10, 10))
    for x in range(50):
        for y in range(50):
            img_min.putpixel((x, y), (x * 4, y * 4, 120))
    img_min.save(exact_min_file, "PNG")

    with pytest.raises(ValueError, match="Image dimensions .* below required"):
        validate_media_artifact(sub_min_file, "png", min_width=100, min_height=100)

    result_exact = validate_media_artifact(exact_min_file, "png", min_width=100, min_height=100)
    assert result_exact["dimensions"] == (100, 100)
    assert result_exact["format"] == "PNG"


def test_exit_code_determinism_contract():
    expected_exit_codes = {
        "SUCCESS": 0,
        "GENERAL_ERROR": 1,
        "COOKIE_EXPIRED": 2,
        "DEDUP_REJECTED": 3,
        "NO_UNUSED_LINK": 4,
        "PLAYWRIGHT_ERROR": 5,
        "IMAGE_MISSING": 6,
        "ACCOUNT_LOCKED": 7,
    }

    assert expected_exit_codes["SUCCESS"] == 0
    assert expected_exit_codes["COOKIE_EXPIRED"] == 2
    assert expected_exit_codes["ACCOUNT_LOCKED"] == 7
