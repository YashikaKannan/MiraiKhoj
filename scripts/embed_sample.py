from __future__ import annotations

import time
from pathlib import Path
import numpy as np
import pandas as pd

from utils.config import PathConfig
from embeddings.embedder import EmbeddingEngine


def main() -> None:
    cfg = PathConfig()
    proc_csv = cfg.data_dir / 'processed' / 'processed_candidates.csv'
    df = pd.read_csv(proc_csv)
    engine = EmbeddingEngine()
    sample_texts = df['candidate_text'].astype(str).tolist()[:128]
    start = time.time()
    emb = engine.encode_texts(sample_texts, batch_size=32)
    print('emb shape', emb.shape)
    engine.save_embeddings(emb, cfg.data_dir / 'processed' / 'candidate_embeddings_sample.npy')
    print('time', time.time() - start)


if __name__ == '__main__':
    main()
