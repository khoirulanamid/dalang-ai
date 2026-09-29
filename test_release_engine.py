"""
Test Suite untuk Automated Semantic Release & Changelog Engine
"""

import pytest
from release_engine import SemanticReleaseEngine, ReleaseCommit, ReleaseVersion


class TestSemanticReleaseEngine:
    def test_parse_conventional_commits(self):
        engine = SemanticReleaseEngine("1.0.0")

        c1 = engine.parse_commit_message("feat(auth): add constant-time HMAC signature verification")
        assert c1.type == "feat"
        assert c1.scope == "auth"
        assert "constant-time" in c1.description
        assert c1.is_breaking is False

        c2 = engine.parse_commit_message("fix(kinematics): flip Three.js knee pitch angle")
        assert c2.type == "fix"
        assert c2.scope == "kinematics"

        c3 = engine.parse_commit_message("feat!: complete rewrite of task router protocol\n\nBREAKING CHANGE: router API changed")
        assert c3.is_breaking is True

    def test_minor_version_bump_on_features(self):
        engine = SemanticReleaseEngine("1.2.4")
        commits = [
            engine.parse_commit_message("feat(tracer): add DAG algorithm visualizer"),
            engine.parse_commit_message("fix(api): handle timeout exception cleanly"),
        ]

        next_ver = engine.calculate_next_version(commits)
        assert next_ver.tag == "v1.3.0"
        assert next_ver.major == 1
        assert next_ver.minor == 3
        assert next_ver.patch == 0
        assert "Fitur Baru" in next_ver.changelog_section
        assert "Perbaikan Bug" in next_ver.changelog_section

    def test_patch_version_bump_on_bugfixes_only(self):
        engine = SemanticReleaseEngine("2.1.0")
        commits = [
            engine.parse_commit_message("fix(dom): prevent xss on innerHTML"),
            engine.parse_commit_message("sec(token): enforce algorithm pinning"),
        ]

        next_ver = engine.calculate_next_version(commits)
        assert next_ver.tag == "v2.1.1"
        assert "Keamanan" in next_ver.changelog_section

    def test_major_version_bump_on_breaking_change(self):
        engine = SemanticReleaseEngine("1.5.9")
        commits = [
            engine.parse_commit_message("feat!: deprecate old REST schema in favor of gRPC"),
        ]

        next_ver = engine.calculate_next_version(commits)
        assert next_ver.tag == "v2.0.0"
