import pandas as pd

# Load the processed dataset
df = pd.read_csv("data/processed/processed_candidates.csv")

# Select first 100 candidates
demo = df.head(100)

# Save demo dataset
demo.to_csv("data/demo/processed_candidates_demo.csv", index=False)

print("Demo dataset created:", len(demo))