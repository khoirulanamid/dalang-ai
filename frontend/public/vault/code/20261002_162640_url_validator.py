"""Affiliate link validation — enforce protocol and domain allowlist.

Prevents open-redirect injection and non-affiliate URL smuggling.
Only HTTPS links from the approved Shopee affiliate short-link domain are accepted.
"""
from __future__ import annotations

from urllib.parse import urlparse


# Allowlist of approved affiliate link domains.
# Extend this list only after explicit approval — do not use a denylist approach
# (OWASP ASVS V5.1.3: input validation MUST use allowlist, not blocklist).
ALLOWED_AFFILIATE_DOMAINS: frozenset[str] = frozenset({
    "s.shopee.co.id",
})

_MAX_URL_LENGTH = 512


def validate_affiliate_link(url: str) -> tuple[bool, str]:
    """Validate an affiliate link against protocol and domain allowlist.

    Args:
        url: The affiliate URL to validate.

    Returns:
        (ok: bool, reason: str) — reason is empty string when ok is True.
    """
    if not isinstance(url, str):
        return False, "Affiliate link must be a string"

    url = url.strip()

    if not url:
        return False, "Affiliate link is empty"

    if len(url) > _MAX_URL_LENGTH:
        return False, f"Affiliate link exceeds maximum length ({_MAX_URL_LENGTH} chars)"

    try:
        parsed = urlparse(url)
    except Exception:
        return False, "Affiliate link could not be parsed as a URL"

    if parsed.scheme != "https":
        return False, (
            f"Affiliate link must use HTTPS. Got scheme: '{parsed.scheme}'. "
            "Plain HTTP and non-HTTP schemes are not permitted."
        )

    # netloc includes port if present; strip it for domain comparison
    host = parsed.netloc.split(":")[0].lower()

    if host not in ALLOWED_AFFILIATE_DOMAINS:
        return False, (
            f"Affiliate link domain '{host}' is not in the approved allowlist "
            f"{sorted(ALLOWED_AFFILIATE_DOMAINS)}. "
            "Only official Shopee affiliate short-links are accepted."
        )

    if not parsed.path or parsed.path == "/":
        return False, "Affiliate link is missing the short-link path segment"

    return True, ""
