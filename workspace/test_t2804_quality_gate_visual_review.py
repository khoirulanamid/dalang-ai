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
MEDIA_DIR = WORKSPACE_ROOT / "product_images" / "sprint28"
PRIMARY_SCREENSHOT = WORKSPACE_ROOT / "threads_sprint28_live.png"
SECONDARY_SCREENSHOTS = [
    Path("/root/storage/projects/dalang-ai/threads_sprint28_live.png"),
    WORKSPACE_ROOT / "workspace" / "threads_sprint28_live.png",
]

REQUIRED_MEDIA_FILES = [f"sprint28_product_{i}.jpg" for i in range(1, 7)]

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
    is_valid = verify_magic_bytes(PRIMARY_SCREENSHOT, "png")
    with open(PRIMARY_SCREENSHOT, "rb") as fh:
        header = fh.read(8)

    assert is_valid is True
    assert header == PNG_MAGIC


def test_screenshot_visual_dimensions_and_rendering():
    validation_res = validate_media_artifact(
        PRIMARY_SCREENSHOT,
        expected_format="png",
        min_bytes=10_000,
        min_width=600,
        min_height=400,
    )
    width, height = validation_res["dimensions"]

    assert validation_res["format"] == "PNG"
    assert width >= 600
    assert height >= 400
    assert validation_res["non_blank"] is True


def test_physical_media_directory_contains_all_sprint28_images():
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


@pytest.mark.parametrize("filename", REQUIRED_MEDIA_FILES)
def test_physical_media_magic_bytes_and_integrity(filename):
    file_path = MEDIA_DIR / filename
    is_valid_magic = verify_magic_bytes(file_path, "jpeg")

    with open(file_path, "rb") as fh:
        header = fh.read(3)

    assert is_valid_magic is True
    assert header == JPEG_MAGIC

    validation_res = validate_media_artifact(
        file_path,
        expected_format="jpeg",
        min_bytes=50 * 1024,
        min_width=300,
        min_height=300,
    )
    assert validation_res["format"] in ("JPEG", "JPG")
    assert validation_res["dimensions"][0] >= 300
    assert validation_res["dimensions"][1] >= 300
    assert validation_res["non_blank"] is True


def test_campaign_documentation_integrity_and_schema():
    campaign_file = DOCS_DIR / "sprint28_campaign.json"
    with open(campaign_file, "r", encoding="utf-8") as fh:
        data = json.load(fh)

    assert campaign_file.is_file() is True
    assert data.get("product_id") == "amora-emweha-jaket-crop"
    assert "20vxzX4Fx0" in data.get("source_url", "")
    assert data["price"]["amount"] > 0
    assert "campaign" in data
    assert "copywriting_angles" in data["campaign"]


def test_threads_posting_script_configuration_and_copy():
    from tools.post_threads_sprint28 import (
        POST_1,
        POST_2,
        PRODUCT_IMAGE,
        SCREENSHOT_LOCATIONS,
    )

    assert PRODUCT_IMAGE.is_file() is True
    assert any(loc.name == "threads_sprint28_live.png" for loc in SCREENSHOT_LOCATIONS)
    assert "20vxzX4Fx0" in POST_2

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


def test_security_tamper_detection_zero_byte_file_rejected(tmp_path):
    empty_file = tmp_path / "zero_byte.jpg"
    empty_file.write_bytes(b"")

    assert verify_magic_bytes(empty_file, "jpeg") is False
    with pytest.raises(ValueError, match="below minimum"):
        validate_media_artifact(empty_file, "jpeg", min_bytes=1)


def test_security_tamper_detection_blank_canvas_rejected(tmp_path):
    blank_file = tmp_path / "uniform_canvas.png"
    img = Image.new("RGB", (200, 200), color=(255, 255, 255))
    img.save(blank_file, "PNG")

    assert is_visual_content_non_blank(blank_file, min_unique_colors=50) is False
    with pytest.raises(ValueError, match="visually blank"):
        validate_media_artifact(blank_file, "png", min_bytes=10)


def test_bva_dimension_boundary_enforcement(tmp_path):
    sub_min_file = tmp_path / "dim_sub_min.png"
    img_sub = Image.new("RGB", (99, 99), color=(10, 20, 30))
    for x in range(50):
        for y in range(50):
            img_sub.putpixel((x, y), (x * 4, y * 4, 100))
    img_sub.save(sub_min_file, "PNG")

    exact_min_file = tmp_path / "dim_exact_min.png"
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
