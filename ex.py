import pandas as pd
import numpy as np

# df = pd.read_csv("data/processed/relevant_candidates.csv")
# emb = np.load("data/processed/candidate_embeddings.npy", mmap_mode="r")

# print(len(df))
# print(emb.shape)


# Checking duplicates

df = pd.read_csv("data/outputs/ranked_candidates.csv")

print("Total rows:", len(df))
print("Unique candidate IDs:", df["candidate_id"].nunique())

duplicates = df[df.duplicated("candidate_id", keep=False)]

if duplicates.empty:
    print("No duplicate candidate IDs found.")
else:
    print("Duplicate candidate IDs found:")
    print(duplicates[["candidate_id", "rank"]])


print("Unique IDs:", df["candidate_id"].nunique())
print("Duplicate IDs:", df["candidate_id"].duplicated().sum())
print("Ranks OK:", list(df["rank"]) == list(range(1, len(df)+1)))
print("Scores descending:", df["final_score"].is_monotonic_decreasing)