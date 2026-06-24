"""Final ranking, honeypot detection, and score fusion."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Sequence
from honeypot.trap_detector import TrapDetector
from utils.config import RankingWeights


@dataclass(slots=True)
class CandidateScoreBundle:
    """All scoring inputs for a single candidate."""

    candidate_id: str
    semantic_score: float
    career_score: float
    retrieval_expertise_score: float
    behavioral_score: float
    credibility_score: float
    logistics_score: float
    trap_penalty: float
    evidence: List[str] = field(default_factory=list)
    candidate_payload: Dict[str, object] = field(default_factory=dict)
    matched_skills: List[str] = field(default_factory=list)


@dataclass(slots=True)
class RankedCandidate:
    """Final ranked candidate with score breakdown."""

    candidate_id: str
    final_score: float
    semantic_score: float
    career_score: float
    retrieval_expertise_score: float
    behavioral_score: float
    credibility_score: float
    logistics_score: float
    trap_penalty: float
    evidence: List[str] = field(default_factory=list)
    candidate_payload: Dict[str, object] = field(default_factory=dict)
    matched_skills: List[str] = field(default_factory=list)


# class HoneypotDetector:
#     """Detect suspicious, keyword-stuffed, or inconsistent profiles."""

#     KEYWORD_STUFFING_PATTERNS = ["faiss faiss", "search search", "machine learning machine learning", "ranking ranking"]
#     FAKE_SENIOR_PATTERNS = ["principal engineer", "staff engineer", "director", "vp", "head of"]
#     CONSULTING_ONLY_PATTERNS = ["consulting", "services", "outsourcing", "staffing"]

#     def detect(self, candidate: Dict[str, object]) -> float:
#         text_blob = self._text_blob(candidate)
#         penalty = 0.0

#         stuffing_hits = sum(1 for pattern in self.KEYWORD_STUFFING_PATTERNS if pattern in text_blob)
#         if stuffing_hits:
#             penalty += min(0.25, 0.08 * stuffing_hits)

#         senior_hits = sum(1 for pattern in self.FAKE_SENIOR_PATTERNS if pattern in text_blob)
#         years = self._extract_years(text_blob)
#         if senior_hits and years is not None and years < 4:
#             penalty += 0.20

#         consulting_hits = sum(1 for pattern in self.CONSULTING_ONLY_PATTERNS if pattern in text_blob)
#         if consulting_hits and not any(term in text_blob for term in ["product", "startup", "platform", "saas", "search", "marketplace"]):
#             penalty += 0.18

#         if self._looks_inconsistent(text_blob):
#             penalty += 0.12

#         return max(0.0, min(1.0, penalty))

#     def _text_blob(self, candidate: Dict[str, object]) -> str:
#         pieces = [str(value) for value in candidate.values() if value]
#         return " ".join(pieces).lower()

#     def _extract_years(self, text_blob: str) -> float | None:
#         import re

#         match = re.search(r"(\d{1,2})\s*\+?\s*(?:years?|yrs?)", text_blob)
#         if match:
#             return float(match.group(1))
#         return None

#     def _looks_inconsistent(self, text_blob: str) -> bool:
#         return any(flag in text_blob for flag in ["intern at many companies", "worked at 20+ companies", "founded 10 startups"])


@dataclass(slots=True)
class FinalRanker:
    """Fuse module scores into a final ranking score."""

    weights: RankingWeights = field(default_factory=RankingWeights)

    def score(self, bundle: CandidateScoreBundle) -> float:
        """Calculate the final score for a candidate."""

        final_score = (
            self.weights.semantic * bundle.semantic_score
            + self.weights.career * bundle.career_score
            + self.weights.retrieval_expertise * bundle.retrieval_expertise_score
            + self.weights.behavioral * bundle.behavioral_score
            + self.weights.credibility * bundle.credibility_score
            + self.weights.logistics * bundle.logistics_score
            - bundle.trap_penalty
        )

        title = str(
            bundle.candidate_payload.get("current_title", "")
        ).lower()

        # Roles that strongly match this JD
        strong_roles = [
            "search engineer",
            "ai engineer",
            "machine learning engineer",
            "ml engineer",
            "nlp engineer",
            "information retrieval engineer",
            "recommendation engineer",
            "applied scientist",
        ]

        # Roles explicitly discouraged by the JD
        irrelevant_roles = [
            "marketing",
            "operations manager",
            "hr manager",
            "customer support",
            "mechanical engineer",
            "civil engineer",
            "sales",
            "accountant",
        ]

        # Reward good AI/Search careers
        if any(role in title for role in strong_roles):
            final_score += 0.08

        # Penalize clearly unrelated careers
        if any(role in title for role in irrelevant_roles):
            final_score -= 0.20

        return max(0.0, min(1.0, final_score))

    def rank(self, bundles: Sequence[CandidateScoreBundle]) -> List[RankedCandidate]:
        """Return candidates sorted by final score descending."""

        ranked: List[RankedCandidate] = []
        for bundle in bundles:
            final_score = self.score(bundle)
            ranked.append(
                RankedCandidate(
                    candidate_id=bundle.candidate_id,
                    final_score=final_score,
                    semantic_score=bundle.semantic_score,
                    career_score=bundle.career_score,
                    retrieval_expertise_score=bundle.retrieval_expertise_score,
                    behavioral_score=bundle.behavioral_score,
                    credibility_score=bundle.credibility_score,
                    logistics_score=bundle.logistics_score,
                    trap_penalty=bundle.trap_penalty,
                    evidence=bundle.evidence,
                    matched_skills=bundle.matched_skills,
                    candidate_payload=bundle.candidate_payload,
                )
            )
        ranked.sort(key=lambda item: item.final_score, reverse=True)
        return ranked
