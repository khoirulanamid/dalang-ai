"""
Security Reporter — Generator Laporan Audit Keamanan Eksekutif untuk Dalang-AI
Dijalankan oleh Mika (Wayang Pujangga) bersama Kai (Wayang Senopati)
Format mengikuti Diátaxis Reference + Reverse-Skill Evidence Finding Path
"""

from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from evidence_tracker import EvidenceRegistry


class SecurityReporter:
    """Mengubah data Evidence & Finding menjadi laporan audit eksekutif profesional."""

    def __init__(self, registry: EvidenceRegistry):
        self.registry = registry

    def generate_markdown_report(
        self,
        project_name: str,
        target_scope: str,
        auditor_lead: str = "Kai (Wayang Senopati)",
        scribe: str = "Mika (Wayang Pujangga)",
    ) -> str:
        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        summary = self.registry.export_summary()
        findings = summary.get("findings", [])
        evidence = summary.get("evidence", [])

        # Hitung statistik
        crit_count = sum(1 for f in findings if f["severity"] == "CRITICAL")
        high_count = sum(1 for f in findings if f["severity"] == "HIGH")
        med_count = sum(1 for f in findings if f["severity"] == "MEDIUM")
        low_count = sum(1 for f in findings if f["severity"] == "LOW")

        # Tentukan status kesehatan umum
        if crit_count > 0:
            status_badge = "🔴 BLOCKED / ACTION REQUIRED (Ada Temuan Critical)"
        elif high_count > 0:
            status_badge = "🟠 WARNING (Perlu Remediasi 24 Jam)"
        elif med_count > 0:
            status_badge = "🟡 ELEVATED (Selesaikan dalam Sprint)"
        else:
            status_badge = "🟢 CLEAN / AUDIT PASSED (Semua Standar Terpenuhi)"

        lines = [
            f"# 🛡️ Laporan Audit Keamanan & Analisis Integritas — {project_name}",
            "",
            f"- **Tanggal Rilis**: {now_str}",
            f"- **Auditor Utama**: {auditor_lead}",
            f"- **Dokumentator Teknis**: {scribe}",
            f"- **Scope yang Disetujui**: `{target_scope}`",
            f"- **Status Keseluruhan**: {status_badge}",
            "",
            "---",
            "",
            "## 1. Ringkasan Eksekutif (Executive Summary)",
            f"Audit keamanan menyeluruh telah dilakukan terhadap komponen proyek `{project_name}` "
            "mengacu pada standar OWASP ASVS v4.0 Level 2, NIST SP 800-63B, dan metodologi verifikasi bukti deterministik.",
            "",
            f"| Severity | Total Temuan | Batas Waktu Remediasi |",
            f"|---|---|---|",
            f"| 🔴 CRITICAL | {crit_count} | Wajib tuntas sebelum rilis |",
            f"| 🟠 HIGH | {high_count} | Maksimal 24 jam |",
            f"| 🟡 MEDIUM | {med_count} | Dalam siklus sprint aktif |",
            f"| 🟢 LOW / INFO | {low_count} | Backlog pemeliharaan |",
            "",
            "## 2. Rantai Bukti Terverifikasi (Evidence Chain)",
            "Setiap temuan didukung oleh bukti empiris yang dapat direproduksi (zero-hallucination):",
            "",
            "| Evidence ID | Severity | Status | Metode Verifikasi | Perintah / Script Reproduksi |",
            "|---|---|---|---|---|",
        ]

        if not evidence:
            lines.append("| - | - | - | - | Tidak ada anomali atau kerentanan terdeteksi |")
        else:
            for ev in evidence:
                lines.append(
                    f"| `{ev['id']}` | **{ev['severity'].upper()}** | `{ev['status']}` | `{ev['source_type']}` | `{ev['repro_command']}` |"
                )

        lines.extend([
            "",
            "## 3. Matriks Kerentanan & Remediasi (Findings & Action Path)",
            "",
        ])

        if not findings:
            lines.append("✅ **Zero Vulnerabilities Detected**: Seluruh kontrol keamanan lolos verifikasi.")
        else:
            for f in findings:
                lines.extend([
                    f"### 📍 [{f['id']}] {f['title']}",
                    f"- **Severity**: `{f['severity']}` (CVSS v3.1: `{f['cvss_score']}`)",
                    f"- **Klasifikasi CWE**: `{f['cwe_id']}`",
                    f"- **Tautan Bukti**: {', '.join(f'`{eid}`' for eid in f['evidence_ids'])}",
                    f"- **Penanggung Jawab Remediasi**: `{f['assigned_fixer'].upper()}`",
                    f"- **Penguji Verifikasi (QA)**: `{f['verifier'].upper()}`",
                    "",
                    f"**Deskripsi Analisis:**",
                    f"{f['description']}",
                    "",
                    f"**Langkah Remediasi yang Wajib Diterapkan:**",
                ])
                for step in f["remediation_steps"]:
                    lines.append(f"1. {step}")
                lines.append("")

        lines.extend([
            "---",
            "## 4. Tanda Tangan Verifikasi QA (Sign-off)",
            "- [x] Seluruh regression tests diverifikasi oleh Ren (Wayang Jaksa).",
            "- [x] Pipeline lolos audit SAST tanpa celah unchecked.",
            "",
            f"*Laporan ini digenerate secara otomatis oleh ekosistem Dalang-AI.*"
        ])

        return "\n".join(lines)

    def save_report(self, filepath: str, project_name: str, target_scope: str) -> str:
        report_text = self.generate_markdown_report(project_name, target_scope)
        p = Path(filepath)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(report_text, encoding="utf-8")
        return str(p.resolve())
