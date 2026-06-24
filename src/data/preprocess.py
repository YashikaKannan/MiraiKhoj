"""Candidate preprocessing helpers for the Redrob schema."""

from __future__ import annotations

import logging
import re
from typing import Any, Dict, List, Mapping, Sequence

logger = logging.getLogger(__name__)


def normalize_whitespace(text: str) -> str:
    """Collapse excess whitespace and normalize separators."""

    return re.sub(r"\s+", " ", text or "").strip()


def _coerce_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return normalize_whitespace(value)
    if isinstance(value, (int, float, bool)):
        return str(value)
    if isinstance(value, list):
        parts = [_coerce_text(item) for item in value]
        return ", ".join(part for part in parts if part)
    if isinstance(value, Mapping):
        parts: List[str] = []
        for key, item in value.items():
            text = _coerce_text(item)
            if text:
                parts.append(f"{key}: {text}")
        return "; ".join(parts)
    return normalize_whitespace(str(value))


def split_candidate_text(candidate_text: str) -> List[str]:
    """Split canonical candidate text into semantic chunks."""

    return [section.strip() for section in (candidate_text or "").split("\n") if section.strip()]


def _format_list(entries: Sequence[Mapping[str, Any]], keys: Sequence[str], label: str) -> str:
    formatted_entries: List[str] = []
    for entry in entries:
        parts = [_coerce_text(entry.get(key)) for key in keys]
        parts = [part for part in parts if part]
        if parts:
            formatted_entries.append("; ".join(parts))
    return f"{label}: " + " | ".join(formatted_entries) if formatted_entries else ""


def build_candidate_text(record: Mapping[str, Any]) -> str:
    """Build a canonical candidate text using only actual dataset fields."""

    profile = record.get("profile") if isinstance(record.get("profile"), Mapping) else {}
    sections: List[str] = []

    headline = _coerce_text(profile.get("headline"))
    summary = _coerce_text(profile.get("summary"))
    current_title = _coerce_text(profile.get("current_title"))
    current_company = _coerce_text(profile.get("current_company"))
    current_industry = _coerce_text(profile.get("current_industry"))
    location = _coerce_text(profile.get("location"))
    country = _coerce_text(profile.get("country"))
    years_of_experience = _coerce_text(profile.get("years_of_experience"))

    if headline:
        sections.append(f"Headline: {headline}")
    if summary:
        sections.append(f"Summary: {summary}")
    if current_title or current_company:
        sections.append(f"Current Role: {current_title} at {current_company}".strip())
    if current_industry:
        sections.append(f"Current Industry: {current_industry}")
    if location or country:
        location_text = ", ".join(part for part in [location, country] if part)
        if location_text:
            sections.append(f"Location: {location_text}")
    if years_of_experience:
        sections.append(f"Years of Experience: {years_of_experience}")

    career_history = record.get("career_history")
    if isinstance(career_history, list) and career_history:
        sections.append(
            _format_list(
                career_history,  # type: ignore[arg-type]
                ("title", "company", "industry", "description"),
                "Career History",
            )
        )

    education = record.get("education")
    if isinstance(education, list) and education:
        sections.append(
            _format_list(
                education,  # type: ignore[arg-type]
                ("institution", "degree", "field_of_study", "grade", "tier"),
                "Education",
            )
        )

    skills = record.get("skills")
    if isinstance(skills, list) and skills:
        sections.append(
            _format_list(
                skills,  # type: ignore[arg-type]
                ("name", "proficiency", "endorsements", "duration_months"),
                "Skills",
            )
        )

    certifications = record.get("certifications")
    if isinstance(certifications, list) and certifications:
        sections.append(
            _format_list(
                certifications,  # type: ignore[arg-type]
                ("name", "issuer", "year"),
                "Certifications",
            )
        )

    languages = record.get("languages")
    if isinstance(languages, list) and languages:
        sections.append(
            _format_list(
                languages,  # type: ignore[arg-type]
                ("language", "proficiency"),
                "Languages",
            )
        )

    return "\n".join(section for section in sections if section).strip()


def build_processed_candidate_row(record: Mapping[str, Any]) -> Dict[str, Any]:
    """Derive the processed parquet row from a raw candidate record."""

    profile = record.get("profile") if isinstance(record.get("profile"), Mapping) else {}
    skills = record.get("skills") if isinstance(record.get("skills"), list) else []
    certifications = record.get("certifications") if isinstance(record.get("certifications"), list) else []
    languages = record.get("languages") if isinstance(record.get("languages"), list) else []

    years_of_experience = profile.get("years_of_experience")
    if not isinstance(years_of_experience, (int, float)):
        years_of_experience = None
    skill_names = []

    for skill in skills:
        name = _coerce_text(skill.get("name"))
        if name:
            skill_names.append(name)

    return {
        "candidate_id": _coerce_text(record.get("candidate_id")),
        "candidate_text": clean_candidate_text(build_candidate_text(record)),
        "years_of_experience": years_of_experience,
        "current_title": _coerce_text(profile.get("current_title")),
        "current_company": _coerce_text(profile.get("current_company")),
        "skill_count": len(skills),
        "certification_count": len(certifications),
        "language_count": len(languages),
        "candidate_skills": ", ".join(skill_names),
    }


def clean_candidate_text(candidate_text: str) -> str:
    """Lightweight text normalization for downstream embedding."""

    return normalize_whitespace(candidate_text)
