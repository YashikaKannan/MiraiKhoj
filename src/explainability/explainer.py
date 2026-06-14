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

        candidate = ranked_candidate.candidate_payload

        years = candidate.get("years_of_experience")
        title = candidate.get("current_title")
        company = candidate.get("current_company")
        if years:
            reasons.append(
                f"{years} years of relevant experience."
            )

        if title and company:
            reasons.append(
                f"Currently working as {title} at {company}."
            )
        if ranked_candidate.matched_skills:
            reasons.append(
                f"Matched {len(ranked_candidate.matched_skills)} JD skills including "
                f"{', '.join(ranked_candidate.matched_skills[:5])}."
            )


        retrieval_tools = []

        for tool in [
            "faiss",
            "elasticsearch",
            "opensearch",
            "qdrant",
            "weaviate",
            "milvus",
            "pinecone",
            "vector search",
        ]:
            if tool in ranked_candidate.evidence:
                retrieval_tools.append(tool.upper())

        if retrieval_tools:
            reasons.append(
                f"Hands-on experience with {', '.join(retrieval_tools[:4])}."
            )

        if ranked_candidate.semantic_score >= 0.75:
            reasons.append("High semantic match with the job description.")
        elif ranked_candidate.semantic_score >= 0.55:
            reasons.append("Relevant semantic overlap with the role requirements.")

        if ranked_candidate.career_score >= 0.70:
            reasons.append("Strong career alignment with the target role.")

        if ranked_candidate.retrieval_expertise_score >= 0.55:
            reasons.append("Strong retrieval and ranking expertise.")

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
