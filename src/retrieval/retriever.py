"""FAISS retrieval wrapper for JD-to-candidate search."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import List

import numpy as np

from retrieval.faiss_builder import FaissIndexBuilder, FaissIndexBundle

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class RetrievalHit:
    """Single retrieval result from the FAISS index."""

    candidate_id: str
    score: float
    rank: int


@dataclass(slots=True)
class FaissRetriever:
    """Retrieve nearest candidates for a JD embedding."""

    index_bundle: FaissIndexBundle

    @classmethod
    def from_files(cls, index_path: str | Path, id_path: str | Path) -> "FaissRetriever":
        builder = FaissIndexBuilder()
        return cls(index_bundle=builder.load(index_path=index_path, id_path=id_path))

    def search(self, query_embedding: np.ndarray, top_k: int = 500) -> List[RetrievalHit]:
        """Search the candidate index with a query vector."""

        if query_embedding.ndim == 1:
            query = query_embedding.reshape(1, -1).astype(np.float32)
        else:
            query = query_embedding.astype(np.float32)

        norms = np.linalg.norm(query, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        query = query / norms

        scores, indices = self.index_bundle.index.search(query, top_k)
        hits: List[RetrievalHit] = []
        candidate_ids = self.index_bundle.candidate_ids
        for rank, (score, index) in enumerate(zip(scores[0], indices[0]), start=1):
            if index < 0 or index >= len(candidate_ids):
                continue
            hits.append(RetrievalHit(candidate_id=candidate_ids[index], score=float(score), rank=rank))
        return hits
