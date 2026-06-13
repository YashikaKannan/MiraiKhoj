"""Schema-aware candidate loading utilities for the Redrob dataset."""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, Iterator, List, Mapping, Sequence

import pandas as pd

from data.preprocess import build_candidate_text, normalize_whitespace

logger = logging.getLogger(__name__)


REQUIRED_TOP_LEVEL_FIELDS: Sequence[str] = (
    "candidate_id",
    "profile",
    "career_history",
    "education",
    "skills",
    "redrob_signals",
)

REQUIRED_PROFILE_FIELDS: Sequence[str] = (
    "anonymized_name",
    "headline",
    "summary",
    "location",
    "country",
    "years_of_experience",
    "current_title",
    "current_company",
    "current_company_size",
    "current_industry",
)

REQUIRED_CAREER_FIELDS: Sequence[str] = (
    "company",
    "title",
    "start_date",
    "end_date",
    "duration_months",
    "is_current",
    "industry",
    "company_size",
    "description",
)

REQUIRED_EDUCATION_FIELDS: Sequence[str] = (
    "institution",
    "degree",
    "field_of_study",
    "start_year",
    "end_year",
)

REQUIRED_SKILL_FIELDS: Sequence[str] = (
    "name",
    "proficiency",
    "endorsements",
)

REQUIRED_SIGNAL_FIELDS: Sequence[str] = (
    "profile_completeness_score",
    "signup_date",
    "last_active_date",
    "open_to_work_flag",
    "profile_views_received_30d",
    "applications_submitted_30d",
    "recruiter_response_rate",
    "avg_response_time_hours",
    "skill_assessment_scores",
    "connection_count",
    "endorsements_received",
    "notice_period_days",
    "expected_salary_range_inr_lpa",
    "preferred_work_mode",
    "willing_to_relocate",
    "github_activity_score",
    "search_appearance_30d",
    "saved_by_recruiters_30d",
    "interview_completion_rate",
    "offer_acceptance_rate",
    "verified_email",
    "verified_phone",
    "linkedin_connected",
)

CURRENT_COMPANY_SIZE_VALUES = {
    "1-10",
    "11-50",
    "51-200",
    "201-500",
    "501-1000",
    "1001-5000",
    "5001-10000",
    "10001+",
}

EDUCATION_TIER_VALUES = {"tier_1", "tier_2", "tier_3", "tier_4", "unknown"}
SKILL_PROFICIENCY_VALUES = {"beginner", "intermediate", "advanced", "expert"}
LANGUAGE_PROFICIENCY_VALUES = {"basic", "conversational", "professional", "native"}
PREFERRED_WORK_MODE_VALUES = {"remote", "hybrid", "onsite", "flexible"}

_CANDIDATE_ID_PATTERN = re.compile(r"^CAND_[0-9]{7}$")


@dataclass(slots=True)
class CandidateRecord:
    """Normalized candidate record used across the pipeline."""

    candidate_id: str
    profile: Dict[str, Any]
    career_history: List[Dict[str, Any]]
    education: List[Dict[str, Any]]
    skills: List[Dict[str, Any]]
    redrob_signals: Dict[str, Any]
    certifications: List[Dict[str, Any]]
    languages: List[Dict[str, Any]]
    candidate_text: str = ""
    raw_record: Dict[str, Any] | None = None


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
    if isinstance(value, dict):
        parts = []
        for key, item in value.items():
            text = _coerce_text(item)
            if text:
                parts.append(f"{key}: {text}")
        return "; ".join(parts)
    return normalize_whitespace(str(value))


def _ensure_mapping(value: Any) -> Dict[str, Any]:
    if isinstance(value, Mapping):
        return dict(value)
    raise TypeError("Expected an object for a nested candidate field")


def _ensure_list(value: Any, field_name: str) -> List[Dict[str, Any]]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise TypeError(f"Expected '{field_name}' to be a list")
    items: List[Dict[str, Any]] = []
    for item in value:
        items.append(_ensure_mapping(item))
    return items


def _validate_required_fields(record: Mapping[str, Any], required_fields: Sequence[str], context: str) -> List[str]:
    missing = [field for field in required_fields if field not in record]
    if missing:
        return [f"{context} missing required fields: {', '.join(missing)}"]
    return []


