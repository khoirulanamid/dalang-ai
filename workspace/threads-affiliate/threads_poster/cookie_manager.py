"""Cookie extraction from Chrome (via browser_cookie3)."""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional


DEFAULT_COOKIES_DIR = Path.home() / ".threads_poster" / "cookies"

# Permitted cookie directory must be under home — prevents path traversal
_SAFE_COOKIE_ROOT = Path.home()


def _assert_safe_path(path: Path) -> None:
    """Reject any cookie path that escapes the user home directory."""
    try:
        path.resolve().relative_to(_SAFE_COOKIE_ROOT.resolve())
    except ValueError:
        raise ValueError(
            f"Cookie path '{path}' is outside the permitted root "
            f"'{_SAFE_COOKIE_ROOT}'. Refusing to write session data there."
        )


def list_chrome_profiles() -> list[Path]:
    """List Chrome profile directories on the current OS."""
    chrome_root = _chrome_root()
    if not chrome_root.exists():
        return []
    return [
        p for p in chrome_root.iterdir()
        if p.is_dir() and (p.name == "Default" or p.name.startswith("Profile "))
    ]


def _chrome_root() -> Path:
    """OS-specific Chrome user-data directory."""
    import platform
    sys = platform.system()
    if sys == "Darwin":
        return Path.home() / "Library/Application Support/Google/Chrome"
    elif sys == "Linux":
        return Path.home() / ".config/google-chrome"
    elif sys == "Windows":
        return Path(os.environ.get("LOCALAPPDATA", "")) / "Google/Chrome/User Data"
    else:
        raise OSError(f"Unsupported OS: {sys}")


def extract_cookies(
    chrome_profile: str = "Default",
    output_path: Optional[Path] = None,
) -> Path:
    """Extract Instagram + Threads cookies from a Chrome profile.

    Args:
        chrome_profile: Profile name (e.g. "Default", "Profile 1")
        output_path: Where to save. Defaults to ~/.threads_poster/cookies/session.json

    Returns:
        Path to saved cookie file
    """
    import browser_cookie3

    profile_path = _chrome_root() / chrome_profile / "Cookies"
    if not profile_path.exists():
        raise FileNotFoundError(
            f"Chrome cookies DB not found at {profile_path}. "
            f"Available profiles: {[p.name for p in list_chrome_profiles()]}"
        )

    # Extract Instagram cookies
    ig_jar = browser_cookie3.chrome(
        domain_name=".instagram.com",
        cookie_file=str(profile_path),
    )
    ig_cookies = {c.name: c.value for c in ig_jar}

    # Extract Threads cookies
    threads_jar = browser_cookie3.chrome(
        domain_name=".threads.net",
        cookie_file=str(profile_path),
    )
    threads_cookies = {c.name: c.value for c in threads_jar}

    payload = {
        "instagram": ig_cookies,
        "threads": threads_cookies,
    }

    if output_path is None:
        output_path = DEFAULT_COOKIES_DIR / "session.json"

    output_path = Path(output_path).expanduser().resolve()

    # Guard: cookie file must stay inside home directory
    _assert_safe_path(output_path)

    # Create parent directory with owner-only permissions (700).
    # mode=0o700 is passed explicitly so the directory is never world-readable,
    # even if the process umask is permissive.
    output_path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)

    # Enforce 700 on every ancestor we created up to the safe root, because
    # mkdir(mode=) is subject to umask on some systems.
    _harden_dir_permissions(output_path.parent)

    output_path.write_text(json.dumps(payload, indent=2))

    # 600: owner read/write only — no group or world access to session tokens
    os.chmod(output_path, 0o600)

    return output_path


def _harden_dir_permissions(directory: Path) -> None:
    """Ensure directory and its parents (up to home) are mode 700."""
    target = directory.resolve()
    home = _SAFE_COOKIE_ROOT.resolve()
    current = target
    while True:
        try:
            current.relative_to(home)
        except ValueError:
            break
        try:
            current.chmod(0o700)
        except PermissionError:
            break
        if current == home:
            break
        current = current.parent


def validate_cookies(cookies_path: Path | str) -> tuple[bool, dict]:
    """Test if cookies still grant authenticated access.

    Returns:
        (valid: bool, details: dict)
    """
    import urllib.request
    import urllib.error

    cookies_path = Path(cookies_path).expanduser()
    if not cookies_path.exists():
        return False, {"error": f"Cookie file not found: {cookies_path}"}

    data = json.loads(cookies_path.read_text())
    ig_cookies = data.get("instagram", {})

    if not ig_cookies:
        return False, {"error": "No Instagram cookies in file"}

    # Use Instagram web profile info endpoint
    sessionid = ig_cookies.get("sessionid", "")
    username = "instagram"  # use Instagram's own account as test target

    cookie_header = "; ".join(f"{k}={v}" for k, v in ig_cookies.items())
    req = urllib.request.Request(
        f"https://www.instagram.com/api/v1/users/web_profile_info/?username={username}",
        headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                          "AppleWebKit/537.36 Chrome/149.0.0.0 Safari/537.36",
            "Cookie": cookie_header,
            "X-IG-App-ID": "936619743392459",
            "X-Requested-With": "XMLHttpRequest",
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = json.loads(resp.read())
        user = body.get("data", {}).get("user", {})
        if user.get("username"):
            return True, {
                "session_user_id": ig_cookies.get("ds_user_id", "?"),
                "verified_via": "web_profile_info",
            }
    except urllib.error.HTTPError as e:
        return False, {"error": f"HTTP {e.code}", "body": e.read().decode()[:200]}
    except Exception as e:
        return False, {"error": str(e)}

    return False, {"error": "Could not verify session"}
