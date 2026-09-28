"""
Scope Guard — Keamanan Batas Wilayah Eksekusi (Scope Contract) untuk Dalang-AI
Terinspirasi dari ops/scope-contract.md di zhaoxuya520/reverse-skill

Memastikan sub-agent hanya beroperasi di dalam workspace yang diotorisasi,
mencegah manipulasi file berbahaya di luar folder proyek, dan mencegah akses network liar.
"""

from pathlib import Path
from typing import List, Optional
from urllib.parse import urlparse


class ScopeViolationError(Exception):
    """Dilemparkan jika sub-agent mencoba melanggar batas otorisasi proyek."""
    pass


def validate_path_in_scope(target_path: str, allowed_root: str) -> Path:
    """
    Memvalidasi bahwa path target berada di dalam batas direktori proyek/workspace yang diizinkan.
    Mencegah path traversal (misal: ../../../etc/passwd atau /root/.ssh).
    """
    root = Path(allowed_root).resolve()
    target = Path(target_path)
    
    if not target.is_absolute():
        resolved_target = (root / target).resolve()
    else:
        resolved_target = target.resolve()

    try:
        resolved_target.relative_to(root)
    except ValueError:
        raise ScopeViolationError(
            f"AKSES DITOLAK: Path '{target_path}' berada di luar scope workspace '{allowed_root}'. "
            f"Sub-agent hanya boleh memodifikasi file di dalam workspace yang ditentukan."
        )

    return resolved_target


def validate_network_target(url: str, allowed_hosts: Optional[List[str]] = None) -> bool:
    """
    Memvalidasi URL target agar tidak menghubungi endpoint sembarangan
    tanpa izin eksplisit (Authorized Target Only).
    """
    parsed = urlparse(url)
    hostname = parsed.hostname or ""
    
    # Default local allowed
    default_allowed = ["localhost", "127.0.0.1", "0.0.0.0"]
    all_allowed = set(default_allowed + [h.lower() for h in (allowed_hosts or [])])

    if hostname.lower() in all_allowed:
        return True

    # Jika target eksplisit diberikan
    for allowed in all_allowed:
        if hostname.lower().endswith("." + allowed) or hostname.lower() == allowed:
            return True

    raise ScopeViolationError(
        f"AKSES NETWORK DITOLAK: Host '{hostname}' tidak berada dalam allowed_hosts ({all_allowed}). "
        f"Otorisasi scope diperlukan sebelum mengirim data keluar."
    )