def validate_candidate_schema(record: Mapping[str, Any]) -> List[str]:
    """Return schema validation errors for a raw candidate record."""

    errors: List[str] = []
    errors.extend(_validate_required_fields(record, REQUIRED_TOP_LEVEL_FIELDS, "top-level record"))

    candidate_id = _coerce_text(record.get("candidate_id"))
    if candidate_id and not _CANDIDATE_ID_PATTERN.fullmatch(candidate_id):
        errors.append("candidate_id must match ^CAND_[0-9]{7}$")

    profile_value = record.get("profile")
    if isinstance(profile_value, Mapping):
        errors.extend(_validate_required_fields(profile_value, REQUIRED_PROFILE_FIELDS, "profile"))
        current_company_size = _coerce_text(profile_value.get("current_company_size"))
        if current_company_size and current_company_size not in CURRENT_COMPANY_SIZE_VALUES:
            errors.append("profile.current_company_size has an invalid enum value")
    elif "profile" in record:
        errors.append("profile must be an object")

    for field_name, required_fields in (
        ("career_history", REQUIRED_CAREER_FIELDS),
        ("education", REQUIRED_EDUCATION_FIELDS),
        ("skills", REQUIRED_SKILL_FIELDS),
    ):
        field_value = record.get(field_name)
        if isinstance(field_value, list):
            if field_name == "career_history" and not field_value:
                errors.append("career_history must contain at least 1 item")
            if field_name == "career_history" and len(field_value) > 10:
                errors.append("career_history must contain at most 10 items")
            if field_name == "education" and len(field_value) > 5:
                errors.append("education must contain at most 5 items")
            for index, entry in enumerate(field_value):
                if not isinstance(entry, Mapping):
                    errors.append(f"{field_name}[{index}] must be an object")
                    continue
                errors.extend(_validate_required_fields(entry, required_fields, f"{field_name}[{index}]"))
                if field_name == "career_history":
                    company_size = _coerce_text(entry.get("company_size"))
                    if company_size and company_size not in CURRENT_COMPANY_SIZE_VALUES:
                        errors.append(f"career_history[{index}].company_size has an invalid enum value")
                elif field_name == "education":
                    tier = _coerce_text(entry.get("tier"))
                    if tier and tier not in EDUCATION_TIER_VALUES:
                        errors.append(f"education[{index}].tier has an invalid enum value")
                elif field_name == "skills":
                    proficiency = _coerce_text(entry.get("proficiency"))
                    if proficiency and proficiency not in SKILL_PROFICIENCY_VALUES:
                        errors.append(f"skills[{index}].proficiency has an invalid enum value")
        elif field_name in record:
            errors.append(f"{field_name} must be an array")

    for field_name, required_fields in (("certifications", ("name", "issuer", "year")), ("languages", ("language", "proficiency"))):
        field_value = record.get(field_name)
        if field_value is None:
            continue
        if isinstance(field_value, list):
            for index, entry in enumerate(field_value):
                if not isinstance(entry, Mapping):
                    errors.append(f"{field_name}[{index}] must be an object")
                    continue
                errors.extend(_validate_required_fields(entry, required_fields, f"{field_name}[{index}]"))
                if field_name == "languages":
                    proficiency = _coerce_text(entry.get("proficiency"))
                    if proficiency and proficiency not in LANGUAGE_PROFICIENCY_VALUES:
                        errors.append(f"languages[{index}].proficiency has an invalid enum value")
        else:
            errors.append(f"{field_name} must be an array when provided")

    signals_value = record.get("redrob_signals")
    if isinstance(signals_value, Mapping):
        errors.extend(_validate_required_fields(signals_value, REQUIRED_SIGNAL_FIELDS, "redrob_signals"))
        preferred_work_mode = _coerce_text(signals_value.get("preferred_work_mode"))
        if preferred_work_mode and preferred_work_mode not in PREFERRED_WORK_MODE_VALUES:
            errors.append("redrob_signals.preferred_work_mode has an invalid enum value")
    elif "redrob_signals" in record:
        errors.append("redrob_signals must be an object")

    return errors


def build_candidate_text(record: Mapping[str, Any]) -> str:
    """Build the canonical candidate text using only actual dataset fields."""

    profile = _ensure_mapping(record.get("profile", {}))
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

    career_history = _ensure_list(record.get("career_history"), "career_history")
    if career_history:
        formatted_history: List[str] = []
        for entry in career_history:
            parts = [
                _coerce_text(entry.get("title")),
                _coerce_text(entry.get("company")),
                _coerce_text(entry.get("industry")),
                _coerce_text(entry.get("description")),
            ]
            parts = [part for part in parts if part]
            if parts:
                formatted_history.append("; ".join(parts))
        if formatted_history:
            sections.append("Career History: " + " | ".join(formatted_history))

    education = _ensure_list(record.get("education"), "education")
    if education:
        formatted_education: List[str] = []
        for entry in education:
            parts = [
                _coerce_text(entry.get("institution")),
                _coerce_text(entry.get("degree")),
                _coerce_text(entry.get("field_of_study")),
                _coerce_text(entry.get("grade")),
                _coerce_text(entry.get("tier")),
            ]
            parts = [part for part in parts if part]
            if parts:
                formatted_education.append("; ".join(parts))
        if formatted_education:
            sections.append("Education: " + " | ".join(formatted_education))

    skills = _ensure_list(record.get("skills"), "skills")
    if skills:
        formatted_skills: List[str] = []
        for entry in skills:
            parts = [
                _coerce_text(entry.get("name")),
                _coerce_text(entry.get("proficiency")),
                _coerce_text(entry.get("endorsements")),
                _coerce_text(entry.get("duration_months")),
            ]
            parts = [part for part in parts if part]
            if parts:
                formatted_skills.append("; ".join(parts))
        if formatted_skills:
            sections.append("Skills: " + " | ".join(formatted_skills))

    certifications_value = record.get("certifications")
    if isinstance(certifications_value, list) and certifications_value:
        formatted_certs: List[str] = []
        for entry in _ensure_list(certifications_value, "certifications"):
            parts = [
                _coerce_text(entry.get("name")),
                _coerce_text(entry.get("issuer")),
                _coerce_text(entry.get("year")),
            ]
            parts = [part for part in parts if part]
            if parts:
                formatted_certs.append("; ".join(parts))
        if formatted_certs:
            sections.append("Certifications: " + " | ".join(formatted_certs))

    languages_value = record.get("languages")
    if isinstance(languages_value, list) and languages_value:
        formatted_languages: List[str] = []
        for entry in _ensure_list(languages_value, "languages"):
            parts = [
                _coerce_text(entry.get("language")),
                _coerce_text(entry.get("proficiency")),
            ]
            parts = [part for part in parts if part]
            if parts:
                formatted_languages.append("; ".join(parts))
        if formatted_languages:
            sections.append("Languages: " + " | ".join(formatted_languages))

    return "\n".join(section for section in sections if section).strip()


