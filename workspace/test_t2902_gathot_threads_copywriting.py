#!/usr/bin/env python3
"""
Test Suite for Task T-2902: Gathot Threads Viral Copywriting Strategy
Compliance validation for docs/sprint29_campaign.json
"""
import json
import os
import re
import pytest

CAMPAIGN_FILE = "docs/sprint29_campaign.json"
EXPECTED_AFFILIATE_URL = "https://s.shopee.co.id/8AWbWHUOPx"

@pytest.fixture
def campaign_data():
    assert os.path.exists(CAMPAIGN_FILE), f"Campaign file {CAMPAIGN_FILE} not found!"
    with open(CAMPAIGN_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data

def test_campaign_metadata_and_status(campaign_data):
    """Verify basic product and campaign metadata."""
    assert campaign_data.get("product_id") == "homedoki-rak-piring-wastafel-penutup"
    assert "Homedoki Rak Piring Wastafel" in campaign_data.get("product_name", "")
    assert campaign_data.get("status") == "ready_for_campaign"
    assert campaign_data.get("affiliate_url") == EXPECTED_AFFILIATE_URL
    assert "Peralatan Dapur" in campaign_data.get("category", "") or "Rak Dapur" in campaign_data.get("category", "")
    assert len(campaign_data.get("specs", [])) >= 4

def test_target_audience_and_strategy(campaign_data):
    """Verify target audience definition and strategy align with Gathot standards."""
    strat = campaign_data.get("campaign_strategy", {})
    assert "threads_viral_strategy" in strat
    assert strat["threads_viral_strategy"]["framework"] == "2-Post Thread Split (Post 1: Situational Hook / Dilemma -> Post 2: Curated Specs & Soft CTA Shopee)"
    
    camp = campaign_data.get("campaign", {})
    audience = camp.get("target_audience", {})
    assert "demographics" in audience
    assert len(audience.get("pain_points", [])) >= 3
    assert "tone_and_manner" in audience

def test_copywriting_angles_threads_standards(campaign_data):
    """Verify Threads copywriting complies with Diátaxis & Meta character limits and format."""
    angles = campaign_data.get("campaign", {}).get("copywriting_angles", [])
    assert len(angles) >= 3, "Minimum 3 diverse copywriting angles required."

    forbidden_patterns = [
        r"\baku\s+(sudah|udah|pernah|pake|pakai|coba|beli)\b",
        r"\bsaya\s+(sudah|udah|pernah|pake|pakai|coba|beli)\b",
        r"\bpiring\s+aku\b",
        r"\bdapur\s+aku\b",
        r"\brumah\s+aku\b",
        r"\bdi\s+dapurku\b"
    ]

    for angle in angles:
        threads = angle.get("threads", {})
        assert "post_1" in threads, f"Missing post_1 in {angle['angle_id']}"
        assert "post_2" in threads, f"Missing post_2 in {angle['angle_id']}"

        p1_cap = threads["post_1"]["caption"]
        p2_cap = threads["post_2"]["caption"]

        # Thread split format
        assert threads["post_1"]["type"] == "hook_relatable"
        assert threads["post_2"]["type"] == "spec_curation_cta"

        # Character limit <= 500
        assert len(p1_cap) <= 500, f"Post 1 in {angle['angle_id']} exceeds 500 chars: {len(p1_cap)}"
        assert len(p2_cap) <= 500, f"Post 2 in {angle['angle_id']} exceeds 500 chars: {len(p2_cap)}"

        # Non-empty and reasonable length
        assert len(p1_cap) >= 80, f"Post 1 in {angle['angle_id']} too short: {len(p1_cap)}"
        assert len(p2_cap) >= 150, f"Post 2 in {angle['angle_id']} too short: {len(p2_cap)}"

        # Exact CTA affiliate URL in Post 2
        assert EXPECTED_AFFILIATE_URL in p2_cap, f"Affiliate link missing in {angle['angle_id']} Post 2"

        # Targeted hashtags 3-5 in Post 2
        p2_tags = re.findall(r"#[A-Za-z0-9_]+", p2_cap)
        assert 3 <= len(p2_tags) <= 5, f"Hashtag count {len(p2_tags)} not between 3 and 5 in {angle['angle_id']} Post 2"

        # Anti-fabrication check
        for pat in forbidden_patterns:
            assert not re.search(pat, p1_cap, re.IGNORECASE), f"Forbidden pattern {pat} in {angle['angle_id']} Post 1"
            assert not re.search(pat, p2_cap, re.IGNORECASE), f"Forbidden pattern {pat} in {angle['angle_id']} Post 2"

def test_media_reference_validity(campaign_data):
    """Verify that visual notes reference valid downloaded media assets."""
    assets = [a["file_name"] for a in campaign_data.get("media", {}).get("assets", [])]
    assert len(assets) > 0, "No media assets found in campaign."

    angles = campaign_data.get("campaign", {}).get("copywriting_angles", [])
    for angle in angles:
        for platform in ["threads", "facebook", "instagram"]:
            for post_key in ["post_1", "post_2"]:
                vnote = angle[platform][post_key].get("visual_note", "")
                assert any(asset in vnote for asset in assets), f"Visual note '{vnote}' does not reference any downloaded asset"

def test_multichannel_platform_strategy(campaign_data):
    """Verify platform strategies for Threads, Facebook, and Instagram."""
    platforms = campaign_data.get("campaign", {}).get("platform_strategy", {})
    assert "threads" in platforms
    assert "facebook" in platforms
    assert "instagram" in platforms
    for plat in ["threads", "facebook", "instagram"]:
        assert len(platforms[plat].get("recommended_posting_hours_wib", [])) >= 2
