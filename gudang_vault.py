"""
Gudang / Vault Manager — Modul Bagong (Wayang Juru Simpan / Release & Asset Custodian)
Menampung, mengindeks, dan mendistribusikan semua artefak output Dalang-AI
(HTML, Video, Desain, Dokumen, Kode, Asset Microstock).
Output bisa diakses via API/Dashboard dan dikirim langsung ke Telegram.
"""

import os
import json
import time
import shutil
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from ren_quality_gate import ren_quality_gate

VAULT_DIR = Path("/root/storage/projects/dalang-ai/vault")
VAULT_INDEX_FILE = VAULT_DIR / "vault_index.json"


@dataclass
class VaultItem:
    id: str
    filename: str
    category: str  # "html_film", "video", "design", "code", "document", "microstock", "report"
    producer_agent: str
    title: str
    description: str
    file_path: str
    relative_url: str
    size_bytes: int
    created_at: str
    metadata: dict


class QARejectionError(Exception):
    """Raised saat Ren menolak artefak karena tidak memenuhi standar mutu."""
    pass


class VaultManager:
    """Manajer Gudang / Asset Custodian Dalang-AI."""

    def __init__(self):
        VAULT_DIR.mkdir(parents=True, exist_ok=True)
        if not VAULT_INDEX_FILE.exists():
            self._save_index([])

    def _load_index(self) -> List[dict]:
        if not VAULT_INDEX_FILE.exists():
            return []
        try:
            with open(VAULT_INDEX_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    def _save_index(self, items: List[dict]):
        with open(VAULT_INDEX_FILE, "w", encoding="utf-8") as f:
            json.dump(items, f, indent=2, ensure_ascii=False)

    def deposit_artifact(
        self,
        source_path: str,
        category: str,
        producer_agent: str,
        title: str,
        description: str = "",
        metadata: Optional[dict] = None,
    ) -> VaultItem:
        """
        Menyimpan file hasil kerja ke dalam Vault resmi, mengindeksnya,
        dan menyalinnya ke public frontend agar bisa diakses browser.
        """
        src = Path(source_path)
        if not src.exists():
            raise FileNotFoundError(f"File sumber tidak ditemukan: {source_path}")

        # ── 🛡️ MANDATORY QA INSPECTION BY REN (WAYANG JAKSA) ───────────────
        verdict = ren_quality_gate.inspect_artifact(
            file_path=str(src),
            category=category,
            producer_agent=producer_agent,
        )
        if verdict.status == "REJECTED":
            issues_str = "; ".join(verdict.issues)
            raise QARejectionError(
                f"[Ren QA Gate REJECTED] Artefak {src.name} ditolak Ren (Skor: {verdict.score}/100). "
                f"Alasan: {issues_str}"
            )

        # Tentukan subfolder kategori
        cat_dir = VAULT_DIR / category
        cat_dir.mkdir(parents=True, exist_ok=True)

        # Buat nama unik di gudang
        timestamp_str = time.strftime("%Y%m%d_%H%M%S")
        dest_filename = f"{timestamp_str}_{src.name}"
        dest_path = cat_dir / dest_filename

        shutil.copy2(src, dest_path)

        # Salin juga ke public frontend agar bisa di-preview di browser
        public_dir = Path("/root/storage/projects/dalang-ai/frontend/public/vault") / category
        public_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, public_dir / dest_filename)

        item_id = f"VLT-{abs(hash(dest_filename)) % 100000:05d}"
        item = VaultItem(
            id=item_id,
            filename=dest_filename,
            category=category,
            producer_agent=producer_agent,
            title=title,
            description=description,
            file_path=str(dest_path),
            relative_url=f"/vault/{category}/{dest_filename}",
            size_bytes=os.path.getsize(dest_path),
            created_at=time.strftime("%Y-%m-%d %H:%M:%S"),
            metadata=metadata or {},
        )

        index = self._load_index()
        index.insert(0, asdict(item))
        self._save_index(index)
        return item

    def list_items(self, category: Optional[str] = None, agent: Optional[str] = None) -> List[dict]:
        items = self._load_index()
        if category:
            items = [i for i in items if i.get("category") == category]
        if agent:
            items = [i for i in items if i.get("producer_agent") == agent]
        return items

    def get_item(self, item_id: str) -> Optional[dict]:
        items = self._load_index()
        return next((i for i in items if i.get("id") == item_id), None)


# Singleton
vault_manager = VaultManager()
