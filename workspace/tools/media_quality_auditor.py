from pathlib import Path

from PIL import Image

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
JPEG_MAGIC = b"\xff\xd8\xff"

def verify_magic_bytes(file_path: Path, expected_type: str) -> bool:
    if not file_path.is_file():
        return False
    with open(file_path, "rb") as fh:
        header = fh.read(8)
    if expected_type.lower() == "png":
        return header.startswith(PNG_MAGIC)
    if expected_type.lower() in ("jpeg", "jpg"):
        return header.startswith(JPEG_MAGIC)
    return False

def is_visual_content_non_blank(file_path: Path, min_unique_colors: int = 50) -> bool:
    with Image.open(file_path) as img:
        rgb_img = img.convert("RGB")
        extrema = rgb_img.getextrema()
        for low, high in extrema:
            if low == high:
                return False
        colors = rgb_img.getcolors(maxcolors=min_unique_colors + 10)
        if colors is None:
            return True
        return len(colors) >= min_unique_colors

def validate_media_artifact(
    file_path: Path,
    expected_format: str,
    min_bytes: int = 1,
    max_bytes: int = 50 * 1024 * 1024,
    min_width: int = 100,
    min_height: int = 100,
) -> dict:
    resolved = file_path.resolve()
    if not resolved.exists():
        raise FileNotFoundError(f"Media file does not exist: {file_path}")
    if not resolved.is_file():
        raise ValueError(f"Path is not a regular file: {file_path}")

    file_size = resolved.stat().st_size
    if file_size < min_bytes:
        raise ValueError(f"File size {file_size} bytes below minimum {min_bytes} bytes")
    if file_size > max_bytes:
        raise ValueError(f"File size {file_size} bytes exceeds maximum {max_bytes} bytes")

    if not verify_magic_bytes(resolved, expected_format):
        raise ValueError(f"File magic bytes do not match expected format {expected_format}")

    with Image.open(resolved) as img:
        img.verify()

    with Image.open(resolved) as img:
        width, height = img.size
        actual_format = img.format
        if width < min_width or height < min_height:
            raise ValueError(
                f"Image dimensions ({width}x{height}) below required ({min_width}x{min_height})"
            )

    is_valid_pixels = is_visual_content_non_blank(resolved)
    if not is_valid_pixels:
        raise ValueError("Image appears visually blank or has uniform color value")

    return {
        "path": str(resolved),
        "size_bytes": file_size,
        "format": actual_format,
        "dimensions": (width, height),
        "non_blank": is_valid_pixels,
    }
