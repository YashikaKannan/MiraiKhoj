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
    def skill_match_score(self, jd_skills: list[str], candidate_text: str,) -> float:
        matched = 0

        for skill in jd_skills:
            if skill.lower() in candidate_text.lower():
                matched += 1

        return matched / max(len(jd_skills), 1)
