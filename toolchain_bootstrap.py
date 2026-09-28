"""
Toolchain Bootstrapper & Status Index untuk Dalang-AI
Dikelola oleh Nova (Wayang Patih — DevOps & SRE Specialist)
Terinspirasi dari skills/ops/skill-supply-chain.md di zhaoxuya520/reverse-skill

Menyediakan audit status toolchain secara terstruktur dan resep bootstrap yang terisolasi.
"""

import shutil
import subprocess
from typing import Any, Dict, List, Optional


KNOWN_TOOLCHAIN = {
    "python": {"cmd": "python3", "category": "runtime", "desc": "Python 3.11+ Interpreter"},
    "pytest": {"cmd": "pytest", "category": "testing", "desc": "Python Test Runner (Ren)"},
    "ruff": {"cmd": "ruff", "category": "linter", "desc": "High-Performance Python Linter (Zaki)"},
    "bandit": {"cmd": "bandit", "category": "security", "desc": "Python SAST Security Scanner (Kai)"},
    "pip-audit": {"cmd": "pip-audit", "category": "security", "desc": "Dependency Vulnerability Scanner (Kai)"},
    "node": {"cmd": "node", "category": "runtime", "desc": "Node.js JavaScript Runtime (Lulu)"},
    "npm": {"cmd": "npm", "category": "package_manager", "desc": "Node Package Manager (Lulu)"},
    "git": {"cmd": "git", "category": "vcs", "desc": "Git Version Control (Nova)"},
    "docker": {"cmd": "docker", "category": "container", "desc": "Containerization Engine (Nova)"},
}


def check_tool_available(tool_name: str) -> Dict[str, Any]:
    """Memeriksa ketersediaan executable tool di sistem."""
    info = KNOWN_TOOLCHAIN.get(tool_name.lower())
    cmd = info["cmd"] if info else tool_name
    found_path = shutil.which(cmd)

    version_str = None
    if found_path:
        try:
            res = subprocess.run([found_path, "--version"], capture_output=True, text=True, timeout=5)
            version_str = (res.stdout or res.stderr).strip().splitlines()[0] if (res.stdout or res.stderr) else "detected"
        except Exception:
            version_str = "detected"

    return {
        "tool": tool_name,
        "available": bool(found_path),
        "path": found_path,
        "version": version_str,
        "category": info["category"] if info else "custom",
        "description": info["desc"] if info else "Custom tool",
    }


def audit_full_toolchain() -> Dict[str, Dict]:
    """Mengaudit seluruh toolchain standar Dalang-AI."""
    status = {}
    for name in KNOWN_TOOLCHAIN:
        status[name] = check_tool_available(name)
    return status


def get_bootstrap_recipe(tool_name: str) -> Optional[str]:
    """
    Memberikan resep instalasi aman (hermetic/pinned) tanpa mengotori host root jika memungkinkan.
    """
    recipes = {
        "bandit": "pip install --no-cache-dir bandit",
        "pip-audit": "pip install --no-cache-dir pip-audit",
        "ruff": "pip install --no-cache-dir ruff",
        "pytest": "pip install --no-cache-dir pytest pytest-asyncio",
    }
    return recipes.get(tool_name.lower())
