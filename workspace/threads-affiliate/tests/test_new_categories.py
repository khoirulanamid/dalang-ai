"""Tests for new hook template categories: fashion, gadget, food."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

TEMPLATES_DIR = Path(__file__).parent.parent / "templates"
NEW_CATEGORIES = ["fashion", "gadget", "food"]
REQUIRED_HOOK_STYLES = [
    "edukasi",
    "validasi_mental",
    "storytelling",
    "problem_solving",
    "hook_pancingan",
    "transformasi",
    "social_proof",
    "urgency",
    "controversy",
]
MIN_VARIANTS_PER_STYLE = 3


class TestHookTemplateStructure:
    """Validate JSON structure and content of new hook template files."""

    @pytest.mark.parametrize("category", NEW_CATEGORIES)
    def test_template_file_exists(self, category: str) -> None:
        path = TEMPLATES_DIR / f"hooks_{category}.json"
        assert path.exists(), f"Missing template file: {path}"

    @pytest.mark.parametrize("category", NEW_CATEGORIES)
    def test_template_is_valid_json(self, category: str) -> None:
        path = TEMPLATES_DIR / f"hooks_{category}.json"
        data = json.loads(path.read_text())
        assert isinstance(data, dict)

    @pytest.mark.parametrize("category", NEW_CATEGORIES)
    def test_meta_block_present(self, category: str) -> None:
        path = TEMPLATES_DIR / f"hooks_{category}.json"
        data = json.loads(path.read_text())
        assert "_meta" in data
        meta = data["_meta"]
        assert meta["category"] == category
        assert meta["language"] == "id-ID"
        assert meta["tone"] == "casual-genz"
        assert "version" in meta

    @pytest.mark.parametrize("category", NEW_CATEGORIES)
    def test_all_nine_hook_styles_present(self, category: str) -> None:
        path = TEMPLATES_DIR / f"hooks_{category}.json"
        data = json.loads(path.read_text())
        hooks = data["hooks"]
        missing = [s for s in REQUIRED_HOOK_STYLES if s not in hooks]
        assert not missing, f"[{category}] Missing hook styles: {missing}"

    @pytest.mark.parametrize("category", NEW_CATEGORIES)
    def test_each_style_has_minimum_three_variants(self, category: str) -> None:
        path = TEMPLATES_DIR / f"hooks_{category}.json"
        data = json.loads(path.read_text())
        hooks = data["hooks"]
        for style in REQUIRED_HOOK_STYLES:
            variants = hooks.get(style, [])
            assert len(variants) >= MIN_VARIANTS_PER_STYLE, (
                f"[{category}][{style}] has {len(variants)} variants, need >= {MIN_VARIANTS_PER_STYLE}"
            )

    @pytest.mark.parametrize("category", NEW_CATEGORIES)
    def test_all_variants_contain_product_placeholder(self, category: str) -> None:
        path = TEMPLATES_DIR / f"hooks_{category}.json"
        data = json.loads(path.read_text())
        hooks = data["hooks"]
        for style, variants in hooks.items():
            for i, variant in enumerate(variants):
                assert "{product}" in variant, (
                    f"[{category}][{style}][{i}] missing {{product}} placeholder"
                )

    @pytest.mark.parametrize("category", NEW_CATEGORIES)
    def test_variants_are_non_empty_strings(self, category: str) -> None:
        path = TEMPLATES_DIR / f"hooks_{category}.json"
        data = json.loads(path.read_text())
        hooks = data["hooks"]
        for style, variants in hooks.items():
            for i, variant in enumerate(variants):
                assert isinstance(variant, str) and len(variant.strip()) > 0, (
                    f"[{category}][{style}][{i}] is empty or not a string"
                )

    @pytest.mark.parametrize("category", NEW_CATEGORIES)
    def test_product_placeholder_formats_correctly(self, category: str) -> None:
        path = TEMPLATES_DIR / f"hooks_{category}.json"
        data = json.loads(path.read_text())
        hooks = data["hooks"]
        for style, variants in hooks.items():
            for variant in variants:
                formatted = variant.format(product="TestProduct")
                assert "TestProduct" in formatted
                assert "{product}" not in formatted


class TestContentGeneratorNewCategories:
    """Integration tests for ContentGenerator with new categories."""

    @pytest.fixture
    def generator(self):
        from threads_poster.content_generator import ContentGenerator
        return ContentGenerator(templates_dir=TEMPLATES_DIR)

    @pytest.mark.parametrize("category", NEW_CATEGORIES)
    def test_generate_hook_returns_valid_text(self, generator, category: str) -> None:
        text, style = generator.generate_hook("Produk Test", category)
        assert isinstance(text, str) and len(text) > 0
        assert "Produk Test" in text
        assert style in REQUIRED_HOOK_STYLES

    @pytest.mark.parametrize("category", NEW_CATEGORIES)
    def test_generate_hook_with_explicit_style(self, generator, category: str) -> None:
        for style in REQUIRED_HOOK_STYLES:
            text, used_style = generator.generate_hook("Produk Test", category, hook_style=style)
            assert used_style == style
            assert "Produk Test" in text

    @pytest.mark.parametrize("category", NEW_CATEGORIES)
    def test_available_hook_styles_returns_all_nine(self, generator, category: str) -> None:
        styles = generator.available_hook_styles(category)
        assert set(REQUIRED_HOOK_STYLES).issubset(set(styles)), (
            f"[{category}] missing styles: {set(REQUIRED_HOOK_STYLES) - set(styles)}"
        )

    @pytest.mark.parametrize("category", NEW_CATEGORIES)
    def test_generate_chain_3_posts(self, generator, category: str) -> None:
        chain = generator.generate_chain(
            product="Produk Test",
            affiliate_link="https://s.shopee.co.id/test",
            category=category,
            num_posts=3,
        )
        assert "post_1" in chain
        assert "post_2" in chain
        assert "post_3" in chain
        assert chain["category"] == category
        assert chain["affiliate_link"] == "https://s.shopee.co.id/test"
        assert "Produk Test" in chain["post_1"]

    @pytest.mark.parametrize("category", NEW_CATEGORIES)
    def test_generate_chain_2_posts(self, generator, category: str) -> None:
        chain = generator.generate_chain(
            product="Produk Test",
            affiliate_link="https://s.shopee.co.id/test",
            category=category,
            num_posts=2,
        )
        assert "post_1" in chain
        assert "post_2" in chain
        assert "post_3" not in chain

    def test_invalid_category_raises_value_error(self, generator) -> None:
        with pytest.raises(ValueError, match="Category must be one of"):
            generator.generate_chain(
                product="X",
                affiliate_link="https://s.shopee.co.id/x",
                category="invalid_category",
            )

    @pytest.mark.parametrize("category", NEW_CATEGORIES)
    def test_generate_post2_returns_category_specific_template(
        self, generator, category: str
    ) -> None:
        text = generator.generate_post2("Produk Test", category)
        assert isinstance(text, str) and len(text) > 0


class TestCategoriesConstant:
    """Verify CATEGORIES constant includes all new categories."""

    def test_new_categories_in_constant(self) -> None:
        from threads_poster.content_generator import CATEGORIES
        for cat in NEW_CATEGORIES:
            assert cat in CATEGORIES, f"'{cat}' missing from CATEGORIES constant"

    def test_original_categories_still_present(self) -> None:
        from threads_poster.content_generator import CATEGORIES
        for cat in ["skincare", "parfum", "haircare", "makeup"]:
            assert cat in CATEGORIES, f"Original category '{cat}' was removed"


class TestPost2TemplatesNewCategories:
    """Verify post2_templates.json has entries for new categories."""

    @pytest.fixture
    def post2_data(self):
        path = TEMPLATES_DIR / "post2_templates.json"
        return json.loads(path.read_text())

    @pytest.mark.parametrize("category", NEW_CATEGORIES)
    def test_category_key_exists(self, post2_data: dict, category: str) -> None:
        assert category in post2_data, (
            f"post2_templates.json missing key for category '{category}'"
        )

    @pytest.mark.parametrize("category", NEW_CATEGORIES)
    def test_category_has_minimum_templates(self, post2_data: dict, category: str) -> None:
        templates = post2_data[category]
        assert len(templates) >= 3, (
            f"post2_templates.json[{category}] has {len(templates)} templates, need >= 3"
        )

    @pytest.mark.parametrize("category", NEW_CATEGORIES)
    def test_templates_contain_product_placeholder(self, post2_data: dict, category: str) -> None:
        templates = post2_data[category]
        for i, tmpl in enumerate(templates):
            assert "{product}" in tmpl, (
                f"post2_templates.json[{category}][{i}] missing {{product}} placeholder"
            )
