"""
Test Suite untuk Database Security Guard & Misconfiguration Audit (OWASP DB Security)
"""

import pytest
from db_security_guard import DatabaseSecurityGuard


class TestDatabaseSecurityGuard:
    def test_detect_insecure_connection_strings(self):
        # Insecure 0.0.0.0 binding & hardcoded password
        bad_uri = "postgresql://dbuser:supersecret123@0.0.0.0:5432/production_db"
        report = DatabaseSecurityGuard.audit_connection_string(bad_uri)
        assert report["safe"] is False
        assert any("0.0.0.0" in issue for issue in report["issues"])
        assert any("plaintext password" in issue for issue in report["issues"])
        assert "supersecret123" not in report["sanitized_uri"]

    def test_safe_connection_string(self):
        safe_uri = "postgresql://app_user:${DB_PASS}@localhost:5432/app_db"
        report = DatabaseSecurityGuard.audit_connection_string(safe_uri)
        assert report["safe"] is True
        assert len(report["issues"]) == 0

    def test_remote_missing_tls(self):
        remote_uri = "postgresql://app_user:${DB_PASS}@db.example.internal:5432/app_db"
        report = DatabaseSecurityGuard.audit_connection_string(remote_uri)
        assert any("TLS" in issue for issue in report["issues"])

    def test_detect_dangerous_sql_injection_patterns(self):
        bad_query_fstring = 'f"SELECT * FROM users WHERE username = \'{user_input}\'"'
        is_safe, issues = DatabaseSecurityGuard.inspect_query_safety(bad_query_fstring)
        assert is_safe is False
        assert any("f-string" in issue for issue in issues)

        bad_query_concat = '"SELECT * FROM items WHERE id = " + str(item_id)'
        is_safe, issues = DatabaseSecurityGuard.inspect_query_safety(bad_query_concat)
        assert is_safe is False
        assert any("concatenation" in issue for issue in issues)

    def test_safe_sql_query(self):
        safe_query = "cursor.execute('SELECT * FROM users WHERE username = %s', (user_input,))"
        is_safe, issues = DatabaseSecurityGuard.inspect_query_safety(safe_query)
        assert is_safe is True
        assert len(issues) == 0

    def test_verify_role_privileges(self):
        violating_grants = ["SELECT", "INSERT", "SUPERUSER", "COPY PROGRAM"]
        is_compliant, violations = DatabaseSecurityGuard.verify_role_privilege(violating_grants)
        assert is_compliant is False
        assert len(violations) == 2
        assert any("SUPERUSER" in v for v in violations)

        safe_grants = ["SELECT", "INSERT", "UPDATE", "DELETE"]
        is_compliant, violations = DatabaseSecurityGuard.verify_role_privilege(safe_grants)
        assert is_compliant is True
        assert len(violations) == 0
