"""
test_frontend_auth.py
=====================
Tests for the frontend_auth SPA files:
  - frontend_auth/index.html
  - frontend_auth/style.css
  - frontend_auth/app.js

Validates structure, required elements, API endpoint references,
CSS class coverage, and JS logic correctness.
"""

import os
import re
import pytest

FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "frontend_auth")
HTML_FILE = os.path.join(FRONTEND_DIR, "index.html")
CSS_FILE = os.path.join(FRONTEND_DIR, "style.css")
JS_FILE = os.path.join(FRONTEND_DIR, "app.js")


# ─────────────────────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def html():
    with open(HTML_FILE, encoding="utf-8") as f:
        return f.read()


@pytest.fixture(scope="module")
def css():
    with open(CSS_FILE, encoding="utf-8") as f:
        return f.read()


@pytest.fixture(scope="module")
def js():
    with open(JS_FILE, encoding="utf-8") as f:
        return f.read()


# ─────────────────────────────────────────────────────────────────────────────
# File Existence
# ─────────────────────────────────────────────────────────────────────────────

class TestFilesExist:
    def test_html_exists(self):
        assert os.path.isfile(HTML_FILE), "index.html not found"

    def test_css_exists(self):
        assert os.path.isfile(CSS_FILE), "style.css not found"

    def test_js_exists(self):
        assert os.path.isfile(JS_FILE), "app.js not found"

    def test_html_non_empty(self):
        assert os.path.getsize(HTML_FILE) > 1000, "index.html appears too small"

    def test_css_non_empty(self):
        assert os.path.getsize(CSS_FILE) > 1000, "style.css appears too small"

    def test_js_non_empty(self):
        assert os.path.getsize(JS_FILE) > 1000, "app.js appears too small"


# ─────────────────────────────────────────────────────────────────────────────
# HTML Structure Tests
# ─────────────────────────────────────────────────────────────────────────────

