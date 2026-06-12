"""Retrieval domain expertise detection."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from utils.config import RETRIEVAL_EVAL_TERMS, RETRIEVAL_TECH_TERMS


@dataclass(slots=True)
class RetrievalExpertiseAnalysis:
    """Score for retrieval/search expertise."""

    retrieval_expertise_score: float
    technology_hits: List[str] = field(default_factory=list)
    evaluation_hits: List[str] = field(default_factory=list)


class RetrievalExpertiseDetector:
    """Detect hands-on retrieval and ranking expertise from profile text."""

    def analyze(self, candidate: Dict[str, object]) -> RetrievalExpertiseAnalysis:
        text_blob = self._text_blob(candidate)
        technology_hits = [term for term in RETRIEVAL_TECH_TERMS if term in text_blob]
        evaluation_hits = [term for term in RETRIEVAL_EVAL_TERMS if term in text_blob]
        score = min(1.0, 0.14 * len(technology_hits) + 0.12 * len(evaluation_hits))
        return RetrievalExpertiseAnalysis(
            retrieval_expertise_score=score,
            technology_hits=technology_hits,
            evaluation_hits=evaluation_hits,
        )

    def _text_blob(self, candidate: Dict[str, object]) -> str:
        pieces = [str(value) for value in candidate.values() if value]
        return "\n".join(pieces).lower()
