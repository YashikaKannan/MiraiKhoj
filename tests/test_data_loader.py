from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
import sys

import pandas as pd

SRC_ROOT = Path(__file__).resolve().parents[1] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from data.loader import (
    REQUIRED_PROFILE_FIELDS,
    REQUIRED_SIGNAL_FIELDS,
    build_candidate_text,
    iter_candidate_records,
    load_candidates,
    validate_candidate_schema,
)


class LoaderSchemaTests(unittest.TestCase):
    def setUp(self) -> None:
        self.sample_path = Path(r"D:\MiraiKhoj\data\raw\sample_candidates.json")
        self.jsonl_path = Path(r"D:\MiraiKhoj\data\raw\candidates.jsonl")

    def test_sample_candidates_schema_compatibility(self) -> None:
        sample_records = json.loads(self.sample_path.read_text(encoding="utf-8"))
        self.assertEqual(len(sample_records), 50)
        for record in sample_records:
            self.assertEqual(validate_candidate_schema(record), [])

    def test_jsonl_first_record_schema_compatibility(self) -> None:
        first_line = self.jsonl_path.read_text(encoding="utf-8").splitlines()[0]
        record = json.loads(first_line)
        self.assertEqual(validate_candidate_schema(record), [])

    def test_loader_preserves_nested_structure(self) -> None:
        df = load_candidates(self.sample_path)
        self.assertEqual(len(df), 50)
        self.assertIn("profile", df.columns)
        self.assertIn("redrob_signals", df.columns)
        row = df.iloc[0]
        self.assertIsInstance(row["profile"], dict)
        self.assertIsInstance(row["career_history"], list)
        self.assertIsInstance(row["skills"], list)
        self.assertIsInstance(row["redrob_signals"], dict)
        self.assertIn("Headline:", row["candidate_text"])
        self.assertIn("Skills:", row["candidate_text"])

    def test_loader_handles_missing_optional_fields(self) -> None:
        valid_record = {
            "candidate_id": "CAND_9999999",
            "profile": {
                "anonymized_name": "Test Candidate",
                "headline": "Test Engineer",
                "summary": "Testing optional fields.",
                "location": "Remote",
                "country": "India",
                "years_of_experience": 3.5,
                "current_title": "Test Engineer",
                "current_company": "ExampleCo",
                "current_company_size": "11-50",
                "current_industry": "Software",
            },
            "career_history": [
                {
                    "company": "ExampleCo",
                    "title": "Test Engineer",
                    "start_date": "2022-01-01",
                    "end_date": None,
                    "duration_months": 24,
                    "is_current": True,
                    "industry": "Software",
                    "company_size": "11-50",
                    "description": "Worked on test systems.",
                }
            ],
            "education": [
                {
                    "institution": "Example University",
                    "degree": "B.Tech",
                    "field_of_study": "Computer Science",
                    "start_year": 2015,
                    "end_year": 2019,
                }
            ],
            "skills": [
                {
                    "name": "Python",
                    "proficiency": "advanced",
                    "endorsements": 10,
                }
            ],
            "redrob_signals": {
                "profile_completeness_score": 90.0,
                "signup_date": "2025-01-01",
                "last_active_date": "2025-01-02",
                "open_to_work_flag": True,
                "profile_views_received_30d": 10,
                "applications_submitted_30d": 1,
                "recruiter_response_rate": 0.5,
                "avg_response_time_hours": 24.0,
                "skill_assessment_scores": {},
                "connection_count": 100,
                "endorsements_received": 5,
                "notice_period_days": 30,
                "expected_salary_range_inr_lpa": {"min": 10, "max": 15},
                "preferred_work_mode": "remote",
                "willing_to_relocate": True,
                "github_activity_score": 88.0,
                "search_appearance_30d": 20,
                "saved_by_recruiters_30d": 3,
                "interview_completion_rate": 0.75,
                "offer_acceptance_rate": -1,
                "verified_email": True,
                "verified_phone": False,
                "linkedin_connected": True,
            },
        }
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "candidates.json"
            path.write_text(json.dumps([valid_record]), encoding="utf-8")
            df = load_candidates(path)
        self.assertEqual(len(df), 1)
        self.assertEqual(df.iloc[0]["certifications"], [])
        self.assertEqual(df.iloc[0]["languages"], [])
        self.assertIn("Python", df.iloc[0]["candidate_text"])

    def test_iter_candidate_records_streams_valid_rows(self) -> None:
        records = list(iter_candidate_records(self.sample_path))
        self.assertEqual(len(records), 50)
        self.assertTrue(all(record.candidate_id.startswith("CAND_") for record in records))


if __name__ == "__main__":
    unittest.main()
