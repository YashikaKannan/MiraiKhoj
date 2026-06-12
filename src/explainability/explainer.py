"""Human-readable explanation generation for candidate rankings."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from ranking.ai_ranker import RankedCandidate


@dataclass(slots=True)
class CandidateExplainer:
    """Turn score breakdowns into recruiter-friendly reasons."""

    def explain(self, ranked_candidate: RankedCandidate) -> str:
        """Create a concise explanation for a ranked candidate."""

        reasons: List[str] = []

        if ranked_candidate.semantic_score >= 0.75:
            reasons.append("Strong semantic alignment with the JD.")
        elif ranked_candidate.semantic_score >= 0.55:
            reasons.append("Relevant semantic overlap with the role requirements.")

        if ranked_candidate.career_score >= 0.70:
            reasons.append("Career history shows strong role fit and progression.")

        if ranked_candidate.retrieval_expertise_score >= 0.55:
            reasons.append("Hands-on retrieval, ranking, or search expertise detected.")

        if ranked_candidate.behavioral_score >= 0.55:
            reasons.append("Positive recruitability and engagement signals.")

        if ranked_candidate.credibility_score >= 0.60:
            reasons.append("Profile credibility and completeness look solid.")

        if ranked_candidate.logistics_score >= 0.55:
            reasons.append("Good logistics fit for availability or location constraints.")

        if ranked_candidate.trap_penalty > 0.0:
            reasons.append("Suspicious profile signals were detected and penalized.")

        if not reasons:
            reasons.append("Candidate is a moderate match with limited supporting evidence.")

        return " ".join(reasons)
