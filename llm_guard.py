"""
LLM Security & Prompt Injection Defense — Dalang-AI Guardrail Engine
Terinspirasi dari skills/llm-security (OWASP LLM Top 10 & OWASP Agentic AI / ASI 2026)
dari zhaoxuya520/reverse-skill.

Melindungi sub-agent dari:
1. Indirect Prompt Injection via file workspace (manipulasi context)
2. Direct Override & Jailbreak (DAN, Ignore instructions, delimiter escape)
3. System Prompt & Secret Leakage pada output LLM
4. Excessive Agency pada pemanggilan tools
"""

import re
from typing import Dict, List, Tuple


# Pola serangan prompt injection umum (Direct & Indirect)
INJECTION_PATTERNS = [
    r"(?i)(?:ignore|disregard|forget)\s+(?:all\s+)?(?:previous|prior|above)\s+(?:instructions|prompts|rules)",
    r"(?i)system\s+override\s*:\s*",
    r"(?i)<\|im_start\|>\s*system",
    r"(?i)\[system\s+instruction\]",
    r"(?i)you\s+are\s+now\s+(?:in\s+)?(?:dan|developer|jailbreak|unrestricted)\s+mode",
    r"(?i)from\s+now\s+on\s*,\s*you\s+must\s+(?:act|behave|respond)\s+as",
    r"(?i)(?:reveal|print|output|display)\s+(?:your\s+)?(?:system\s+prompt|initial\s+instructions|hidden\s+rules)",
    r"(?i)base64\s+decode\s+and\s+execute",
]

# Pola kebocoran data rahasia atau instruksi sistem
LEAKAGE_PATTERNS = [
    r"(?i)my\s+system\s+prompt\s+is\s*:",
    r"(?i)i\s+was\s+instructed\s+to\s*:",
    r"(?i)(?:sk-[a-zA-Z0-9]{20,})",  # OpenAI / Generic API key format
    r"(?i)(?:ghp_[a-zA-Z0-9]{36,})",  # GitHub Personal Access Token
]


class LLMGuardrail:
    """
    Guardrail pertahanan aktif untuk memvalidasi input konteks dan output model LLM.
    """

    @staticmethod
    def inspect_input(text: str) -> Tuple[bool, List[str]]:
        """
        Memeriksa apakah teks input (dokumen, prompt, atau konten file) mengandung pola injeksi.
        Mengembalikan (is_safe, list_of_detected_threats).
        """
        threats = []
        for pattern in INJECTION_PATTERNS:
            if re.search(pattern, text):
                threats.append(f"Prompt Injection Pattern Detected: {pattern}")

        return (len(threats) == 0, threats)

    @staticmethod
    def sanitize_untrusted_content(content: str, source_label: str = "workspace_file") -> str:
        """
        Membungkus konten yang tidak tepercaya (untrusted workspace file) ke dalam format
        data pasif yang dinetralisasi agar model tidak mengeksekusinya sebagai instruksi sistem.
        """
        is_safe, threats = LLMGuardrail.inspect_input(content)
        if not is_safe:
            # Netralisasi token pemisah instruksi
            sanitized = content.replace("<|im_start|>", "[NEUTRALIZED_TOKEN]")
            sanitized = sanitized.replace("<|im_end|>", "[NEUTRALIZED_TOKEN]")
            sanitized = re.sub(
                r"(?i)(ignore\s+(?:all\s+)?previous\s+instructions)",
                "[SANITIZED_INJECTION_ATTEMPT]",
                sanitized,
            )
            return (
                f"<!-- UNTRUSTED CONTENT SANITIZED BY DALANG-AI LLM-GUARD ({source_label}) -->\n"
                f"<!-- WARNING: Detected threats: {', '.join(threats)} -->\n"
                f"<untrusted_data>\n{sanitized}\n</untrusted_data>"
            )

        return content

    @staticmethod
    def inspect_output(output_text: str) -> Tuple[bool, List[str]]:
        """
        Memeriksa output model LLM sebelum diserahkan ke pengguna atau dieksekusi.
        Mendeteksi kebocoran kredensial atau prompt internal.
        """
        leaks = []
        for pattern in LEAKAGE_PATTERNS:
            if re.search(pattern, output_text):
                leaks.append(f"Data/Prompt Leakage Detected: {pattern}")

        return (len(leaks) == 0, leaks)

    @staticmethod
    def validate_tool_call_safety(tool_name: str, tool_args: Dict) -> Tuple[bool, str]:
        """
        Memeriksa excessive agency pada pemanggilan tool LLM (OWASP ASI02 / LLM06).
        Mencegah eksekusi perintah exfiltrasi berbahaya melalui tool `run_command`.
        """
        if tool_name == "run_command":
            cmd = tool_args.get("cmd", "")
            dangerous_exfil = [
                r"curl\s+-[^\n]*https?://",
                r"wget\s+https?://",
                r"nc\s+-[^\n]*\d+",
                r"/dev/tcp/",
            ]
            for dang in dangerous_exfil:
                if re.search(dang, cmd):
                    return (False, f"EXCESSIVE AGENCY BLOCKED: Percobaan exfiltrasi jaringan via command: {cmd}")

        return (True, "OK")
