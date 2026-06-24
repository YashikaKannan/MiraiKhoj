from pathlib import Path
import pandas as pd

from scripts.run_full_pipeline import run


def rank_candidates(jd_text: str, top_k: int):
    """
    Execute the AI ranking pipeline and return ranked candidates.
    """

    # Run your existing pipeline
    run(jd_text=jd_text, top_k=top_k)

    # Load generated CSV
    csv_path = Path("data/outputs/ranked_candidates.csv")

    df = pd.read_csv(csv_path)

    return df.to_dict(orient="records")