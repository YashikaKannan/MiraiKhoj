from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT / "src"))

from embeddings.embedder import EmbeddingEngine
from utils.config import EmbeddingConfig

# -----------------------------------
# Paths
# -----------------------------------

DEMO_CSV = Path("data/demo/processed_candidates_demo.csv")

OUTPUT_EMBEDDINGS = Path("data/demo/candidate_embeddings_demo.npy")
OUTPUT_IDS = Path("data/demo/candidate_index_ids_demo.json")

# -----------------------------------
# Load demo candidates
# -----------------------------------

df = pd.read_csv(DEMO_CSV)

print(f"Loaded {len(df)} demo candidates")

# -----------------------------------
# Build embedding model
# -----------------------------------

engine = EmbeddingEngine(EmbeddingConfig())

# -----------------------------------
# Generate embeddings
# -----------------------------------

texts = df["candidate_text"].fillna("").astype(str).tolist()

embeddings = engine.encode_texts(texts)

embeddings = np.asarray(embeddings, dtype=np.float32)

print("Embedding shape:", embeddings.shape)

# -----------------------------------
# Save embeddings
# -----------------------------------

OUTPUT_EMBEDDINGS.parent.mkdir(parents=True, exist_ok=True)

np.save(OUTPUT_EMBEDDINGS, embeddings)

print(f"Saved -> {OUTPUT_EMBEDDINGS}")

# -----------------------------------
# Save candidate ids
# -----------------------------------

candidate_ids = df["candidate_id"].astype(str).tolist()

with open(OUTPUT_IDS, "w", encoding="utf-8") as f:
    json.dump(candidate_ids, f, indent=2)

print(f"Saved -> {OUTPUT_IDS}")

print("\nDemo embeddings generated successfully.")