import pandas as pd
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT / "src"))

INPUT_FILE = "data/processed/processed_candidates.csv"
OUTPUT_FILE = "data/processed/relevant_candidates.csv"

KEYWORDS = [
    "ai engineer",
    "ml engineer",
    "machine learning engineer",
    "nlp engineer",
    "search engineer",
    "recommendation engineer",
    "information retrieval"
]

df = pd.read_csv(INPUT_FILE)

mask = df["candidate_text"].fillna("").str.lower().apply(
    lambda text: any(keyword in text for keyword in KEYWORDS)
)

filtered_df = df[mask]

filtered_df.to_csv(OUTPUT_FILE, index=False)

print(f"Filtered candidates: {len(filtered_df)}")
print(f"Saved to: {OUTPUT_FILE}")