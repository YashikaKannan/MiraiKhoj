"""FAISS index construction and persistence."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Sequence

import numpy as np

logger = logging.getLogger(__name__)


def _require_faiss():
    try:
        import faiss  # type: ignore

        return faiss
    except Exception as exc:
        raise RuntimeError("FAISS is required for candidate retrieval. Install faiss-cpu or faiss-gpu.") from exc


@dataclass(slots=True)
class FaissIndexBundle:
    """Container for a FAISS index and its candidate id mapping."""

    index: object
    candidate_ids: List[str] = field(default_factory=list)


@dataclass(slots=True)
class FaissIndexBuilder:
    """Build and persist an efficient candidate retrieval index."""

    use_hnsw: bool = False
    hnsw_m: int = 32

    def build(self, embeddings: np.ndarray, candidate_ids: Sequence[str]) -> FaissIndexBundle:
        """Build a FAISS index from normalized embeddings."""

        if embeddings.ndim != 2:
            raise ValueError("Embeddings must be a 2D matrix")
        if len(candidate_ids) != embeddings.shape[0]:
            raise ValueError("Candidate id count must match embedding rows")

        faiss = _require_faiss()
        embeddings = np.asarray(embeddings, dtype=np.float32)
        dimension = embeddings.shape[1]
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        embeddings = embeddings / norms

        if self.use_hnsw:
            index = faiss.IndexHNSWFlat(dimension, self.hnsw_m, faiss.METRIC_INNER_PRODUCT)
        else:
            index = faiss.IndexFlatIP(dimension)

        index.add(embeddings)
        logger.info("Built FAISS index with %s vectors", index.ntotal)
        return FaissIndexBundle(index=index, candidate_ids=list(candidate_ids))

    def save(self, bundle: FaissIndexBundle, index_path: str | Path, id_path: str | Path) -> None:
        """Persist the FAISS index and candidate id mapping."""

        faiss = _require_faiss()
        index_file = Path(index_path)
        id_file = Path(id_path)
        index_file.parent.mkdir(parents=True, exist_ok=True)
        id_file.parent.mkdir(parents=True, exist_ok=True)
        faiss.write_index(bundle.index, str(index_file))
        id_file.write_text(json.dumps(bundle.candidate_ids, ensure_ascii=False, indent=2), encoding="utf-8")
        logger.info("Saved FAISS index to %s and ids to %s", index_file, id_file)

    def load(self, index_path: str | Path, id_path: str | Path) -> FaissIndexBundle:
        """Load a persisted index bundle."""

        faiss = _require_faiss()
        index = faiss.read_index(str(index_path))
        candidate_ids = json.loads(Path(id_path).read_text(encoding="utf-8"))
        return FaissIndexBundle(index=index, candidate_ids=list(candidate_ids))
