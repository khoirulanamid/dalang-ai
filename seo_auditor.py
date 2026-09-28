"""
Technical SEO & Core Web Vitals Auditor — Dalang-AI
Terinspirasi dari avansaber/seo-monster (MCP SEO Server)

Digunakan oleh Lulu (Frontend Architect) dan Mika (Technical Writer) untuk:
1. Audit Technical SEO (meta tags, OpenGraph, Twitter Card, canonical link, robots, sitemap)
2. Validasi Structured Data (JSON-LD Schema.org)
3. Audit Core Web Vitals & Asset Performance (resource size, preload hints, layout shift indicators)
"""

import json
import re
from typing import Any, Dict, List, Optional


class TechnicalSEOAuditor:
    """
    Auditor Technical SEO dan Web Vitals untuk memastikan aplikasi dan dokumentasi web
    memiliki skor keterindeksan tinggi di mesin pencari (Google/Bing) dan AI Answer Engines (Perplexity/ChatGPT).
    """

    @staticmethod
    def audit_html_metadata(html_content: str, target_url: str = "") -> Dict[str, Any]:
        """
        Memeriksa kelengkapan elemen meta-tag SEO standar dan media sosial.
        """
        issues = []
        passed = []

        # 1. Title Tag
        title_match = re.search(r"<title[^>]*>(.*?)</title>", html_content, re.IGNORECASE | re.DOTALL)
        if title_match and title_match.group(1).strip():
            title_text = title_match.group(1).strip()
            if len(title_text) < 10 or len(title_text) > 70:
                issues.append(f"WARNING: Title '{title_text}' panjangnya ({len(title_text)} karakter) di luar rekomendasi ideal (10-70 karakter).")
            else:
                passed.append(f"Title tag optimal: '{title_text}' ({len(title_text)} chars)")
        else:
            issues.append("CRITICAL: Tag <title> tidak ditemukan atau kosong.")

        # 2. Meta Description
        desc_match = re.search(r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']', html_content, re.IGNORECASE)
        if desc_match and desc_match.group(1).strip():
            desc_text = desc_match.group(1).strip()
            if len(desc_text) < 50 or len(desc_text) > 160:
                issues.append(f"WARNING: Meta description ({len(desc_text)} karakter) di luar rekomendasi (50-160 karakter).")
            else:
                passed.append("Meta description hadir dan berada dalam rentang ideal.")
        else:
            issues.append("HIGH: Meta description tag tidak ditemukan.")

        # 3. Canonical Tag
        canonical_match = re.search(r'<link\s+rel=["\']canonical["\']\s+href=["\'](.*?)["\']', html_content, re.IGNORECASE)
        if canonical_match and canonical_match.group(1).strip():
            passed.append(f"Canonical tag terdefinisi: {canonical_match.group(1).strip()}")
        else:
            issues.append("MEDIUM: Link rel='canonical' tidak ditemukan (potensi duplikasi konten).")

        # 4. Viewport Tag (Mobile Responsiveness / Google Mobile-Friendly)
        if re.search(r'<meta\s+name=["\']viewport["\']', html_content, re.IGNORECASE):
            passed.append("Meta viewport hadir untuk Google Mobile-Friendly compliance.")
        else:
            issues.append("CRITICAL: Meta viewport tidak ditemukan; situs gagal mobile-friendliness audit.")

        # 5. OpenGraph & Social Sharing
        has_og_title = bool(re.search(r'<meta\s+property=["\']og:title["\']', html_content, re.IGNORECASE))
        has_og_desc = bool(re.search(r'<meta\s+property=["\']og:description["\']', html_content, re.IGNORECASE))
        has_og_image = bool(re.search(r'<meta\s+property=["\']og:image["\']', html_content, re.IGNORECASE))

        if has_og_title and has_og_desc and has_og_image:
            passed.append("OpenGraph tags (og:title, og:description, og:image) lengkap.")
        else:
            missing_og = []
            if not has_og_title: missing_og.append("og:title")
            if not has_og_desc: missing_og.append("og:description")
            if not has_og_image: missing_og.append("og:image")
            issues.append(f"LOW: OpenGraph tag belum lengkap: {', '.join(missing_og)}")

        # 6. JSON-LD Structured Data
        has_json_ld = bool(re.search(r'<script\s+type=["\']application/ld\+json["\']', html_content, re.IGNORECASE))
        if has_json_ld:
            passed.append("Structured data JSON-LD (Schema.org) terdeteksi.")
        else:
            issues.append("MEDIUM: Schema.org structured data (JSON-LD) belum disematkan.")

        score = max(0, 100 - (len(issues) * 15))

        return {
            "seo_score": score,
            "grade": "A" if score >= 85 else ("B" if score >= 70 else "C"),
            "passed_checks": passed,
            "issues": issues,
            "compliant": len(issues) == 0 or (score >= 70),
        }

    @staticmethod
    def validate_json_ld_schema(schema_text: str) -> Dict[str, Any]:
        """
        Memvalidasi struktur JSON-LD Schema.org agar valid dan bebas parsing error.
        """
        try:
            data = json.loads(schema_text)
            has_context = data.get("@context") in ["https://schema.org", "http://schema.org"]
            has_type = bool(data.get("@type"))

            if not has_context:
                return {"valid": False, "error": "Missing or invalid '@context', must be 'https://schema.org'"}
            if not has_type:
                return {"valid": False, "error": "Missing '@type' in Schema object"}

            return {
                "valid": True,
                "schema_type": data.get("@type"),
                "properties_count": len(data),
            }
        except json.JSONDecodeError as e:
            return {"valid": False, "error": f"JSON syntax error in JSON-LD: {e}"}

    @staticmethod
    def generate_sitemap_xml(urls: List[str], base_url: str = "https://dalang.ai") -> str:
        """
        Men-generate sitemap.xml standar untuk otomatisasi submit indexing.
        """
        url_nodes = []
        for u in urls:
            full_url = u if u.startswith("http") else f"{base_url.rstrip('/')}/{u.lstrip('/')}"
            url_nodes.append(f"  <url>\n    <loc>{full_url}</loc>\n    <changefreq>weekly</changefreq>\n    <priority>0.8</priority>\n  </url>")

        return (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            + "\n".join(url_nodes)
            + "\n</urlset>"
        )
