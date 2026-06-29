from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT / "src"))

from retrieval.faiss_builder import FaissIndexBuilder

# ---------------------------------------------------
# Paths
# ---------------------------------------------------

EMBEDDINGS = Path("data/demo/candidate_embeddings_demo.npy")
CSV = Path("data/demo/processed_candidates_demo.csv")

INDEX = Path("data/demo/candidate_index_demo.faiss")
IDS = Path("data/demo/candidate_index_ids_demo.json")

# ---------------------------------------------------
# Load data
# ---------------------------------------------------

embeddings = np.load(EMBEDDINGS)

df = pd.read_csv(CSV)

candidate_ids = df["candidate_id"].astype(str).tolist()

print(f"Loaded {len(candidate_ids)} candidates")
print(f"Embedding shape: {embeddings.shape}")

# ---------------------------------------------------
# Build FAISS
# ---------------------------------------------------

builder = FaissIndexBuilder()

bundle = builder.build(
    embeddings=embeddings,
    candidate_ids=candidate_ids,
)

builder.save(
    bundle,
    INDEX,
    IDS,
)

print("\nDemo FAISS index created successfully!")

print(INDEX)
print(IDS)