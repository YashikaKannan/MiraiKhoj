"""Candidate preprocessing helpers."""

from __future__ import annotations

import logging
import re
from typing import List

logger = logging.getLogger(__name__)


def normalize_whitespace(text: str) -> str:
    """Collapse excess whitespace and normalize separators."""

    return re.sub(r"\s+", " ", text or "").strip()


def split_candidate_text(candidate_text: str) -> List[str]:
    """Split the canonical candidate text into semantic chunks."""

    return [section.strip() for section in (candidate_text or "").split("\n") if section.strip()]


def clean_candidate_text(candidate_text: str) -> str:
    """Lightweight text normalization for downstream embedding."""

    return normalize_whitespace(candidate_text)
