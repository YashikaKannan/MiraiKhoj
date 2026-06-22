"""
MiraiKhoj - Behavioral Signal Scorer

Converts normalized signal features from signal_engine.py into:
- availability_score
- recruitability_score
- engagement_score
- credibility_score
- behavior_score
"""

from __future__ import annotations

from typing import Any, Dict, List


def clamp(value: float, low: float = 0.0, high: float = 100.0) -> float:
    return max(low, min(high, float(value)))


class SignalScorer:
    def score(self, features: Dict[str, Any]) -> Dict[str, Any]:
        availability_score = self._availability_score(features)
        recruitability_score = self._recruitability_score(features)
        engagement_score = self._engagement_score(features)
        credibility_score = self._credibility_score(features)

        behavior_score = (
            0.30 * availability_score
            + 0.30 * recruitability_score
            + 0.20 * engagement_score
            + 0.20 * credibility_score
        )

        return {
            "candidate_id": features.get("candidate_id"),
            "availability_score": round(clamp(availability_score), 2),
            "recruitability_score": round(clamp(recruitability_score), 2),
            "engagement_score": round(clamp(engagement_score), 2),
            "credibility_score": round(clamp(credibility_score), 2),
            "behavior_score": round(clamp(behavior_score), 2),
            "behavior_reasons": self._build_reasons(
                features,
                availability_score,
                recruitability_score,
                engagement_score,
                credibility_score,
            ),
        }

    def _availability_score(self, f: Dict[str, Any]) -> float:
        open_to_work = 100.0 if f.get("open_to_work_flag") else 35.0
        relocation = 100.0 if f.get("willing_to_relocate") else 55.0

        return (
            0.35 * open_to_work
            + 0.30 * f.get("last_active_recency_score", 0)
            + 0.25 * f.get("notice_period_score", 0)
            + 0.10 * relocation
        )

    def _recruitability_score(self, f: Dict[str, Any]) -> float:
        return (
            0.30 * f.get("recruiter_response_score", 0)
            + 0.25 * f.get("response_speed_score", 0)
            + 0.25 * f.get("interview_completion_score", 0)
            + 0.20 * f.get("offer_acceptance_score", 50)
        )

    def _engagement_score(self, f: Dict[str, Any]) -> float:
        return (
            0.25 * f.get("profile_views_score", 0)
            + 0.25 * f.get("search_appearance_score", 0)
            + 0.25 * f.get("saved_by_recruiters_score", 0)
            + 0.15 * f.get("connection_score", 0)
            + 0.10 * f.get("endorsement_score", 0)
        )

    def _credibility_score(self, f: Dict[str, Any]) -> float:
        verified_score = (
            (25 if f.get("verified_email") else 0)
            + (25 if f.get("verified_phone") else 0)
            + (20 if f.get("linkedin_connected") else 0)
        )

        return (
            0.35 * f.get("profile_completeness_normalized", 0)
            + 0.25 * verified_score
            + 0.20 * f.get("github_normalized", 0)
            + 0.20 * f.get("assessment_normalized", 0)
        )

    def _build_reasons(
        self,
        f: Dict[str, Any],
        availability: float,
        recruitability: float,
        engagement: float,
        credibility: float,
    ) -> List[str]:
        reasons = []

        if f.get("open_to_work_flag"):
            reasons.append("Open to work")
        if f.get("last_active_recency_score", 0) >= 70:
            reasons.append("Recently active")
        if recruitability >= 70:
            reasons.append("Strong recruiter responsiveness")
        if engagement >= 70:
            reasons.append("High recruiter engagement")
        if credibility >= 70:
            reasons.append("Strong profile credibility")
        if f.get("verified_email") and f.get("verified_phone"):
            reasons.append("Email and phone verified")
        if f.get("salary_range_valid") is False:
            reasons.append("Salary range anomaly detected")

        return reasons[:5]

    def batch_score(self, feature_rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return [self.score(row) for row in feature_rows]


def score_signal_features(features: Dict[str, Any]) -> Dict[str, Any]:
    return SignalScorer().score(features)