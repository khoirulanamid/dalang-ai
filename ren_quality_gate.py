"""
Ren Quality Gate — Wayang Jaksa (Mandatory QA Testing Gate)
Memeriksa integritas setiap artefak/output SEBELUM diizinkan masuk ke Gudang Bagong.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional
import ast
import json
import re


@dataclass
class QAVerdict:
    artifact_path: str
    category: str
    tester_agent: str
    status: str  # "PASSED", "REJECTED"
    score: float  # 0.0 - 100.0
    issues: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


class RenQualityGate:
    """
    Quality Assurance Gatekeeper resmi Dalang-AI Studio.
    Semua artefak yang diproduksi oleh Wayang (Kresna, Zaki, Lulu, dsb.)
    wajib mendapatkan verifikasi PASSED dari Ren sebelum diserahkan ke Bagong (Vault).
    """

    PASS_THRESHOLD = 80.0

    def inspect_artifact(
        self,
        file_path: str,
        category: str,
        producer_agent: str = "unknown",
    ) -> QAVerdict:
        path = Path(file_path)
        issues = []
        recommendations = []
        score = 100.0

        # 1. Verifikasi Eksistensi & Ukuran Dasar
        if not path.exists():
            return QAVerdict(
                artifact_path=file_path,
                category=category,
                tester_agent="ren",
                status="REJECTED",
                score=0.0,
                issues=[f"File tidak ditemukan di path: {file_path}"],
            )

        file_size = path.stat().st_size
        if file_size == 0:
            return QAVerdict(
                artifact_path=file_path,
                category=category,
                tester_agent="ren",
                status="REJECTED",
                score=0.0,
                issues=["File kosong (0 bytes). Output cacat."],
            )

        # 2. Audit Khusus Per Kategori
        category = category.lower()

        if category == "html_film":
            # Standar Film Kresna: Canvas 2D + Self-contained HTML + Audio API
            try:
                content = path.read_text(encoding="utf-8")
            except Exception as e:
                return QAVerdict(
                    artifact_path=file_path,
                    category=category,
                    tester_agent="ren",
                    status="REJECTED",
                    score=0.0,
                    issues=[f"Gagal membaca teks file: {str(e)}"],
                )

            # 1. Wajib ada <!DOCTYPE html>
            if "<!doctype html>" not in content.lower():
                issues.append("Tidak ditemukan deklarasi <!DOCTYPE html> standar.")
                score -= 20.0

            # 2. Wajib ada elemen <canvas>
            if "<canvas" not in content.lower():
                issues.append("Kritis: Tidak ditemukan tag <canvas> untuk render animasi.")
                score -= 40.0

            # 3. Wajib ada blok <script>
            if "<script" not in content.lower() or "</script>" not in content.lower():
                issues.append("Kritis: Skrip interaktif JavaScript tidak ditemukan.")
                score -= 40.0

            # 4. Wajib ada Web Audio API atau audio logic
            if "AudioContext" not in content and "webkitAudioContext" not in content:
                issues.append("Peringatan: Belum terdeteksi Web Audio API sintetis.")
                score -= 10.0

            # 5. Wajib file TIDAK terpotong — harus ditutup </html>
            stripped = content.strip()
            if not stripped.endswith("</html>") and not stripped.endswith("</html>\n"):
                issues.append("KRITIS: File HTML terpotong (truncated) — tidak ditemukan </html> penutup. Film tidak akan jalan di browser.")
                score -= 60.0

        elif category == "code":
            if path.suffix == ".py":
                try:
                    code_content = path.read_text(encoding="utf-8")
                    ast.parse(code_content)
                except SyntaxError as e:
                    issues.append(f"Python Syntax Error pada baris {e.lineno}: {e.msg}")
                    score -= 60.0
                except Exception as e:
                    issues.append(f"Error parsing kode: {str(e)}")
                    score -= 50.0

            elif path.suffix in [".js", ".jsx", ".ts", ".tsx"]:
                code_content = path.read_text(encoding="utf-8")
                # Deteksi unclosed braces sederhana
                if code_content.count("{") != code_content.count("}"):
                    issues.append("Ketidakseimbangan tanda kurung kurawal '{' dan '}'.")
                    score -= 30.0

            elif path.suffix == ".json":
                try:
                    json.loads(path.read_text(encoding="utf-8"))
                except json.JSONDecodeError as e:
                    issues.append(f"JSON Corrupted: {str(e)}")
                    score -= 60.0

        elif category == "report":
            if path.suffix == ".json":
                try:
                    json.loads(path.read_text(encoding="utf-8"))
                except json.JSONDecodeError as e:
                    issues.append(f"JSON Corrupted: {str(e)}")
                    score -= 60.0

        # Evaluasi Status Akhir
        status = "PASSED" if score >= self.PASS_THRESHOLD else "REJECTED"

        if status == "REJECTED":
            recommendations.append("Perbaiki issue kritis sebelum mengajukan deposit ulang ke Bagong.")

        return QAVerdict(
            artifact_path=str(path),
            category=category,
            tester_agent="ren",
            status=status,
            score=max(0.0, score),
            issues=issues,
            recommendations=recommendations,
        )


# Singleton
ren_quality_gate = RenQualityGate()
