"""
Test Suite untuk Technical SEO & Core Web Vitals Auditor
"""

import pytest
from seo_auditor import TechnicalSEOAuditor


class TestTechnicalSEOAuditor:
    def test_audit_perfect_html_metadata(self):
        html = """<!DOCTYPE html>
        <html lang="id">
        <head>
          <meta charset="UTF-8">
          <meta name="viewport" content="width=device-width, initial-scale=1.0">
          <title>Dalang-AI — Multi-Agent Engineering Automation</title>
          <meta name="description" content="Platform otomasi multi-agent SDLC nyata karya Bos Muda dengan Three.js 3D studio dan zero-mock architecture.">
          <link rel="canonical" href="https://dalang.ai/">
          <meta property="og:title" content="Dalang-AI">
          <meta property="og:description" content="Multi-Agent Automation Platform">
          <meta property="og:image" content="https://dalang.ai/og-cover.png">
          <script type="application/ld+json">
          {
            "@context": "https://schema.org",
            "@type": "SoftwareApplication",
            "name": "Dalang-AI"
          }
          </script>
        </head>
        <body><div id="root"></div></body>
        </html>"""

        res = TechnicalSEOAuditor.audit_html_metadata(html)
        assert res["seo_score"] >= 85
        assert res["grade"] == "A"
        assert res["compliant"] is True
        assert len(res["issues"]) == 0

    def test_audit_missing_crucial_tags(self):
        bad_html = "<html><head></head><body>No meta</body></html>"
        res = TechnicalSEOAuditor.audit_html_metadata(bad_html)
        assert res["seo_score"] < 50
        assert any("title" in issue.lower() for issue in res["issues"])
        assert any("viewport" in issue.lower() for issue in res["issues"])

    def test_validate_valid_json_ld(self):
        valid_schema = """{
            "@context": "https://schema.org",
            "@type": "WebSite",
            "name": "Dalang-AI Studio",
            "url": "https://dalang.ai"
        }"""
        res = TechnicalSEOAuditor.validate_json_ld_schema(valid_schema)
        assert res["valid"] is True
        assert res["schema_type"] == "WebSite"

    def test_validate_invalid_json_ld(self):
        broken_schema = "{ bad json"
        res = TechnicalSEOAuditor.validate_json_ld_schema(broken_schema)
        assert res["valid"] is False
        assert "syntax error" in res["error"]

    def test_generate_sitemap_xml(self):
        urls = ["/", "/docs/architecture", "/docs/quickstart"]
        xml = TechnicalSEOAuditor.generate_sitemap_xml(urls, base_url="https://dalang.ai")
        assert "<?xml version=" in xml
        assert "<loc>https://dalang.ai/</loc>" in xml
        assert "<loc>https://dalang.ai/docs/architecture</loc>" in xml
