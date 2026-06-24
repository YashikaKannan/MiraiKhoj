"""Robust JD parsing for hiring intelligence signals."""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, asdict, field
from typing import Dict, Iterable, List, Sequence

from utils.config import EVALUATION_METRICS, LOCATION_TERMS, ROLE_KEYWORDS, SKILL_LEXICON, SENIORITY_ORDER

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class ParsedJD:
    """Structured representation of a job description."""

    required_skills: List[str] = field(default_factory=list)
    preferred_skills: List[str] = field(default_factory=list)
    experience_range: str = ""
    locations: List[str] = field(default_factory=list)
    role_seniority: str = ""
    domain_keywords: List[str] = field(default_factory=list)
    evaluation_metrics: List[str] = field(default_factory=list)
    target_roles: List[str] = field(default_factory=list)

    raw_text: str = ""

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


class JDParser:
    """Heuristic JD understanding engine with deterministic structured output."""

    REQUIRED_PATTERNS: Sequence[str] = (
        r"required[:\-]?",
        r"must have[:\-]?",
        r"mandatory[:\-]?",
        r"what you bring",
        r"minimum qualifications",
    )
    PREFERRED_PATTERNS: Sequence[str] = (
        r"preferred[:\-]?",
        r"nice to have[:\-]?",
        r"bonus[:\-]?",
        r"good to have[:\-]?",
    )

    def parse(self, job_description: str) -> ParsedJD:
        """Parse raw JD text into a structured JSON-compatible object."""

        cleaned = self._normalize(job_description)
        required_skills = self._extract_skills(cleaned, required=True)
        preferred_skills = self._extract_skills(cleaned, required=False)
        experience_range = self._extract_experience_range(cleaned)
        locations = self._extract_locations(cleaned)
        role_seniority = self._extract_seniority(cleaned)
        domain_keywords = self._extract_domain_keywords(cleaned)
        evaluation_metrics = self._extract_metrics(cleaned)
        target_roles = self._extract_target_roles(cleaned)

        return ParsedJD(
            required_skills=required_skills,
            preferred_skills=preferred_skills,
            experience_range=experience_range,
            locations=locations,
            role_seniority=role_seniority,
            domain_keywords=domain_keywords,
            evaluation_metrics=evaluation_metrics,
            target_roles=target_roles,
            raw_text=cleaned,
        )

    def parse_json(self, job_description: str) -> str:
        """Return the parsed JD as a JSON string."""

        return json.dumps(self.parse(job_description).to_dict(), ensure_ascii=False, indent=2)

    def _normalize(self, text: str) -> str:
        return re.sub(r"\s+", " ", text or "").strip()

    def _extract_skills(self, text: str, required: bool) -> List[str]:
        lowered = text.lower()
        skills: List[str] = []
        for skill in SKILL_LEXICON:
            if skill in lowered:
                skills.append(skill)

        bullet_matches = re.findall(r"(?:[-*•]\s+)([^\n]+)", text)
        for bullet in bullet_matches:
            bullet_lower = bullet.lower()
            for skill in SKILL_LEXICON:
                if skill in bullet_lower:
                    skills.append(skill)

        section_text = self._extract_section(text, self.REQUIRED_PATTERNS if required else self.PREFERRED_PATTERNS)
        for skill in SKILL_LEXICON:
            if skill in section_text.lower():
                skills.append(skill)

        return self._unique(skills)

    def _extract_section(self, text: str, patterns: Sequence[str]) -> str:
        lowered = text.lower()
        for pattern in patterns:
            match = re.search(pattern, lowered)
            if match:
                return text[match.start() : match.start() + 700]
        return text[:700]

    def _extract_experience_range(self, text: str) -> str:
        patterns = [
            r"(\d{1,2})\s*\+?\s*(?:years?|yrs?)\s*(?:of)?\s*experience",
            r"(\d{1,2})\s*[-to]{1,3}\s*(\d{1,2})\s*(?:years?|yrs?)",
            r"(?:minimum|at least|around)\s*(\d{1,2})\s*(?:years?|yrs?)",
        ]
        for pattern in patterns:
            match = re.search(pattern, text, flags=re.IGNORECASE)
            if match:
                return match.group(0)
        return ""

    def _extract_locations(self, text: str) -> List[str]:
        lowered = text.lower()
        locations = [term for term in LOCATION_TERMS if term in lowered]
        city_matches = re.findall(r"(?:based in|location|locations|office in)[:\-]?\s*([A-Za-z ,/]+)", text, flags=re.IGNORECASE)
        for match in city_matches:
            locations.extend([part.strip().lower() for part in re.split(r"[,/]", match) if part.strip()])
        return self._unique(locations)

    def _extract_seniority(self, text: str) -> str:
        lowered = text.lower()
        for seniority in reversed(SENIORITY_ORDER):
            if seniority in lowered:
                return seniority
        return ""

    def _extract_domain_keywords(self, text: str) -> List[str]:
        lowered = text.lower()
        keywords = []
        for term in [
            "ai",
            "machine learning",
            "recommendation",
            "search",
            "retrieval",
            "ranking",
            "information retrieval",
            "semantic",
            "nlp",
            "vector search",
            "ads",
            "marketplace",
            "commerce",
            "personalization",
        ]:
            if term in lowered:
                keywords.append(term)

        capitalized_phrases = re.findall(r"\b([A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+){0,3})\b", text)
        keywords.extend(phrase.lower() for phrase in capitalized_phrases if len(phrase) > 2)
        return self._unique(keywords)

    def _extract_metrics(self, text: str) -> List[str]:
        lowered = text.lower()
        return self._unique([metric for metric in EVALUATION_METRICS if metric in lowered])
    
    def _extract_target_roles(self, text: str) -> List[str]:
        """
        Extract the primary job roles from the JD.
        """

        lowered = text.lower()

        ROLE_MAP = {
            "ai engineer": [
                "ai engineer",
                "machine learning engineer",
                "ml engineer",
                "search engineer",
                "recommendation engineer",
                "nlp engineer",
                "information retrieval engineer",
                "applied scientist",
            ],

            "backend engineer": [
                "backend engineer",
                "software engineer",
                "python developer",
                "platform engineer",
                "backend developer",
            ],

            "frontend engineer": [
                "frontend engineer",
                "frontend developer",
                "ui engineer",
                "react developer",
            ],

            "data engineer": [
                "data engineer",
                "etl engineer",
                "analytics engineer",
                "big data engineer",
            ],

            "data scientist": [
                "data scientist",
                "machine learning scientist",
                "research scientist",
            ],
        }

        for key, roles in ROLE_MAP.items():
            if key in lowered:
                return roles

        return []

    def _unique(self, values: Iterable[str]) -> List[str]:
        seen = set()
        ordered: List[str] = []
        for value in values:
            normalized = value.strip().lower()
            if normalized and normalized not in seen:
                seen.add(normalized)
                ordered.append(normalized)
        return ordered