class TestHTMLStructure:
    def test_doctype(self, html):
        assert html.strip().lower().startswith("<!doctype html>"), "Missing DOCTYPE"

    def test_charset_utf8(self, html):
        assert 'charset="UTF-8"' in html or "charset='UTF-8'" in html.lower()

    def test_viewport_meta(self, html):
        assert "viewport" in html

    def test_title(self, html):
        assert "<title>" in html and "Dalang-AI" in html

    def test_css_link(self, html):
        assert 'href="style.css"' in html, "style.css not linked"

    def test_js_script(self, html):
        assert 'src="app.js"' in html, "app.js not linked"

    # Sections
    def test_auth_section(self, html):
        assert 'id="auth-section"' in html

    def test_dashboard_section(self, html):
        assert 'id="dashboard-section"' in html

    # Tabs
    def test_tab_login_button(self, html):
        assert 'id="tab-login"' in html

    def test_tab_register_button(self, html):
        assert 'id="tab-register"' in html

    def test_login_pane(self, html):
        assert 'id="login-pane"' in html

    def test_register_pane(self, html):
        assert 'id="register-pane"' in html

    # Login Form
    def test_login_form(self, html):
        assert 'id="login-form"' in html

    def test_login_username_input(self, html):
        assert 'id="login-username"' in html

    def test_login_password_input(self, html):
        assert 'id="login-password"' in html

    def test_login_remember_checkbox(self, html):
        assert 'id="login-remember"' in html

    def test_login_submit_button(self, html):
        assert 'id="login-submit-btn"' in html

    def test_login_error_element(self, html):
        assert 'id="login-error"' in html

    # Register Form
    def test_register_form(self, html):
        assert 'id="register-form"' in html

    def test_register_username_input(self, html):
        assert 'id="register-username"' in html

    def test_register_email_input(self, html):
        assert 'id="register-email"' in html

    def test_register_fullname_input(self, html):
        assert 'id="register-fullname"' in html

    def test_register_role_select(self, html):
        assert 'id="register-role"' in html

    def test_register_password_input(self, html):
        assert 'id="register-password"' in html

    def test_register_confirm_password_input(self, html):
        assert 'id="register-confirm-password"' in html

    def test_register_submit_button(self, html):
        assert 'id="register-submit-btn"' in html

    def test_register_error_element(self, html):
        assert 'id="register-error"' in html

    def test_register_success_element(self, html):
        assert 'id="register-success"' in html

    def test_password_strength_bar(self, html):
        assert 'id="password-strength-fill"' in html

    # Dashboard Elements
    def test_user_avatar_initials(self, html):
        assert 'id="user-avatar-initials"' in html

    def test_user_display_name(self, html):
        assert 'id="user-display-name"' in html

    def test_user_role_badge(self, html):
        assert 'id="user-role-badge"' in html

    def test_logout_button(self, html):
        assert 'id="logout-btn"' in html

    def test_detail_username(self, html):
        assert 'id="detail-username"' in html

    def test_detail_email(self, html):
        assert 'id="detail-email"' in html

    def test_detail_role(self, html):
        assert 'id="detail-role"' in html

    def test_detail_id(self, html):
        assert 'id="detail-id"' in html

    def test_detail_created(self, html):
        assert 'id="detail-created"' in html

    def test_detail_updated(self, html):
        assert 'id="detail-updated"' in html

    def test_access_token_display(self, html):
        assert 'id="access-token-display"' in html

    def test_refresh_token_display(self, html):
        assert 'id="refresh-token-display"' in html

    def test_copy_access_token_button(self, html):
        assert 'id="copy-access-token"' in html

    def test_copy_refresh_token_button(self, html):
        assert 'id="copy-refresh-token"' in html

    def test_refresh_token_btn(self, html):
        assert 'id="refresh-token-btn"' in html

    def test_reload_profile_btn(self, html):
        assert 'id="reload-profile-btn"' in html

    # Settings Panel
    def test_settings_panel(self, html):
        assert 'id="settings-panel"' in html

    def test_api_base_url_input(self, html):
        assert 'id="api-base-url"' in html

    def test_save_settings_btn(self, html):
        assert 'id="save-settings-btn"' in html

    # Notification
    def test_notification_element(self, html):
        assert 'id="notification"' in html

    def test_notification_message(self, html):
        assert 'id="notification-message"' in html

    # Role options in select
    def test_role_option_user(self, html):
        assert 'value="user"' in html

    def test_role_option_admin(self, html):
        assert 'value="admin"' in html

    # Password toggle buttons
    def test_password_toggle_buttons(self, html):
        assert "toggle-password" in html

    # Switch links
    def test_switch_to_register_link(self, html):
        assert 'id="switch-to-register"' in html

    def test_switch_to_login_link(self, html):
        assert 'id="switch-to-login"' in html

    # Spinner elements
    def test_spinner_elements(self, html):
        assert 'class="spinner' in html

    # Accessibility
    def test_aria_labels_present(self, html):
        assert "aria-label" in html

    def test_role_alert_on_notification(self, html):
        assert 'role="alert"' in html

    def test_novalidate_on_forms(self, html):
        assert "novalidate" in html


# ─────────────────────────────────────────────────────────────────────────────
# CSS Tests
# ─────────────────────────────────────────────────────────────────────────────

