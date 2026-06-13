"""
MiraiKhoj - Honeypot / Trap Detector

Detects:
- keyword stuffing
- fake seniority
- career mismatch
- skill spam
- title-description mismatch
- salary anomaly
- behavioral contradiction

Output:
trap_penalty from 0 to 40
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Set


AI_KEYWORDS: Set[str] = {
    "rag", "llm", "gpt", "openai", "langchain", "pinecone", "faiss", "milvus",
    "qdrant", "vector", "embedding", "embeddings", "retrieval", "ranking",
    "recommendation", "recommender", "bm25", "semantic search", "nlp",
    "transformer", "bert", "fine-tuning", "lora", "mlops", "kubeflow",
}

NON_TECH_TITLES: Set[str] = {
    "marketing manager", "operations manager", "accountant", "civil engineer",
    "mechanical engineer", "customer support", "hr manager", "content writer",
    "sales", "project manager", "business analyst",
}

SENIOR_TOKENS: Set[str] = {
    "senior", "lead", "principal", "staff", "architect", "head", "director"
}

TECH_ROLE_TOKENS: Set[str] = {
    "engineer", "developer", "data scientist", "ml engineer", "ai engineer",
    "backend", "software", "search", "ranking", "recommendation"
}


def clamp(value: float, low: float = 0.0, high: float = 40.0) -> float:
    return max(low, min(high, float(value)))


def normalize_text(value: Any) -> str:
    return str(value or "").lower().strip()


class TrapDetector:
    def detect(self, candidate: Dict[str, Any]) -> Dict[str, Any]:
        profile = candidate.get("profile", {})
        skills = candidate.get("skills", []) or []
        career = candidate.get("career_history", []) or []
        signals = candidate.get("redrob_signals", {}) or {}

        trap_flags: List[str] = []
        penalty = 0.0

        keyword_penalty, keyword_flags = self._keyword_stuffing(profile, skills, career)
        penalty += keyword_penalty
        trap_flags.extend(keyword_flags)

        seniority_penalty, seniority_flags = self._fake_seniority(profile)
        penalty += seniority_penalty
        trap_flags.extend(seniority_flags)

        mismatch_penalty, mismatch_flags = self._career_mismatch(profile, skills, career)
        penalty += mismatch_penalty
        trap_flags.extend(mismatch_flags)

        spam_penalty, spam_flags = self._skill_spam(skills)
        penalty += spam_penalty
        trap_flags.extend(spam_flags)

        data_penalty, data_flags = self._data_anomalies(profile, signals)
        penalty += data_penalty
        trap_flags.extend(data_flags)

        final_penalty = round(clamp(penalty), 2)

        return {
            "candidate_id": candidate.get("candidate_id"),
            "trap_penalty": final_penalty,
            "trap_flags": trap_flags,
            "is_high_risk_trap": final_penalty >= 25,
            "is_possible_honeypot": final_penalty >= 32,
        }

    def _keyword_stuffing(self, profile, skills, career):
        flags = []
        penalty = 0.0

        skill_names = [normalize_text(s.get("name")) for s in skills]
        ai_skill_count = sum(1 for skill in skill_names if any(k in skill for k in AI_KEYWORDS))

        career_text = " ".join(
            normalize_text(item.get("title", "")) + " " + normalize_text(item.get("description", ""))
            for item in career
        )
        career_ai_hits = sum(1 for k in AI_KEYWORDS if k in career_text)

        title = normalize_text(profile.get("current_title"))

        if ai_skill_count >= 8 and career_ai_hits <= 2:
            penalty += 12
            flags.append("High AI keyword count without matching career evidence")

        if title in NON_TECH_TITLES and ai_skill_count >= 5:
            penalty += 10
            flags.append("Non-technical title with unusually technical AI skill stack")

        return penalty, flags

    def _fake_seniority(self, profile):
        flags = []
        penalty = 0.0

        title = normalize_text(profile.get("current_title"))
        years = float(profile.get("years_of_experience") or 0)

        has_senior_title = any(token in title for token in SENIOR_TOKENS)

        if has_senior_title and years < 3:
            penalty += 12
            flags.append("Senior title with low total experience")

        if "lead" in title and years < 4:
            penalty += 10
            flags.append("Lead title appears inflated for experience level")

        return penalty, flags

    def _career_mismatch(self, profile, skills, career):
        flags = []
        penalty = 0.0

        current_title = normalize_text(profile.get("current_title"))
        summary = normalize_text(profile.get("summary"))

        descriptions = [normalize_text(c.get("description")) for c in career]
        titles = [normalize_text(c.get("title")) for c in career]
        all_career_text = " ".join(titles + descriptions)

        if current_title in NON_TECH_TITLES:
            tech_skill_count = sum(
                1
                for s in skills
                if any(k in normalize_text(s.get("name")) for k in AI_KEYWORDS)
            )

            if tech_skill_count >= 4:
                penalty += 8
                flags.append("Career title does not support claimed AI/search skills")

        if "marketing manager" in summary and not any("marketing" in t for t in titles):
            penalty += 5
            flags.append("Summary background conflicts with career titles")

        if current_title and current_title not in all_career_text:
            penalty += 4
            flags.append("Current title weakly supported by career descriptions")

        role_groups = {
            "marketing": ["marketing", "seo", "content", "brand"],
            "engineering": ["engineer", "developer", "backend", "software", "data"],
            "finance": ["accountant", "accounting", "finance", "tax"],
            "support": ["support", "customer", "ticket"],
            "mechanical": ["mechanical", "cad", "solidworks", "manufacturing"],
        }

        groups_hit = 0
        for terms in role_groups.values():
            if any(term in all_career_text for term in terms):
                groups_hit += 1

        if groups_hit >= 4:
            penalty += 8
            flags.append("Career history jumps across unrelated domains")

        return penalty, flags

    def _skill_spam(self, skills):
        flags = []
        penalty = 0.0

        if len(skills) >= 18:
            penalty += 5
            flags.append("Unusually large skill list")

        advanced_count = sum(1 for s in skills if normalize_text(s.get("proficiency")) in {"advanced", "expert"})
        low_duration_advanced = sum(
            1
            for s in skills
            if normalize_text(s.get("proficiency")) in {"advanced", "expert"}
            and int(s.get("duration_months") or 0) < 12
        )

        if advanced_count >= 8:
            penalty += 5
            flags.append("Too many advanced/expert skills")

        if low_duration_advanced >= 3:
            penalty += 6
            flags.append("Advanced skills claimed with short duration")

        return penalty, flags

    def _data_anomalies(self, profile, signals):
        flags = []
        penalty = 0.0

        salary = signals.get("expected_salary_range_inr_lpa", {}) or {}
        salary_min = salary.get("min", -1)
        salary_max = salary.get("max", -1)

        try:
            if float(salary_min) > float(salary_max):
                penalty += 10
                flags.append("Invalid salary range: minimum greater than maximum")
        except Exception:
            penalty += 4
            flags.append("Invalid salary values")

        if not signals.get("open_to_work_flag") and int(signals.get("applications_submitted_30d", 0)) >= 8:
            penalty += 6
            flags.append("Not open to work but high application activity")

        if float(signals.get("profile_completeness_score", 0)) < 35:
            penalty += 5
            flags.append("Very low profile completeness")

        if int(signals.get("notice_period_days", 0)) >= 150:
            penalty += 4
            flags.append("Very long notice period")

        return penalty, flags

    def batch_detect(self, candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return [self.detect(candidate) for candidate in candidates]


def detect_traps(candidate: Dict[str, Any]) -> Dict[str, Any]:
    return TrapDetector().detect(candidate)