"""Generate banner Instagram affiliate — dark mode, no emoji dependency."""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path


def make_banner(
    product: str,
    features: list[str],
    cta: str = "Cek link di bio",
    out_path: str = "/tmp/ig_banner.jpg",
    bg_color: tuple = (10, 10, 10),
    accent_color: tuple = (245, 197, 24),   # kuning Shopee
    text_color: tuple = (255, 255, 255),
) -> str:
    W, H = 1080, 1080
    img = Image.new("RGB", (W, H), color=bg_color)
    draw = ImageDraw.Draw(img)

    # Subtle gradient overlay
    for y in range(H):
        v = int(18 * (1 - y / H))
        draw.line([(0, y), (W, y)], fill=(v, v, v + 5))

    # Garis aksen atas & bawah
    draw.rectangle([(0, 0), (W, 10)], fill=accent_color)
    draw.rectangle([(0, H - 10), (W, H)], fill=accent_color)

    # Kotak dekoratif kanan atas
    draw.rectangle([(W - 160, 0), (W, 160)], fill=(30, 30, 30))
    draw.rectangle([(W - 155, 5), (W - 5, 155)], outline=accent_color, width=2)

    # Load font
    try:
        font_label = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 30)
        font_big   = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 58)
        font_med   = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 36)
        font_sml   = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 28)
        font_cta   = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 42)
    except Exception:
        font_label = font_big = font_med = font_sml = font_cta = ImageFont.load_default()

    # Label REKOMENDASI
    draw.text((60, 55), "[ REKOMENDASI ]", font=font_label, fill=accent_color)

    # Nama produk — wrap per kata
    words = product.replace("\n", " ").split()
    lines, cur = [], []
    for w in words:
        test = " ".join(cur + [w])
        bbox = draw.textbbox((0, 0), test, font=font_big)
        if bbox[2] - bbox[0] < W - 120:
            cur.append(w)
        else:
            if cur:
                lines.append(" ".join(cur))
            cur = [w]
    if cur:
        lines.append(" ".join(cur))

    y = 130
    for line in lines:
        draw.text((60, y), line, font=font_big, fill=text_color)
        y += 72

    # Garis pemisah
    y += 20
    draw.rectangle([(60, y), (W - 60, y + 4)], fill=accent_color)
    y += 30

    # Fitur-fitur
    for feat in features:
        draw.text((60, y), "  ->  " + feat, font=font_med, fill=text_color)
        y += 58

    # CTA box di bagian bawah
    y_cta = H - 210
    draw.rectangle([(0, y_cta), (W, y_cta + 4)], fill=accent_color)
    draw.text((60, y_cta + 20), cta, font=font_cta, fill=accent_color)
    draw.text((60, y_cta + 80), "Shopee Affiliate  |  Link ada di bio", font=font_sml, fill=(180, 180, 180))
    draw.text((60, y_cta + 120), "s.shopee.co.id", font=font_sml, fill=(100, 100, 100))

    # Simpan
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path, "JPEG", quality=93)
    return out_path


if __name__ == "__main__":
    out = make_banner(
        product="Tumbler 1 Liter Tahan Panas & Dingin",
        features=[
            "Dingin 24 jam / Panas 12 jam",
            "Kapasitas 1 Liter -- anti bolak-balik",
            "BPA Free & Anti Bocor",
            "Grip Silitech yang nyaman",
        ],
        cta=">> Cek link di bio",
        out_path="/tmp/ig_debug/banner_v2.jpg",
    )
    print(f"Banner: {out}")
