"""Behavioral intelligence engine for recruitability signals."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass(slots=True)
class BehavioralAnalysis:
    """Output of the behavioral signal engine."""

    behavioral_score: float
    availability_score: float
    recruitability_score: float
    engagement_score: float
    credibility_score: float
    logistics_score: float
    evidence: List[str] = field(default_factory=list)


class BehavioralSignalEngine:
    """Infer recruiter-friendly engagement and availability signals."""

    def analyze(self, candidate: Dict[str, object]) -> BehavioralAnalysis:
        availability_score = self._score_flag(candidate, ["open_to_work", "available", "immediately_available"], default=0.5)
        recruitability_score = self._score_numeric(candidate, ["response_rate", "recruiter_interest", "interview_completion"], default=0.5)
        engagement_score = self._score_numeric(candidate, ["github_activity", "recent_activity", "linkedin_connection"], default=0.45)
        credibility_score = self._credibility(candidate)
        logistics_score = self._logistics(candidate)

        behavioral_score = max(
            0.0,
            min(
                1.0,
                0.28 * availability_score
                + 0.30 * recruitability_score
                + 0.22 * engagement_score
                + 0.20 * credibility_score,
            ),
        )

        evidence = []
        for key in ["open_to_work", "available", "immediately_available", "response_rate", "interview_completion", "github_activity", "recent_activity", "profile_completeness"]:
            if key in candidate:
                evidence.append(f"{key}={candidate.get(key)}")

        return BehavioralAnalysis(
            behavioral_score=behavioral_score,
            availability_score=availability_score,
            recruitability_score=recruitability_score,
            engagement_score=engagement_score,
            credibility_score=credibility_score,
            logistics_score=logistics_score,
            evidence=evidence,
        )

    def _score_flag(self, candidate: Dict[str, object], keys: List[str], default: float = 0.5) -> float:
        for key in keys:
            value = candidate.get(key)
            if isinstance(value, bool):
                return 1.0 if value else 0.0
            if isinstance(value, (int, float)):
                return max(0.0, min(1.0, float(value)))
            if isinstance(value, str):
                lowered = value.lower()
                if lowered in {"yes", "true", "open", "available", "actively looking"}:
                    return 1.0
                if lowered in {"no", "false", "closed", "not available"}:
                    return 0.0
        return default

    def _score_numeric(self, candidate: Dict[str, object], keys: List[str], default: float = 0.5) -> float:
        values = []
        for key in keys:
            value = candidate.get(key)
            if isinstance(value, (int, float)):
                values.append(max(0.0, min(1.0, float(value))))
        if not values:
            return default
        return sum(values) / len(values)

    def _credibility(self, candidate: Dict[str, object]) -> float:
        completeness = candidate.get("profile_completeness")
        if isinstance(completeness, (int, float)):
            score = max(0.0, min(1.0, float(completeness)))
        else:
            filled_fields = sum(1 for key, value in candidate.items() if value)
            score = min(1.0, 0.4 + 0.05 * filled_fields)
        activity = self._score_numeric(candidate, ["github_activity", "recent_activity"], default=0.45)
        return max(0.0, min(1.0, 0.65 * score + 0.35 * activity))

    def _logistics(self, candidate: Dict[str, object]) -> float:
        score = 0.5
        location = str(candidate.get("location", "")).lower()
        if location:
            score += 0.15 if location in {"remote", "hybrid"} else 0.0
        notice_period = candidate.get("notice_period_days")
        if isinstance(notice_period, (int, float)):
            if notice_period <= 30:
                score += 0.25
            elif notice_period <= 60:
                score += 0.10
            else:
                score -= 0.05
        return max(0.0, min(1.0, score))
