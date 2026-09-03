"""Disk-cached FAISS vector store build/load.

The legacy prototype rebuilt (re-embedded) every PDF on every process start.
Here, each domain's index is persisted under `persist_dir/<domain>/` via
`FAISS.save_local`, alongside a small manifest of the source PDFs' mtimes.
On the next startup, if the manifest still matches the source files, the
index is loaded from disk instead of being rebuilt.
"""

import json
import logging
from pathlib import Path

from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

from app.rag.loader import load_and_split

logger = logging.getLogger(__name__)

_MANIFEST_NAME = "manifest.json"


def _manifest_path(domain_dir: Path) -> Path:
    return domain_dir / _MANIFEST_NAME


def _current_manifest(pdf_paths: list[Path]) -> dict[str, float]:
    return {p.name: p.stat().st_mtime for p in pdf_paths}


def _is_cache_valid(domain_dir: Path, pdf_paths: list[Path]) -> bool:
    manifest_file = _manifest_path(domain_dir)
    index_file = domain_dir / "index.faiss"
    if not manifest_file.exists() or not index_file.exists():
        return False
    try:
        cached_manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    return cached_manifest == _current_manifest(pdf_paths)


def build_or_load_vector_store(
    domain: str,
    pdf_paths: list[Path],
    persist_dir: Path,
    embeddings: HuggingFaceEmbeddings,
    chunk_size: int,
    chunk_overlap: int,
) -> FAISS:
    domain_dir = persist_dir / domain

    if _is_cache_valid(domain_dir, pdf_paths):
        logger.info("Loading cached FAISS index for domain '%s' from %s", domain, domain_dir)
        return FAISS.load_local(
            str(domain_dir),
            embeddings,
            allow_dangerous_deserialization=True,
        )

    logger.info(
        "Building FAISS index for domain '%s' from %d source PDF(s) (no valid cache found)",
        domain,
        len(pdf_paths),
    )
    chunks = load_and_split(pdf_paths, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    vector_store = FAISS.from_documents(chunks, embeddings)

    domain_dir.mkdir(parents=True, exist_ok=True)
    vector_store.save_local(str(domain_dir))
    _manifest_path(domain_dir).write_text(
        json.dumps(_current_manifest(pdf_paths)),
        encoding="utf-8",
    )
    return vector_store
