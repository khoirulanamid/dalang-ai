"""
Database Security & Misconfiguration Guard — Dalang-AI Data Security Engine
Terinspirasi dari skills/database-security di zhaoxuya520/reverse-skill

Membantu Pingot (Data Architect) dan Zaki (Backend) melakukan:
1. Audit connection string (pencegahan eksposur password dan binding 0.0.0.0)
2. Deteksi SQL & NoSQL injection vulnerability patterns pada kode data
3. Verifikasi Principle of Least Privilege (PoLP) pada konfigurasi database
"""

import re
from typing import Any, Dict, List, Optional, Tuple


class DatabaseSecurityGuard:
    """
    Audit keamanan lapisan basis data untuk mencegah salah konfigurasi dan celah injeksi.
    """

    @staticmethod
    def audit_connection_string(conn_uri: str) -> Dict[str, Any]:
        """
        Memeriksa apakah connection URI mengandung plaintext secret atau terikat ke interface publik tanpa TLS.
        """
        issues = []
        is_safe = True

        # Deteksi binding host publik 0.0.0.0
        if "0.0.0.0" in conn_uri:
            issues.append("CRITICAL: Database connection terikat ke interface publik 0.0.0.0 tanpa isolasi.")
            is_safe = False

        # Deteksi plaintext credentials di URI
        user_pass_match = re.search(r"://([^:@]+):([^@]+)@", conn_uri)
        if user_pass_match:
            user, pwd = user_pass_match.group(1), user_pass_match.group(2)
            if pwd and pwd not in ["${DB_PASS}", "password", "$PASSWORD", "env"]:
                issues.append("HIGH: Hardcoded plaintext password terdeteksi pada connection URI.")
                is_safe = False

        # Deteksi ketiadaan enkripsi TLS untuk koneksi remote (bukan localhost)
        is_remote = not any(h in conn_uri for h in ["localhost", "127.0.0.1", "sqlite"])
        if is_remote and "sslmode=require" not in conn_uri and "ssl=true" not in conn_uri:
            issues.append("MEDIUM: Remote database connection tidak memaksakan enkripsi TLS (sslmode=require).")

        return {
            "safe": is_safe,
            "issues": issues,
            "sanitized_uri": re.sub(r"://([^:@]+):([^@]+)@", r"://\1:******@", conn_uri),
        }

    @staticmethod
    def inspect_query_safety(query_code: str) -> Tuple[bool, List[str]]:
        """
        Mendeteksi pembuatan query dinamis yang rentan terhadap SQL/NoSQL Injection.
        """
        vulnerabilities = []

        # Deteksi Python f-string pada query SQL
        if re.search(r'f["\'].*?\b(?:SELECT|INSERT|UPDATE|DELETE|DROP)\b.*?\{', query_code, re.IGNORECASE | re.DOTALL):
            vulnerabilities.append("CRITICAL: String interpolation (f-string) terdeteksi pada SQL query. Gunakan parameterized queries.")

        # Deteksi string concatenation (+) pada SQL
        if re.search(r'["\'].*?\b(?:SELECT|INSERT|UPDATE|DELETE)\b.*?["\']\s*\+', query_code, re.IGNORECASE | re.DOTALL):
            vulnerabilities.append("HIGH: String concatenation (+) terdeteksi pada pembentukan query SQL.")

        # Deteksi query dengan format %s tanpa tuple parameter
        if re.search(r'execute\(\s*["\'][^"\']*%s[^"\']*["\']\s*%', query_code, re.IGNORECASE):
            vulnerabilities.append("HIGH: Python % formatting langsung pada query string.")

        # Deteksi NoSQL operator injection ($where, $regex langsung dari parameter)
        if re.search(r'\{"\$where":\s*["\']', query_code):
            vulnerabilities.append("CRITICAL: Penggunaan ekspresi $where pada query NoSQL sangat rentan terhadap JS code injection.")

        return (len(vulnerabilities) == 0, vulnerabilities)

    @staticmethod
    def verify_role_privilege(role_grants: List[str]) -> Tuple[bool, List[str]]:
        """
        Memverifikasi bahwa akun aplikasi mematuhi Principle of Least Privilege (PoLP).
        Akun aplikasi tidak boleh memiliki wewenang DDL atau OS command execution.
        """
        forbidden_privileges = [
            "SUPERUSER", "ADMIN", "COPY PROGRAM", "FILE_PRIV",
            "XP_CMDSHELL", "ALTER SYSTEM", "DROP DATABASE"
        ]
        violations = []
        for grant in role_grants:
            upper_grant = grant.upper().strip()
            for forbidden in forbidden_privileges:
                if forbidden in upper_grant:
                    violations.append(f"VIOLATION: Hak akses '{forbidden}' terlalu berlebih untuk akun aplikasi.")

        return (len(violations) == 0, violations)
