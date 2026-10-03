import os
import sys
import json

print("Checking environment and existing files...")
for p in ["post_jeans_facebook.py", "docs/celana_jeans_campaign.json", "docs/naskah_celana_jeans_korea_canonical.md"]:
    if os.path.exists(p):
        print(f"Found {p} (size: {os.path.getsize(p)})")
    else:
        print(f"NOT found {p}")
