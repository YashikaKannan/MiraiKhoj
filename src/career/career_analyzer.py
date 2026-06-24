"""Career intelligence scoring for actual experience fit."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from utils.config import COMPANY_QUALITY_TERMS, CONSULTING_TERMS, ROLE_KEYWORDS, RETRIEVAL_TECH_TERMS, SENIORITY_ORDER


@dataclass(slots=True)
class CareerAnalysis:
    """Output of the career intelligence engine."""

    career_score: float
    role_relevance: float
    retrieval_experience: float
    career_growth: float
    company_quality: float
    consulting_penalty: float
    evidence: List[str] = field(default_factory=list)


class CareerAnalyzer:
    """Score candidates based on titles, progression, companies, and projects."""

    def analyze(self, candidate: Dict[str, object], target_roles: List[str],) -> CareerAnalysis:
        """Return a normalized career-fit score with supporting evidence."""

        text_blob = self._build_text_blob(candidate)
        # target_roles = candidate.get("target_roles", [])

        role_relevance, role_evidence = self._role_relevance(text_blob, target_roles)
        retrieval_experience, retrieval_evidence = self._retrieval_experience(text_blob)
        career_growth = self._career_growth(text_blob)
        company_quality, company_evidence, consulting_penalty = self._company_quality(text_blob)

        base_score = (
            0.40 * role_relevance
            + 0.25 * retrieval_experience
            + 0.20 * career_growth
            + 0.15 * company_quality
        )
        career_score = max(0.0, min(1.0, base_score - consulting_penalty))
        evidence = role_evidence + retrieval_evidence + company_evidence
        return CareerAnalysis(
            career_score=career_score,
            role_relevance=role_relevance,
            retrieval_experience=retrieval_experience,
            career_growth=career_growth,
            company_quality=company_quality,
            consulting_penalty=consulting_penalty,
            evidence=evidence,
        )

    def _build_text_blob(self, candidate: Dict[str, object]) -> str:
        parts: List[str] = []
        for key in ["headline", "summary", "current_title", "current_company", "career_history", "skills", "certifications", "raw_record"]:
            value = candidate.get(key)
            if value:
                parts.append(str(value))
        return "\n".join(parts).lower()

    def _role_relevance(self, text_blob: str, target_roles: List[str],) -> tuple[float, List[str]]:

        evidence: List[str] = []

        BAD_ROLES = {
            "marketing manager",
            "operations manager",
            "customer support",
            "hr manager",
            "accountant",
            "civil engineer",
            "sales manager",
            "content writer",
        }

        # Strong penalty for clearly irrelevant careers
        for role in BAD_ROLES:
            if role in text_blob:
                evidence.append(f"irrelevant_role:{role}")
                return 0.05, evidence

        # JD-specific role matching
        for role in target_roles:
            if role in text_blob:
                evidence.append(f"matched_target_role:{role}")
                return 1.0, evidence

        # Partial matches
        partial_roles = [
            "software engineer",
            "backend engineer",
            "machine learning engineer",
            "ai engineer",
            "data engineer",
            "python developer",
        ]

        for role in partial_roles:
            if role in text_blob:
                evidence.append(f"related_role:{role}")
                return 0.75, evidence

        return 0.25, evidence

    def _retrieval_experience(self, text_blob: str) -> tuple[float, List[str]]:
        evidence = [f"retrieval: {term}" for term in RETRIEVAL_TECH_TERMS if term in text_blob]
        metric_hits = [term for term in ["ndcg", "mrr", "map", "learning to rank", "ab testing"] if term in text_blob]
        score = min(1.0, 0.14 * len(evidence) + 0.10 * len(metric_hits))
        return score, evidence + [f"metrics: {term}" for term in metric_hits]

    def _career_growth(self, text_blob: str) -> float:
        stages = [stage for stage in SENIORITY_ORDER if stage in text_blob]
        if not stages:
            return 0.35
        progression = 0
        for earlier, later in zip(stages, stages[1:]):
            if SENIORITY_ORDER.index(later) >= SENIORITY_ORDER.index(earlier):
                progression += 1
        return min(1.0, 0.35 + 0.15 * len(stages) + 0.10 * progression)

    def _company_quality(self, text_blob: str) -> tuple[float, List[str], float]:
        evidence: List[str] = []
        scores: List[float] = []
        for term, score in COMPANY_QUALITY_TERMS.items():
            if term in text_blob:
                scores.append(score)
                evidence.append(f"company: {term}")

        consulting_hits = [term for term in CONSULTING_TERMS if term in text_blob]
        consulting_penalty = 0.0
        if consulting_hits and not scores:
            consulting_penalty = 0.18
        elif consulting_hits:
            consulting_penalty = 0.08

        if not scores:
            return 0.45, evidence, consulting_penalty

        return min(1.0, sum(scores) / len(scores)), evidence, consulting_penalty
