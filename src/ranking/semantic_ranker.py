"""Semantic ranking utilities."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(slots=True)
class SemanticRanker:
    """Compute semantic relevance between a JD and a candidate profile."""

    def score(self, jd_embedding: np.ndarray, candidate_embedding: np.ndarray) -> float:
        """Return cosine similarity in the range [0, 1]."""

        jd = np.asarray(jd_embedding, dtype=np.float32).reshape(-1)
        candidate = np.asarray(candidate_embedding, dtype=np.float32).reshape(-1)
        if jd.size == 0 or candidate.size == 0:
            return 0.0
        numerator = float(np.dot(jd, candidate))
        denominator = float(np.linalg.norm(jd) * np.linalg.norm(candidate))
        if denominator == 0.0:
            return 0.0
        cosine = numerator / denominator
        return max(0.0, min(1.0, (cosine + 1.0) / 2.0))
    def skill_match_score(self, required_skills: list[str], candidate_text: str,) -> float:

        candidate_text = candidate_text.lower()

        HIGH_WEIGHT = {
            "embedding",
            "embeddings",
            "retrieval",
            "ranking",
            "faiss",
            "pinecone",
            "qdrant",
            "milvus",
            "weaviate",
            "vector search",
            "vector database",
            "recommendation",
            "information retrieval",
            "learning to rank",
            "ndcg",
            "mrr",
            "map",
            "llm",
        }

        score = 0.0
        max_score = 0.0

        for skill in required_skills:

            weight = 3.0 if skill in HIGH_WEIGHT else 1.5

            max_score += weight

            if skill.lower() in candidate_text:
                score += weight

        if max_score == 0:
            return 0.0

        return score / max_score