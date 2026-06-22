from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import numpy as np

SRC_ROOT = Path(__file__).resolve().parents[1] / "src"
import sys
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from retrieval.faiss_builder import FaissIndexBuilder
from retrieval.retriever import FaissRetriever
from ranking.semantic_ranker import SemanticRanker
from career.career_analyzer import CareerAnalyzer
from career.retrieval_expertise import RetrievalExpertiseDetector
from utils.config import PathConfig


class PipelineComponentTests(unittest.TestCase):
    def setUp(self) -> None:
        self.cfg = PathConfig()
        self.sample_path = Path(r"D:\MiraiKhoj\data\raw\sample_candidates.json")
        self.df = None
        try:
            import pandas as pd

            self.df = pd.read_json(self.sample_path)
        except Exception:
            self.df = None

    def test_semantic_ranker_cosine(self) -> None:
        sr = SemanticRanker()
        a = np.array([1.0, 0.0, 0.0], dtype=np.float32)
        b = np.array([0.0, 1.0, 0.0], dtype=np.float32)
        self.assertAlmostEqual(sr.score(a, a), 1.0)
        self.assertGreater(sr.score(a, b), 0.0)

    def test_faiss_build_and_query(self) -> None:
        n = 20
        dim = 8
        rng = np.random.RandomState(0)
        emb = rng.randn(n, dim).astype('float32')
        ids = [f"C{i:03d}" for i in range(n)]

        builder = FaissIndexBuilder()
        bundle = builder.build(emb, ids)
        with tempfile.TemporaryDirectory() as tmpdir:
            idx_path = Path(tmpdir) / "test_index.faiss"
            id_path = Path(tmpdir) / "ids.json"
            builder.save(bundle, idx_path, id_path)
            retriever = FaissRetriever.from_files(idx_path, id_path)
            q = emb[0]
            hits = retriever.search(q, top_k=5)
            self.assertTrue(len(hits) > 0)

    def test_career_and_retrieval_detectors(self) -> None:
        cad = CareerAnalyzer()
        red = RetrievalExpertiseDetector()
        # create toy candidate dict
        cand = {
            "headline": "Senior ML Engineer",
            "summary": "Worked on retrieval, faiss and ranking. ndcg improvements.",
            "current_title": "ML Engineer",
            "current_company": "SearchCorp",
            "skills": ["python", "faiss", "pytorch"],
        }
        career = cad.analyze(cand)
        rex = red.analyze(cand)
        self.assertGreaterEqual(career.career_score, 0.0)
        self.assertGreaterEqual(rex.retrieval_expertise_score, 0.0)


if __name__ == "__main__":
    unittest.main()
