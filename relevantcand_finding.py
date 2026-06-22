import pandas as pd

df = pd.read_csv("data/processed/processed_candidates.csv")

keywords = [
    "ai engineer",
    "ml engineer",
    "machine learning engineer",
    "nlp engineer",
    "search engineer",
    "recommendation engineer",
    "information retrieval"
]

count = 0

for text in df["candidate_text"].fillna("").astype(str):
    t = text.lower()
    if any(k in t for k in keywords):
        count += 1

print("Relevant candidates:", count)
print("Total candidates:", len(df))