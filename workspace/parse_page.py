import re

with open("rendered_page.html", "r", encoding="utf-8") as f:
    content = f.read()

print("File size:", len(content))

keywords = ["Dara", "Blouse", "Kulot", "Rayon", "124", "124500", "124.500", "image", "jpg", "jpeg", "png", "cf.shopee.co.id", "down-id.img.susercontent.com"]
for kw in keywords:
    count = len(re.findall(re.escape(kw), content, re.IGNORECASE))
    print(f"{kw}: {count}")

# Print any image URLs found
img_urls = set(re.findall(r'https?://[^\s"\'<>]+\.(?:jpg|jpeg|png|webp)', content, re.IGNORECASE))
print(f"Total image URLs found: {len(img_urls)}")
for u in list(img_urls)[:15]:
    print("  Img:", u)

# Check for product title or json ld
for match in re.finditer(r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', content, re.DOTALL):
    print("LD+JSON:", match.group(1)[:500])
