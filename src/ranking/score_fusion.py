"""
MiraiKhoj - Score Fusion

Combines Person A scores with Person B behavioral and trap scores.

Input:
semantic_score, career_score, retrieval_score,
availability_score, recruitability_score, engagement_score,
credibility_score, trap_penalty

Output:
final_score
"""

from __future__ import annotations

from typing import Any, Dict, List


def clamp(value: float, low: float = 0.0, high: float = 100.0) -> float:
    return max(low, min(high, float(value)))


class ScoreFusion:
    def fuse(self, row: Dict[str, Any]) -> Dict[str, Any]:
        semantic_score = clamp(row.get("semantic_score", 0))
        career_score = clamp(row.get("career_score", 0))
        retrieval_score = clamp(row.get("retrieval_score", 0))

        availability_score = clamp(row.get("availability_score", 0))
        recruitability_score = clamp(row.get("recruitability_score", 0))
        engagement_score = clamp(row.get("engagement_score", 0))
        credibility_score = clamp(row.get("credibility_score", 0))

        trap_penalty = float(row.get("trap_penalty", 0) or 0)

        raw_score = (
            0.35 * semantic_score
            + 0.25 * career_score
            + 0.15 * retrieval_score
            + 0.08 * availability_score
            + 0.06 * recruitability_score
            + 0.04 * engagement_score
            + 0.04 * credibility_score
            - trap_penalty
        )

        final_score = round(clamp(raw_score), 4)

        fused = dict(row)
        fused["final_score"] = final_score
        fused["score_band"] = self._score_band(final_score)
        fused["fusion_reason"] = self._reason(fused)

        return fused

    def _score_band(self, score: float) -> str:
        if score >= 85:
            return "excellent"
        if score >= 70:
            return "strong"
        if score >= 55:
            return "moderate"
        return "weak"

    def _reason(self, row: Dict[str, Any]) -> str:
        reasons = []

        if row.get("semantic_score", 0) >= 75:
            reasons.append("high semantic JD alignment")
        if row.get("career_score", 0) >= 70:
            reasons.append("strong career fit")
        if row.get("retrieval_score", 0) >= 70:
            reasons.append("relevant retrieval/search expertise")
        if row.get("availability_score", 0) >= 70:
            reasons.append("good availability")
        if row.get("recruitability_score", 0) >= 70:
            reasons.append("strong recruiter responsiveness")
        if row.get("credibility_score", 0) >= 70:
            reasons.append("credible verified profile")
        if row.get("trap_penalty", 0) >= 20:
            reasons.append("penalized for profile inconsistency")

        if not reasons:
            reasons.append("balanced candidate fit based on available signals")

        return "; ".join(reasons[:4])

    def batch_fuse(self, rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        fused = [self.fuse(row) for row in rows]
        fused.sort(key=lambda x: x.get("final_score", 0), reverse=True)

        for idx, row in enumerate(fused, start=1):
            row["rank"] = idx

        return fused


def fuse_score(row: Dict[str, Any]) -> Dict[str, Any]:
    return ScoreFusion().fuse(row)