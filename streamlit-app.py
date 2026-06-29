import streamlit as st
import pandas as pd
from pathlib import Path
from docx import Document
import tempfile

from scripts.run_full_pipeline import run

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

        report = run(jd_text, top_k=100)

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