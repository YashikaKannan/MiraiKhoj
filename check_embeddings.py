import numpy as np

emb = np.load("data/processed/candidate_embeddings.npy")
print(emb.shape)

import pandas as pd

df = pd.read_csv("data/processed/relevant_candidates.csv")
print(len(df))