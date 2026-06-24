from __future__ import annotations

import json
import logging
import time
from pathlib import Path
from typing import Dict

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT / "src"))

import pandas as pd

from data.loader import load_candidates, iter_candidate_records
from data.preprocess import build_processed_candidate_row
from utils.config import PathConfig

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s - %(message)s")
logger = logging.getLogger(__name__)


def main() -> None:
    cfg = PathConfig()
    raw_path = cfg.data_dir / "raw" / "candidates.jsonl"
    processed_path = cfg.processed_candidates
    report_path = cfg.data_dir / "processed" / "PREPROCESSING_REPORT.md"

    start = time.time()
    logger.info("Loading candidates from %s", raw_path)
    df = load_candidates(raw_path)
    total = len(df)

    processed_rows = []
    failed = 0
    missing_stats: Dict[str, int] = {"candidate_text": 0, "years_of_experience": 0, "current_title": 0, "current_company": 0}

    for idx, raw in enumerate(iter_candidate_records(raw_path), start=1):
        try:
            row = build_processed_candidate_row(raw.raw_record)
            for key in list(missing_stats.keys()):
                if row.get(key) in (None, "", []):
                    missing_stats[key] += 1
            processed_rows.append(row)
        except Exception:
            logger.exception("Failed to process candidate at %s", idx)
            failed += 1

    proc_df = pd.DataFrame.from_records(processed_rows)
    # try:
    #     proc_df.to_parquet(processed_path, index=False)
    # except Exception:
    #     csv_path = processed_path.with_suffix('.csv')
    #     proc_df.to_csv(csv_path, index=False)
    #     logger.warning("pyarrow/fastparquet not available; wrote CSV to %s", csv_path)

    # Save as CSV
    proc_df.to_csv(processed_path, index=False)
    
    duration = time.time() - start

    report = {
        "total_records_loaded": int(total),
        "total_records_processed": int(len(proc_df)),
        "failed_records": int(failed),
        "runtime_seconds": float(duration),
        "output_schema": list(proc_df.columns),
        "missing_field_stats": missing_stats,
    }

    report_md = ["# Preprocessing Report\n", "\n", "## Summary\n", "\n"]
    report_md.append(f"- Total records loaded: {report['total_records_loaded']}\n")
    report_md.append(f"- Total records processed: {report['total_records_processed']}\n")
    report_md.append(f"- Failed records: {report['failed_records']}\n")
    report_md.append(f"- Runtime (s): {report['runtime_seconds']:.2f}\n")
    report_md.append("\n## Output Schema\n\n")
    for col in report['output_schema']:
        report_md.append(f"- {col}\n")
    report_md.append("\n## Missing Field Statistics\n\n")
    for key, val in report['missing_field_stats'].items():
        report_md.append(f"- {key}: {val}\n")

    report_md.append("\n## Notes\n\n")
    report_md.append("- The processed candidate text is a canonical secondary representation built from structured fields.\n")

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("".join(report_md), encoding="utf-8")
    logger.info("Wrote preprocessing report to %s", report_path)


if __name__ == '__main__':
    main()
