"""
MiraiKhoj - Submission Generator

Generates final_submission.csv in required format:
candidate_id,rank,score,reasoning
"""

from __future__ import annotations

import pandas as pd
from pathlib import Path
from typing import Optional

REQUIRED_COLUMNS = ["candidate_id", "rank", "score", "reasoning"]


class SubmissionGenerator:
    def __init__(self, top_k: int = 100) -> None:
        self.top_k = top_k

    def generate(
        self,
        ranked_input_path: str,
        output_path: str = "data/outputs/final_submission.csv",
        score_column: str = "final_score",
        reason_column: str = "reasoning",
    ) -> pd.DataFrame:
        df = pd.read_csv(ranked_input_path)

        if "candidate_id" not in df.columns:
            raise ValueError("Input must contain candidate_id")

        if score_column not in df.columns:
            raise ValueError(f"Input must contain {score_column}")

        if reason_column not in df.columns:
            if "candidate_reason" in df.columns:
                reason_column = "candidate_reason"
            elif "fusion_reason" in df.columns:
                reason_column = "fusion_reason"
            else:
                df["reasoning"] = "Candidate ranked based on AI relevance, behavioral quality, and profile trust signals."
                reason_column = "reasoning"

        df = df.sort_values(score_column, ascending=False).head(self.top_k).copy()
        df["rank"] = range(1, len(df) + 1)
        df["score"] = df[score_column].round(4)
        df["reasoning"] = df[reason_column].fillna("").astype(str).apply(self._clean_reason)

        submission = df[["candidate_id", "rank", "score", "reasoning"]]

        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        submission.to_csv(output, index=False)

        return submission

    def _clean_reason(self, reason: str) -> str:
        reason = " ".join(str(reason).split())

        if not reason:
            return "Strong candidate based on combined relevance, behavioral, and trust signals."

        words = reason.split()
        if len(words) > 45:
            reason = " ".join(words[:45]) + "."

        return reason


if __name__ == "__main__":
    generator = SubmissionGenerator()
    generator.generate(
        ranked_input_path="data/outputs/ranked_candidates.csv",
        output_path="data/outputs/final_submission.csv",
    )
    print("final_submission.csv generated successfully.")