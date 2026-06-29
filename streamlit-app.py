import streamlit as st
import pandas as pd
from pathlib import Path
from docx import Document
import tempfile

from scripts.run_full_pipeline import run
from utils.config import PathConfig

cfg = PathConfig()

cfg.processed_candidates = Path("data/demo/processed_candidates_demo.csv")
cfg.candidate_embeddings = Path("data/demo/candidate_embeddings_demo.npy")
cfg.candidate_index = Path("data/demo/candidate_index_demo.faiss")
cfg.candidate_index_ids = Path("data/demo/candidate_index_ids_demo.json")

st.set_page_config(
    page_title="MiraiKhoj",
    page_icon="🔍",
    layout="wide",
)

st.title("🔍 MiraiKhoj")
st.subheader("Intelligent Candidate Discovery System")

st.write(
    "Upload or paste a Job Description to generate the Top 100 ranked candidates."
)

uploaded = st.file_uploader(
    "Upload Job Description (.txt or .docx)",
    type=["txt", "docx"],
)

jd_text = st.text_area(
    "Or Paste Job Description",
    height=250,
)

if st.button("Rank Candidates"):

    # Read uploaded file
    if uploaded is not None:

        if uploaded.name.endswith(".txt"):
            jd_text = uploaded.read().decode("utf-8")

        elif uploaded.name.endswith(".docx"):
            doc = Document(uploaded)
            jd_text = "\n".join(
                para.text for para in doc.paragraphs
            )

    if not jd_text.strip():
        st.error("Please upload or paste a Job Description.")
        st.stop()

    with st.spinner("Ranking candidates..."):

        report = run(jd_text, top_k=100, demo=True)

    csv_path = Path("data/outputs/final_submission.csv")

    df = pd.read_csv(csv_path)

    st.success("Ranking Completed!")

    st.dataframe(df)

    with open(csv_path, "rb") as f:
        st.download_button(
            "Download final_submission.csv",
            f,
            file_name="final_submission.csv",
            mime="text/csv",
        )

st.info(
    "Demo Mode: This sandbox runs on a curated sample of 100 candidates for reproducibility. "
    "The full pipeline supports the complete candidate dataset and is available in the GitHub repository."
)
