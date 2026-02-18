from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import faiss
import numpy as np
from openai import OpenAI
from pypdf import PdfReader

from app.config import Settings


@dataclass(slots=True)
class ChunkRecord:
    source_file: str
    page_number: int
    text: str


class PDFRAGService:
    def __init__(self, settings: Settings, embedding_client: OpenAI) -> None:
        self.settings = settings
        self.embedding_client = embedding_client
        self.pdf_root = settings.pdf_root
        self.vector_root = settings.vector_root
        self.index_path = self.vector_root / "faiss.index"
        self.meta_path = self.vector_root / "metadata.jsonl"
        self.manifest_path = self.vector_root / "manifest.json"
        self.records: list[ChunkRecord] = []
        self.index: faiss.Index | None = None

    def _corpus_hash(self) -> str:
        hasher = hashlib.sha256()
        files = sorted(self.pdf_root.glob("*.pdf"))
        for path in files:
            stat = path.stat()
            hasher.update(str(path.name).encode("utf-8"))
            hasher.update(str(stat.st_size).encode("utf-8"))
            hasher.update(str(int(stat.st_mtime)).encode("utf-8"))
        return hasher.hexdigest()

    def _chunk_text(self, text: str) -> list[str]:
        clean = " ".join(text.split())
        if not clean:
            return []
        size = self.settings.rag_chunk_size
        overlap = self.settings.rag_chunk_overlap
        chunks: list[str] = []
        start = 0
        while start < len(clean):
            end = min(start + size, len(clean))
            chunks.append(clean[start:end])
            if end == len(clean):
                break
            start = max(0, end - overlap)
        return chunks

    def _extract_pdf_chunks(self) -> list[ChunkRecord]:
        records: list[ChunkRecord] = []
        if not self.pdf_root.exists():
            return records
        for pdf in sorted(self.pdf_root.glob("*.pdf")):
            reader = PdfReader(str(pdf))
            for idx, page in enumerate(reader.pages):
                text = (page.extract_text() or "").strip()
                if not text:
                    continue
                for chunk in self._chunk_text(text):
                    records.append(ChunkRecord(source_file=pdf.name, page_number=idx + 1, text=chunk))
        return records

    def _embed(self, texts: list[str]) -> np.ndarray:
        vectors: list[list[float]] = []
        batch_size = 64
        for start in range(0, len(texts), batch_size):
            batch = texts[start : start + batch_size]
            response = self.embedding_client.embeddings.create(
                model=self.settings.embedding_model,
                input=batch,
            )
            vectors.extend([item.embedding for item in response.data])
        return np.array(vectors, dtype="float32")

    def _persist(self, corpus_hash: str) -> None:
        self.vector_root.mkdir(parents=True, exist_ok=True)
        if self.index is not None:
            faiss.write_index(self.index, str(self.index_path))
        with self.meta_path.open("w", encoding="utf-8") as f:
            for record in self.records:
                f.write(
                    json.dumps(
                        {
                            "source_file": record.source_file,
                            "page_number": record.page_number,
                            "text": record.text,
                        },
                        ensure_ascii=False,
                    )
                    + "\n"
                )
        self.manifest_path.write_text(
            json.dumps({"corpus_hash": corpus_hash, "count": len(self.records)}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def _load_persisted(self) -> bool:
        if not (self.index_path.exists() and self.meta_path.exists() and self.manifest_path.exists()):
            return False
        try:
            manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
            if manifest.get("corpus_hash") != self._corpus_hash():
                return False
            self.records = []
            with self.meta_path.open("r", encoding="utf-8") as f:
                for line in f:
                    item = json.loads(line)
                    self.records.append(
                        ChunkRecord(
                            source_file=item["source_file"],
                            page_number=int(item["page_number"]),
                            text=item["text"],
                        )
                    )
            self.index = faiss.read_index(str(self.index_path))
            return True
        except Exception:
            return False

    def build_index(self, force: bool = False) -> dict[str, Any]:
        corpus_hash = self._corpus_hash()
        if not force and self._load_persisted():
            return {"status": "loaded", "chunks": len(self.records)}

        self.records = self._extract_pdf_chunks()
        if not self.records:
            self.index = None
            return {"status": "no_documents", "chunks": 0}

        vectors = self._embed([rec.text for rec in self.records])
        if vectors.size == 0:
            self.index = None
            return {"status": "no_vectors", "chunks": 0}

        faiss.normalize_L2(vectors)
        dim = vectors.shape[1]
        self.index = faiss.IndexFlatIP(dim)
        self.index.add(vectors)
        self._persist(corpus_hash)
        return {"status": "built", "chunks": len(self.records)}

    def query(self, query_en: str, top_k: int | None = None) -> list[dict[str, Any]]:
        if top_k is None:
            top_k = self.settings.rag_top_k
        if self.index is None or not self.records:
            return []

        q_vec = self._embed([query_en])
        if q_vec.size == 0:
            return []
        faiss.normalize_L2(q_vec)
        scores, ids = self.index.search(q_vec, top_k)

        out: list[dict[str, Any]] = []
        for score, idx in zip(scores[0], ids[0]):
            if idx < 0 or idx >= len(self.records):
                continue
            rec = self.records[idx]
            out.append(
                {
                    "source_file": rec.source_file,
                    "page_number": rec.page_number,
                    "snippet": rec.text[:380],
                    "score": float(score),
                }
            )
        return out
