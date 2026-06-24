from __future__ import annotations
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT / "src"))
import logging
import time
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

from embeddings.embedder import EmbeddingEngine
from utils.config import PathConfig, PipelineConfig


logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s - %(message)s")
logger = logging.getLogger(__name__)


def _load_candidates(path: Path) -> pd.DataFrame:
    if path.suffix == ".parquet":
        return pd.read_parquet(path)
    return pd.read_csv(path)


def generate_embeddings(
    processed_path: Path | str | None = None,
    out_path: Path | str | None = None,
    batch_size: Optional[int] = None,
) -> dict:
    cfg = PipelineConfig()
    # processed_path = Path(processed_path) if processed_path else cfg.paths.processed_candidates
    # to generate embeddings for only relevant candidates
    processed_path = (
    Path(processed_path)
    if processed_path
    else cfg.paths.processed_dir / "processed_candidates.csv")
    out_path = Path(out_path) if out_path else cfg.paths.candidate_embeddings

    df = _load_candidates(processed_path)
    texts = df["candidate_text"].astype(str).tolist()
    n = len(texts)
    engine = EmbeddingEngine(cfg.embedding)

    start = time.time()
    # encode first batch to discover dimension
    batch_size = batch_size or cfg.embedding.batch_size
    first_batch = texts[: min(batch_size, n)]
    first_emb = engine.encode_texts(first_batch, batch_size=batch_size)
    dim = first_emb.shape[1]

    # create memmap-backed .npy file
    out_path.parent.mkdir(parents=True, exist_ok=True)
    mem = np.lib.format.open_memmap(str(out_path), mode="w+", dtype="float32", shape=(n, dim))
    mem[: first_emb.shape[0]] = first_emb

    idx = first_emb.shape[0]
    logger.info("Embedding dim=%s, candidates=%s", dim, n)

    try:
        from tqdm import tqdm

        iterator = range(idx, n, batch_size)
        iterator = tqdm(list(iterator), desc="Embedding batches")
    except Exception:
        iterator = range(idx, n, batch_size)

    for start_idx in iterator:
        end_idx = min(start_idx + batch_size, n)
        batch = texts[start_idx:end_idx]
        emb = engine.encode_texts(batch, batch_size=batch_size)
        mem[start_idx:end_idx] = emb
        if (start_idx // batch_size) % 10 == 0:
            logger.info("Processed embeddings %s/%s", end_idx, n)

    mem.flush()
    duration = time.time() - start

    try:
        import psutil

        process = psutil.Process()
        mem_info = process.memory_info().rss
    except Exception:
        mem_info = -1

    size_bytes = out_path.stat().st_size if out_path.exists() else 0

    report = {
        "model": cfg.embedding.primary_model_name,
        "dim": int(dim),
        "candidate_count": int(n),
        "runtime_seconds": float(duration),
        "memory_rss_bytes": int(mem_info),
        "output_file": str(out_path),
        "output_size_bytes": int(size_bytes),
    }

    logger.info("Embedding generation finished in %.2fs", duration)
    return report


def main() -> None:
    cfg = PathConfig()
    report = generate_embeddings()
    md = ["# Embedding Report\n\n"]
    md.append(f"- Model: {report['model']}\n")
    md.append(f"- Dimensions: {report['dim']}\n")
    md.append(f"- Candidates: {report['candidate_count']}\n")
    md.append(f"- Runtime (s): {report['runtime_seconds']:.2f}\n")
    md.append(f"- Memory RSS (bytes): {report['memory_rss_bytes']}\n")
    md.append(f"- Output file: {report['output_file']}\n")
    md.append(f"- Output size (bytes): {report['output_size_bytes']}\n")

    report_path = cfg.data_dir / "docs" / "EMBEDDING_REPORT.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("".join(md), encoding="utf-8")
    logger.info("Wrote embedding report to %s", report_path)


if __name__ == "__main__":
    main()