def iter_candidate_records(source_path: str | Path) -> Iterator[CandidateRecord]:
    """Yield normalized candidate records from JSON, JSONL, or a JSON array file."""

    path = Path(source_path)
    raw_text = path.read_text(encoding="utf-8").strip()
    if not raw_text:
        return

    if raw_text.startswith("["):
        try:
            iterable: Iterable[Any] = json.loads(raw_text)
        except json.JSONDecodeError:
            logger.exception("Failed to parse JSON array from %s", path)
            return
    else:
        def _jsonl_iter() -> Iterator[Any]:
            with path.open("r", encoding="utf-8") as jsonl_handle:
                for line_number, line in enumerate(jsonl_handle, start=1):
                    stripped = line.strip()
                    if not stripped:
                        continue
                    try:
                        yield json.loads(stripped)
                    except json.JSONDecodeError:
                        logger.exception("Skipping malformed JSONL record at line %s", line_number)

        iterable = _jsonl_iter()

    for index, raw_record in enumerate(iterable, start=1):
        if not isinstance(raw_record, Mapping):
            logger.warning("Skipping non-object record at position %s", index)
            continue
        try:
            errors = validate_candidate_schema(raw_record)
            if errors:
                raise ValueError("; ".join(errors))

            candidate_id = _coerce_text(raw_record.get("candidate_id"))
            normalized = CandidateRecord(
                candidate_id=candidate_id,
                profile=_ensure_mapping(raw_record["profile"]),
                career_history=_ensure_list(raw_record.get("career_history"), "career_history"),
                education=_ensure_list(raw_record.get("education"), "education"),
                skills=_ensure_list(raw_record.get("skills"), "skills"),
                redrob_signals=_ensure_mapping(raw_record["redrob_signals"]),
                certifications=_ensure_list(raw_record.get("certifications"), "certifications"),
                languages=_ensure_list(raw_record.get("languages"), "languages"),
                candidate_text="",
                raw_record=dict(raw_record),
            )
            normalized.candidate_text = build_candidate_text(raw_record)
            yield normalized
        except Exception:
            logger.exception("Skipping malformed candidate record at position %s", index)


def load_candidates(jsonl_path: str | Path) -> pd.DataFrame:
    """Load candidate records into a DataFrame.

    The loader preserves nested structures and materializes a schema-aligned row
    for every valid candidate record.
    """

    records: List[Dict[str, Any]] = []
    for index, record in enumerate(iter_candidate_records(jsonl_path), start=1):
        records.append(
            {
                "candidate_id": record.candidate_id,
                "profile": record.profile,
                "career_history": record.career_history,
                "education": record.education,
                "skills": record.skills,
                "certifications": record.certifications,
                "languages": record.languages,
                "redrob_signals": record.redrob_signals,
                "candidate_text": record.candidate_text,
                "raw_record": record.raw_record,
            }
        )
        if index % 10000 == 0:
            logger.info("Loaded %s candidate records from %s", index, jsonl_path)

    if not records:
        return pd.DataFrame(
            columns=[
                "candidate_id",
                "profile",
                "career_history",
                "education",
                "skills",
                "certifications",
                "languages",
                "redrob_signals",
                "candidate_text",
                "raw_record",
            ]
        )

    return pd.DataFrame.from_records(records)


def process_candidates_jsonl(jsonl_path: str | Path, output_path: str | Path) -> pd.DataFrame:
    """Process candidates and write a parquet artifact for downstream stages."""

    df = load_candidates(jsonl_path)
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(output, index=False)
    logger.info("Wrote processed candidates to %s", output)
    return df