class TestCSSStructure:
    def test_css_variables_defined(self, css):
        assert ":root" in css
        assert "--color-primary" in css
        assert "--color-bg" in css
        assert "--color-surface" in css
        assert "--color-error" in css
        assert "--color-success" in css

    def test_responsive_media_query(self, css):
        assert "@media" in css

    def test_card_class(self, css):
        assert ".card" in css

    def test_tabs_class(self, css):
        assert ".tabs" in css

    def test_tab_btn_class(self, css):
        assert ".tab-btn" in css

    def test_tab_pane_class(self, css):
        assert ".tab-pane" in css

    def test_form_group_class(self, css):
        assert ".form-group" in css

    def test_btn_primary_class(self, css):
        assert ".btn-primary" in css

    def test_btn_block_class(self, css):
        assert ".btn-block" in css

    def test_spinner_class(self, css):
        assert ".spinner" in css

    def test_notification_class(self, css):
        assert ".notification" in css

    def test_dashboard_class(self, css):
        assert ".dashboard" in css

    def test_badge_class(self, css):
        assert ".badge" in css

    def test_hidden_class(self, css):
        assert ".hidden" in css

    def test_font_mono_class(self, css):
        assert ".font-mono" in css

    def test_password_strength_classes(self, css):
        assert ".strength-fill" in css
        assert ".weak" in css
        assert ".strong" in css

    def test_token_box_class(self, css):
        assert ".token-box" in css

    def test_details_grid_class(self, css):
        assert ".details-grid" in css

    def test_avatar_badge_class(self, css):
        assert ".avatar-badge" in css

    def test_settings_panel_class(self, css):
        assert ".settings-panel" in css

    def test_animation_keyframes(self, css):
        assert "@keyframes" in css

    def test_transition_defined(self, css):
        assert "transition" in css

    def test_form_error_class(self, css):
        assert ".form-error" in css

    def test_form_success_class(self, css):
        assert ".form-success" in css

    def test_app_header_class(self, css):
        assert ".app-header" in css

    def test_app_footer_class(self, css):
        assert ".app-footer" in css

    def test_brand_class(self, css):
        assert ".brand" in css

    def test_input_wrapper_class(self, css):
        assert ".input-wrapper" in css

    def test_toggle_password_class(self, css):
        assert ".toggle-password" in css


# ─────────────────────────────────────────────────────────────────────────────
# JavaScript Tests
# ─────────────────────────────────────────────────────────────────────────────

