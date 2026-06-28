"""Human-readable explanation generation for candidate rankings."""

from __future__ import annotations

from dataclasses import dataclass

from ranking.ai_ranker import RankedCandidate


@dataclass(slots=True)
class CandidateExplainer:
    """Generate recruiter-friendly candidate explanations."""

    def explain(self, ranked_candidate: RankedCandidate) -> str:
        
        candidate = ranked_candidate.candidate_payload

        if ("llm_reason" in candidate and candidate["llm_reason"] not in ["LLM evaluation failed.", "LLM unavailable. Used deterministic AI ranking."]):
            reason = candidate.get("llm_reason", "")

            strengths = candidate.get("strengths", [])
            risks = candidate.get("risks", [])

            parts = [reason]

            if strengths:
                parts.append("Strengths: " + ", ".join(strengths))

            if risks:
                parts.append("Risks: " + ", ".join(risks))

            return " ".join(parts)

        reasons = []

        years = float(candidate.get("years_of_experience", 0))
        title = candidate.get("current_title") or ""
        title_lower = title.lower()
        company = candidate.get("current_company")

        # ----------------------------------------------------
        # Experience
        # ----------------------------------------------------

        if years > 0:

            if company:
                reasons.append(
                    f"{years:.1f} years of experience as {title} at {company}."
                )
            else:
                reasons.append(
                    f"{years:.1f} years of experience as {title}."
                )

        # ----------------------------------------------------
        # Skills
        # ----------------------------------------------------

        if ranked_candidate.matched_skills:

            skills = ", ".join(ranked_candidate.matched_skills[:4])

            # reasons.append(
            #     f"Matched {len(ranked_candidate.matched_skills)} key JD skills including {skills}."
            # )
            if len(ranked_candidate.matched_skills) >= 8:
                reasons.append(
                    f"Matches {len(ranked_candidate.matched_skills)} of the required technical capabilities, including {skills}."
                )
            elif len(ranked_candidate.matched_skills) >= 5:
                reasons.append(
                    f"Covers most of the required engineering stack, including {skills}."
                )
            else:
                reasons.append(
                    f"Relevant technical experience includes {skills}."
                )

        # ----------------------------------------------------
        # Retrieval technologies
        # ----------------------------------------------------

        evidence = " ".join(ranked_candidate.evidence).lower()

        tools = []

        for tool in [
            "faiss",
            "elasticsearch",
            "opensearch",
            "qdrant",
            "weaviate",
            "pinecone",
            "milvus",
            "vector search",
        ]:

            if tool in evidence:
                tools.append(tool.upper())

        if tools:

            reasons.append(
                f"Hands-on experience with {', '.join(tools[:3])}."
            )

        # ----------------------------------------------------
        # Role-specific reasoning
        # ----------------------------------------------------

        if "search engineer" in title_lower:

            reasons.append(
                "Built production search and retrieval systems closely aligned with the role's ranking responsibilities."
            )

        elif "recommendation" in title_lower:

            reasons.append(
                "Recommendation system experience indicates strong relevance and ranking expertise."
            )

        elif "nlp" in title_lower:

            reasons.append(
                "Strong NLP background aligns well with semantic search and embedding-based retrieval."
            )

        elif "machine learning" in title_lower or "ml engineer" in title_lower:

            reasons.append(
                "Production machine learning experience supports deployment of intelligent retrieval systems."
            )

        elif "ai engineer" in title_lower:

            reasons.append(
                "Hands-on AI engineering experience matches the production-focused expectations of the role."
            )

        # ----------------------------------------------------
        # Career
        # ----------------------------------------------------

        if ranked_candidate.career_score >= 0.70:

            reasons.append(
                "Career progression closely matches the senior AI engineering profile."
            )

        elif ranked_candidate.career_score >= 0.55:

            reasons.append(
                "Career history demonstrates consistent growth in relevant engineering roles."
            )

        # ----------------------------------------------------
        # Semantic
        # ----------------------------------------------------

        if ranked_candidate.semantic_score >= 0.85:

            reasons.append(
                "Excellent semantic alignment with the job description."
            )

        elif ranked_candidate.semantic_score >= 0.70:

            reasons.append(
                "Strong semantic similarity to the required responsibilities."
            )

        # ----------------------------------------------------
        # Retrieval expertise
        # ----------------------------------------------------

        if ranked_candidate.retrieval_expertise_score >= 0.90:

            reasons.append(
                "Demonstrates extensive production experience with retrieval and vector search technologies."
            )

        elif ranked_candidate.retrieval_expertise_score >= 0.70:

            reasons.append(
                "Good practical exposure to modern retrieval infrastructure."
            )

        # ----------------------------------------------------
        # Behaviour
        # ----------------------------------------------------

        if ranked_candidate.behavioral_score >= 0.70:

            reasons.append(
                "Behavioral signals indicate strong hiring readiness."
            )

        elif ranked_candidate.behavioral_score >= 0.50:

            reasons.append(
                "Behavioral profile is consistent with an active candidate."
            )

        else:

            reasons.append(
                "Behavioral signals should be validated during interview."
            )

        # ----------------------------------------------------
        # Credibility
        # ----------------------------------------------------

        if ranked_candidate.credibility_score >= 0.70:

            reasons.append(
                "Profile demonstrates strong credibility with consistent career information."
            )

        elif ranked_candidate.credibility_score >= 0.55:

            reasons.append(
                "Profile information is sufficiently complete for evaluation."
            )

        # ----------------------------------------------------
        # Logistics
        # ----------------------------------------------------

        if ranked_candidate.logistics_score >= 0.60:

            reasons.append(
                "Availability and logistics are favorable for hiring."
            )

        # ----------------------------------------------------
        # Trap detector
        # ----------------------------------------------------

        if ranked_candidate.trap_penalty >= 0.05:

            reasons.append(
                "Minor profile inconsistencies slightly reduced the final ranking."
            )

        # ----------------------------------------------------
        # Fallback
        # ----------------------------------------------------

        if len(reasons) < 3:

            reasons.append(
                "Overall profile demonstrates a solid match for the role."
            )
        #  Remove duplicate sentences while preserving order
        reasons = list(dict.fromkeys(reasons))
        return " ".join(reasons)