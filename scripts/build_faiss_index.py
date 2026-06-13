from __future__ import annotations
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT / "src"))
import logging
import time
from pathlib import Path
from typing import List

import numpy as np
import pandas as pd

from retrieval.faiss_builder import FaissIndexBuilder
from retrieval.retriever import FaissRetriever, RetrievalHit
from utils.config import PathConfig


logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s - %(message)s")
logger = logging.getLogger(__name__)


def build_index(embeddings_path: Path | str | None = None) -> dict:
    cfg = PathConfig()
    embeddings_path = Path(embeddings_path) if embeddings_path else cfg.candidate_embeddings
    emb = np.load(embeddings_path, mmap_mode="r")

    # load candidate ids
    cand_df = pd.read_csv("data/processed/relevant_candidates.csv")
    candidate_ids: List[str] = cand_df["candidate_id"].astype(str).tolist()

    builder = FaissIndexBuilder()
    start = time.time()
    print("Embeddings:", emb.shape[0])
    print("Candidate IDs:", len(candidate_ids))
    bundle = builder.build(emb, candidate_ids)
    builder.save(bundle, cfg.candidate_index, cfg.candidate_index_ids)
    duration = time.time() - start

    # quick retrieval benchmark
    retriever = FaissRetriever.from_files(cfg.candidate_index, cfg.candidate_index_ids)
    sample_queries = min(100, emb.shape[0])
    import random

    q_indices = random.sample(range(emb.shape[0]), sample_queries)
    times = []
    for qi in q_indices:
        q = emb[qi]
        t0 = time.time()
        _hits = retriever.search(q, top_k=10)
        times.append(time.time() - t0)

    avg_latency = sum(times) / len(times) if times else 0.0

    report = {
        "index_type": type(bundle.index).__name__,
        "candidate_count": int(bundle.index.ntotal),
        "build_time_seconds": float(duration),
        "avg_query_latency_seconds": float(avg_latency),
        "index_file": str(cfg.candidate_index),
    }

    logger.info("Built FAISS index: %s vectors", bundle.index.ntotal)
    return report


def main() -> None:
    cfg = PathConfig()
    report = build_index()
    md = ["# Retrieval Report\n\n"]
    md.append(f"- Index type: {report['index_type']}\n")
    md.append(f"- Candidate count: {report['candidate_count']}\n")
    md.append(f"- Build time (s): {report['build_time_seconds']:.2f}\n")
    md.append(f"- Avg query latency (s): {report['avg_query_latency_seconds']:.6f}\n")
    md.append(f"- Index file: {report['index_file']}\n")

    report_path = cfg.data_dir / "docs" / "RETRIEVAL_REPORT.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("".join(md), encoding="utf-8")
    logger.info("Wrote retrieval report to %s", report_path)


if __name__ == "__main__":
    main()