class TestJSStructure:
    # API Endpoints
    def test_login_endpoint(self, js):
        assert "'/login'" in js or '"/login"' in js

    def test_register_endpoint(self, js):
        assert "'/register'" in js or '"/register"' in js

    def test_refresh_endpoint(self, js):
        assert "'/refresh'" in js or '"/refresh"' in js

    def test_me_endpoint(self, js):
        assert "'/me'" in js or '"/me"' in js

    # HTTP Methods
    def test_post_method_used(self, js):
        assert "method: 'POST'" in js or 'method: "POST"' in js

    def test_get_method_implied(self, js):
        # GET is the default; /me is called without explicit method
        assert "'/me'" in js or '"/me"' in js

    # Authorization Header
    def test_bearer_auth_header(self, js):
        assert "Bearer" in js
        assert "Authorization" in js

    # Token Storage Keys
    def test_access_token_storage_key(self, js):
        assert "ACCESS_TOKEN" in js

    def test_refresh_token_storage_key(self, js):
        assert "REFRESH_TOKEN" in js

    def test_remember_me_storage_key(self, js):
        assert "REMEMBER_ME" in js

    def test_api_base_url_storage_key(self, js):
        assert "API_BASE_URL" in js

    # Core Functions
    def test_handle_login_function(self, js):
        assert "handleLogin" in js

    def test_handle_register_function(self, js):
        assert "handleRegister" in js

    def test_handle_refresh_token_function(self, js):
        assert "handleRefreshToken" in js

    def test_handle_reload_profile_function(self, js):
        assert "handleReloadProfile" in js

    def test_handle_logout_function(self, js):
        assert "handleLogout" in js

    def test_try_auto_login_function(self, js):
        assert "tryAutoLogin" in js

    def test_show_dashboard_function(self, js):
        assert "showDashboard" in js

    def test_show_auth_section_function(self, js):
        assert "showAuthSection" in js

    def test_switch_tab_function(self, js):
        assert "switchTab" in js

    def test_save_tokens_function(self, js):
        assert "saveTokens" in js

    def test_clear_tokens_function(self, js):
        assert "clearTokens" in js

    def test_api_request_function(self, js):
        assert "apiRequest" in js

    def test_get_api_url_function(self, js):
        assert "getApiUrl" in js

    def test_show_notification_function(self, js):
        assert "showNotification" in js

    def test_render_user_profile_function(self, js):
        assert "renderUserProfile" in js

    def test_render_token_snippets_function(self, js):
        assert "renderTokenSnippets" in js

    def test_evaluate_password_strength_function(self, js):
        assert "evaluatePasswordStrength" in js

    def test_update_password_strength_ui_function(self, js):
        assert "updatePasswordStrengthUI" in js

    def test_set_button_loading_function(self, js):
        assert "setButtonLoading" in js

    # Client-side Validation
    def test_username_regex_validation(self, js):
        assert "usernameRegex" in js or "USERNAME_REGEX" in js or r"[a-zA-Z0-9_.-]" in js

    def test_email_regex_validation(self, js):
        assert "emailRegex" in js or "EMAIL_REGEX" in js or r"[^@\s]" in js

    def test_password_length_validation(self, js):
        assert "password.length < 8" in js or "minlength" in js

    def test_password_confirm_validation(self, js):
        assert "password !== confirmPassword" in js or "confirmPassword" in js

    # Error Handling
    def test_error_status_handling(self, js):
        assert "err.status" in js or "error.status" in js

    def test_401_handling(self, js):
        assert "401" in js

    def test_network_error_handling(self, js):
        assert "Network error" in js or "networkError" in js

    def test_fastapi_detail_array_parsing(self, js):
        assert "Array.isArray" in js and "detail" in js

    # Token Management
    def test_localstorage_usage(self, js):
        assert "localStorage" in js

    def test_sessionstorage_usage(self, js):
        assert "sessionStorage" in js

    def test_access_token_in_request_body(self, js):
        assert "access_token" in js

    def test_refresh_token_in_request_body(self, js):
        assert "refresh_token" in js

    # Auto-login
    def test_auto_login_on_init(self, js):
        assert "tryAutoLogin" in js
        assert "DOMContentLoaded" in js or "init()" in js

    # Clipboard
    def test_clipboard_api_usage(self, js):
        assert "clipboard" in js

    # Password Strength Levels
    def test_password_strength_levels(self, js):
        assert "weak" in js
        assert "fair" in js
        assert "good" in js
        assert "strong" in js

    # IIFE / Strict Mode
    def test_strict_mode(self, js):
        assert "'use strict'" in js or '"use strict"' in js

    def test_iife_pattern(self, js):
        assert "(function" in js or "(() =>" in js

    # Debug export
    def test_debug_export(self, js):
        assert "__rippleAuthApp" in js

    # JSON body serialization
    def test_json_stringify_used(self, js):
        assert "JSON.stringify" in js

    # Content-Type header
    def test_content_type_json(self, js):
        assert "application/json" in js

    # Fetch API
    def test_fetch_api_used(self, js):
        assert "fetch(" in js or "await fetch" in js


# ─────────────────────────────────────────────────────────────────────────────
# Integration: Cross-file Consistency
# ─────────────────────────────────────────────────────────────────────────────

class TestCrossFileConsistency:
    """Ensure IDs referenced in JS match those defined in HTML."""

    def _extract_html_ids(self, html):
        return set(re.findall(r'id="([^"]+)"', html))

    def _extract_js_get_element_by_id(self, js):
        return set(re.findall(r"getElementById\(['\"]([^'\"]+)['\"]\)", js))

    def test_all_js_ids_exist_in_html(self, html, js):
        html_ids = self._extract_html_ids(html)
        js_ids = self._extract_js_get_element_by_id(js)
        missing = js_ids - html_ids
        assert not missing, (
            f"JS references IDs not found in HTML: {missing}"
        )

    def test_css_classes_used_in_html(self, html, css):
        """Spot-check that key CSS classes appear in HTML."""
        key_classes = [
            "card", "tabs", "tab-btn", "tab-pane", "form-group",
            "btn", "btn-primary", "spinner", "notification",
            "badge", "hidden", "avatar-badge", "token-box",
        ]
        for cls in key_classes:
            assert cls in html, f"CSS class '{cls}' not found in HTML"
            assert f".{cls}" in css, f"CSS class '.{cls}' not defined in CSS"
