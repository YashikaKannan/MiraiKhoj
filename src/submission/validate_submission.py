"""
MiraiKhoj - Submission Validator

Validates:
- required columns
- exactly top 100 or fewer during test
- candidate_id format
- rank order
- score range
- no duplicate candidates
- non-empty reasons
"""

from __future__ import annotations

import re
import pandas as pd
from typing import Dict, Any


CANDIDATE_ID_PATTERN = re.compile(r"^CAND_[0-9]{7}$")
REQUIRED_COLUMNS = ["candidate_id", "rank", "score", "reasoning"]


class SubmissionValidator:
    def validate(self, path: str, expected_rows: int = 100) -> Dict[str, Any]:
        errors = []
        warnings = []

        try:
            df = pd.read_csv(path)
        except Exception as exc:
            return {"valid": False, "errors": [f"Could not read CSV: {exc}"], "warnings": []}

        for col in REQUIRED_COLUMNS:
            if col not in df.columns:
                errors.append(f"Missing required column: {col}")

        if errors:
            return {"valid": False, "errors": errors, "warnings": warnings}

        if len(df) != expected_rows:
            warnings.append(f"Expected {expected_rows} rows, found {len(df)}")

        if df["candidate_id"].duplicated().any():
            errors.append("Duplicate candidate_id values found")

        invalid_ids = df[~df["candidate_id"].astype(str).str.match(CANDIDATE_ID_PATTERN)]
        if len(invalid_ids) > 0:
            errors.append(f"Invalid candidate_id format found in {len(invalid_ids)} rows")

        expected_ranks = list(range(1, len(df) + 1))
        actual_ranks = df["rank"].tolist()
        if actual_ranks != expected_ranks:
            errors.append("Ranks must start at 1 and increase sequentially")

        if not pd.api.types.is_numeric_dtype(df["score"]):
            errors.append("Score column must be numeric")
        else:
            if (df["score"] < 0).any() or (df["score"] > 100).any():
                errors.append("Scores must be between 0 and 100")

            if not df["score"].is_monotonic_decreasing:
                warnings.append("Scores are not sorted in descending order")

        empty_reasons = df["reasoning"].fillna("").astype(str).str.strip().eq("")
        if empty_reasons.any():
            errors.append("Reason column contains empty values")

        long_reasons = df["reasoning"].astype(str).str.split().apply(len) > 60
        if long_reasons.any():
            warnings.append("Some reasons are longer than recommended")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "row_count": len(df),
        }


if __name__ == "__main__":
    validator = SubmissionValidator()
    result = validator.validate("data/outputs/final_submission.csv")
    print(result)