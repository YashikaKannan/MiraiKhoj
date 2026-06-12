"""Large-scale candidate loading utilities."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterator, List

import pandas as pd

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class CandidateRecord:
    """Normalized candidate record used across the pipeline."""

    candidate_id: str
    headline: str = ""
    summary: str = ""
    current_title: str = ""
    current_company: str = ""
    career_history: str = ""
    skills: str = ""
    certifications: str = ""
    candidate_text: str = ""
    raw_record: Dict[str, Any] | None = None


def _coerce_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
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
    return str(value).strip()


def _flatten_career_history(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, list):
        formatted = []
        for item in value:
            if isinstance(item, dict):
                title = _coerce_text(item.get("title") or item.get("role") or item.get("position"))
                company = _coerce_text(item.get("company") or item.get("organization"))
                duration = _coerce_text(item.get("duration") or item.get("tenure"))
                project = _coerce_text(item.get("project") or item.get("description"))
                segment = ", ".join(part for part in [title, company, duration, project] if part)
                if segment:
                    formatted.append(segment)
            else:
                text = _coerce_text(item)
                if text:
                    formatted.append(text)
        return " | ".join(formatted)
    return _coerce_text(value)


def candidate_text_from_record(record: Dict[str, Any]) -> str:
    """Build the canonical candidate text used for embedding and retrieval."""

    sections: List[str] = []

    headline = _coerce_text(record.get("headline"))
    summary = _coerce_text(record.get("summary"))
    current_title = _coerce_text(record.get("current_title") or record.get("title"))
    current_company = _coerce_text(record.get("current_company") or record.get("company"))
    career_history = _flatten_career_history(record.get("career_history") or record.get("experience"))
    skills = _coerce_text(record.get("skills"))
    certifications = _coerce_text(record.get("certifications"))

    if headline:
        sections.append(f"Headline: {headline}")
    if summary:
        sections.append(f"Summary: {summary}")
    if current_title or current_company:
        sections.append(f"Current Role: {current_title} at {current_company}".strip())
    if career_history:
        sections.append(f"Career History: {career_history}")
    if skills:
        sections.append(f"Skills: {skills}")
    if certifications:
        sections.append(f"Certifications: {certifications}")

    return "\n".join(section for section in sections if section).strip()


def iter_candidate_records(jsonl_path: str | Path) -> Iterator[CandidateRecord]:
    """Yield normalized candidate records from a JSONL file."""

    path = Path(jsonl_path)
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            raw_line = line.strip()
            if not raw_line:
                continue
            try:
                raw_record = json.loads(raw_line)
                if not isinstance(raw_record, dict):
                    raise ValueError("JSONL row must decode to an object")
                candidate_id = _coerce_text(raw_record.get("candidate_id")) or f"row_{line_number}"
                normalized = CandidateRecord(
                    candidate_id=candidate_id,
                    headline=_coerce_text(raw_record.get("headline")),
                    summary=_coerce_text(raw_record.get("summary")),
                    current_title=_coerce_text(raw_record.get("current_title") or raw_record.get("title")),
                    current_company=_coerce_text(raw_record.get("current_company") or raw_record.get("company")),
                    career_history=_flatten_career_history(raw_record.get("career_history") or raw_record.get("experience")),
                    skills=_coerce_text(raw_record.get("skills")),
                    certifications=_coerce_text(raw_record.get("certifications")),
                    candidate_text="",
                    raw_record=raw_record,
                )
                normalized.candidate_text = candidate_text_from_record(raw_record)
                yield normalized
            except Exception as exc:
                logger.exception("Failed to parse candidate record on line %s: %s", line_number, exc)


def load_candidates(jsonl_path: str | Path) -> pd.DataFrame:
    """Load candidate records into a DataFrame."""

    records = [record.__dict__ for record in iter_candidate_records(jsonl_path)]
    if not records:
        return pd.DataFrame(
            columns=[
                "candidate_id",
                "headline",
                "summary",
                "current_title",
                "current_company",
                "career_history",
                "skills",
                "certifications",
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
