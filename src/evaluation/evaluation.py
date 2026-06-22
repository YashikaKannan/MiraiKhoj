"""
MiraiKhoj - Internal Evaluation

Metrics:
- Top 10 quality
- Top 20 quality
- Average score
- Honeypot rate
- Behavioral score distribution
"""

from __future__ import annotations

import pandas as pd
from typing import Dict, Any


class Evaluation:
    def evaluate(self, ranked_path: str) -> Dict[str, Any]:
        df = pd.read_csv(ranked_path)

        metrics = {
            "candidate_count": len(df),
            "average_final_score": self._mean(df, "final_score"),
            "top_10_average_score": self._mean(df.head(10), "final_score"),
            "top_20_average_score": self._mean(df.head(20), "final_score"),
            "average_behavior_score": self._mean(df, "behavior_score"),
            "average_availability_score": self._mean(df, "availability_score"),
            "average_recruitability_score": self._mean(df, "recruitability_score"),
            "average_engagement_score": self._mean(df, "engagement_score"),
            "average_credibility_score": self._mean(df, "credibility_score"),
            "average_trap_penalty": self._mean(df, "trap_penalty"),
            "honeypot_risk_rate_top_100": self._honeypot_rate(df.head(100)),
            "high_trap_count_top_100": self._high_trap_count(df.head(100)),
        }

        return metrics

    def _mean(self, df: pd.DataFrame, col: str) -> float:
        if col not in df.columns or len(df) == 0:
            return 0.0
        return round(float(df[col].fillna(0).mean()), 4)

    def _honeypot_rate(self, df: pd.DataFrame) -> float:
        if len(df) == 0 or "trap_penalty" not in df.columns:
            return 0.0

        high_risk = df["trap_penalty"].fillna(0) >= 25
        return round(float(high_risk.mean() * 100), 2)

    def _high_trap_count(self, df: pd.DataFrame) -> int:
        if "trap_penalty" not in df.columns:
            return 0
        return int((df["trap_penalty"].fillna(0) >= 25).sum())

    def save_report(
        self,
        ranked_path: str,
        output_path: str = "docs/END_TO_END_VALIDATION_REPORT.md",
    ) -> Dict[str, Any]:
        metrics = self.evaluate(ranked_path)

        lines = ["# MiraiKhoj Evaluation Report", ""]
        for key, value in metrics.items():
            lines.append(f"- **{key}**: {value}")

        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        return metrics


if __name__ == "__main__":
    evaluator = Evaluation()
    result = evaluator.save_report("data/outputs/ranked_candidates.csv")
    print(result)