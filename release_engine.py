"""
Automated Semantic Release & Changelog Engine — Dalang-AI
Dikelola bersama oleh Nova (DevOps) dan Mika (Technical Writer).

Standar:
- Semantic Versioning 2.0.0 (SemVer: MAJOR.MINOR.PATCH)
- Conventional Commits 1.0.0 (feat, fix, docs, refactor, perf, sec)
- Keep a Changelog format (Added, Changed, Fixed, Security)
"""

import re
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ReleaseCommit:
    type: str  # feat, fix, sec, docs, refactor, perf
    scope: Optional[str]
    description: str
    is_breaking: bool = False
    raw_message: str = ""


@dataclass
class ReleaseVersion:
    major: int
    minor: int
    patch: int
    tag: str
    release_date: str
    changelog_section: str


class SemanticReleaseEngine:
    """
    Engine otomatisasi perilisan versi software dan generator changelog.
    """

    def __init__(self, current_version: str = "1.0.0"):
        self.current_version = self._parse_version(current_version)

    def _parse_version(self, version_str: str) -> tuple[int, int, int]:
        clean = version_str.lstrip("v").strip()
        parts = clean.split(".")
        return (int(parts[0]), int(parts[1]), int(parts[2]))

    def parse_commit_message(self, message: str) -> ReleaseCommit:
        """Mem-parse pesan commit bergaya Conventional Commits."""
        # Check for breaking change
        is_breaking = "BREAKING CHANGE:" in message or bool(re.search(r'^[a-z]+(\([a-z0-9_-]+\))?!:', message))

        match = re.match(r'^([a-z]+)(?:\(([a-z0-9_-]+)\))?!?:\s*(.*)', message.strip())
        if match:
            commit_type = match.group(1).lower()
            scope = match.group(2)
            desc = match.group(3)
        else:
            commit_type = "feat"
            scope = None
            desc = message.strip()

        return ReleaseCommit(
            type=commit_type,
            scope=scope,
            description=desc,
            is_breaking=is_breaking,
            raw_message=message,
        )

    def calculate_next_version(self, commits: List[ReleaseCommit]) -> ReleaseVersion:
        """
        Menghitung kenaikan versi berikutnya berdasarkan sifat commit:
        - Ada breaking change -> MAJOR increment (+1.0.0)
        - Ada 'feat' -> MINOR increment (0.+1.0)
        - Hanya 'fix', 'sec', atau lainnya -> PATCH increment (0.0.+1)
        """
        major, minor, patch = self.current_version

        has_breaking = any(c.is_breaking for c in commits)
        has_feat = any(c.type == "feat" for c in commits)

        if has_breaking:
            major += 1
            minor = 0
            patch = 0
        elif has_feat:
            minor += 1
            patch = 0
        else:
            patch += 1

        next_tag = f"v{major}.{minor}.{patch}"
        today_str = time.strftime("%Y-%m-%d", time.localtime())

        changelog = self.generate_changelog_section(next_tag, today_str, commits)

        return ReleaseVersion(
            major=major,
            minor=minor,
            patch=patch,
            tag=next_tag,
            release_date=today_str,
            changelog_section=changelog,
        )

    def generate_changelog_section(self, version_tag: str, release_date: str, commits: List[ReleaseCommit]) -> str:
        """Menghasilkan potongan CHANGELOG.md berstandar Keep a Changelog."""
        added = [c for c in commits if c.type == "feat"]
        fixed = [c for c in commits if c.type in ["fix", "bug"]]
        security = [c for c in commits if c.type in ["sec", "security"]]
        changed = [c for c in commits if c.type in ["refactor", "perf", "docs"]]

        lines = [f"## [{version_tag}] - {release_date}"]

        if security:
            lines.append("\n### 🛡️ Keamanan & Anti-Tamper")
            for c in security:
                scope_str = f"**({c.scope})** " if c.scope else ""
                lines.append(f"- {scope_str}{c.description}")

        if added:
            lines.append("\n### 🚀 Fitur Baru")
            for c in added:
                scope_str = f"**({c.scope})** " if c.scope else ""
                lines.append(f"- {scope_str}{c.description}")

        if fixed:
            lines.append("\n### 🐛 Perbaikan Bug")
            for c in fixed:
                scope_str = f"**({c.scope})** " if c.scope else ""
                lines.append(f"- {scope_str}{c.description}")

        if changed:
            lines.append("\n### ⚙️ Perubahan Arsitektur & Performa")
            for c in changed:
                scope_str = f"**({c.scope})** " if c.scope else ""
                lines.append(f"- {scope_str}{c.description}")

        return "\n".join(lines)
