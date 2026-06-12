"""Streamlit demo dashboard for MiraiKhoj."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from main_pipeline import MiraiKhojPipeline

st.set_page_config(page_title="MiraiKhoj", page_icon="MK", layout="wide")

st.markdown(
    """
    <style>
        .stApp {
            background:
                radial-gradient(circle at top left, rgba(16, 185, 129, 0.18), transparent 30%),
                radial-gradient(circle at top right, rgba(37, 99, 235, 0.15), transparent 28%),
                linear-gradient(180deg, #07111f 0%, #0b1628 45%, #f5f7fb 45%, #f5f7fb 100%);
        }
        .hero {
            padding: 2.2rem 2rem 1.2rem 2rem;
            border-radius: 24px;
            background: rgba(7, 17, 31, 0.72);
            color: white;
            box-shadow: 0 18px 60px rgba(0,0,0,0.18);
            margin-bottom: 1rem;
        }
        .hero h1 {
            margin: 0;
            font-size: 3rem;
            letter-spacing: -0.04em;
        }
        .hero p {
            margin: 0.45rem 0 0;
            color: rgba(255,255,255,0.82);
            font-size: 1.05rem;
        }
        .card {
            background: rgba(255,255,255,0.88);
            border: 1px solid rgba(15, 23, 42, 0.08);
            border-radius: 20px;
            padding: 1rem 1rem 0.75rem 1rem;
            box-shadow: 0 12px 30px rgba(15, 23, 42, 0.08);
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
        <h1>MiraiKhoj</h1>
        <p>Finding Talent Beyond Keywords.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

left, right = st.columns([1.15, 0.85])
with left:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    candidates_file = st.file_uploader("Upload candidates.jsonl", type=["jsonl"])
    jd_text = st.text_area(
        "Paste the job description",
        height=320,
        placeholder="Looking for an AI engineer with retrieval, ranking, recommendation, and evaluation experience...",
    )
    top_k = st.slider("Top candidates", min_value=5, max_value=50, value=10)
    run_button = st.button("Rank Candidates", type="primary")
    st.markdown("</div>", unsafe_allow_html=True)

with right:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("What gets scored")
    st.write(
        "Semantic relevance, career fit, retrieval expertise, behavioral signals, credibility, logistics, and honeypot penalties."
    )
    st.subheader("Expected fields")
    st.code(
        "candidate_id, headline, summary, current_title, current_company, career_history, skills, certifications",
        language="text",
    )
    st.markdown('</div>', unsafe_allow_html=True)

if run_button:
    if not candidates_file or not jd_text.strip():
        st.error("Provide both a candidate file and a job description.")
    else:
        temp_candidates = ROOT / "_uploaded_candidates.jsonl"
        temp_candidates.write_bytes(candidates_file.getvalue())

        pipeline = MiraiKhojPipeline()
        with st.spinner("Ranking candidates..."):
            results = pipeline.rank(temp_candidates, jd_text, top_k=top_k)

        if not results:
            st.warning("No candidates were ranked.")
        else:
            df = pd.DataFrame(
                [
                    {
                        "candidate_id": row["candidate_id"],
                        "final_score": row["final_score"],
                        "semantic_score": row["semantic_score"],
                        "career_score": row["career_score"],
                        "retrieval_expertise_score": row["retrieval_expertise_score"],
                        "behavioral_score": row["behavioral_score"],
                        "credibility_score": row["credibility_score"],
                        "logistics_score": row["logistics_score"],
                        "trap_penalty": row["trap_penalty"],
                        "reason": row["candidate_reason"],
                    }
                    for row in results
                ]
            )
            st.subheader("Ranked candidates")
            st.dataframe(df, use_container_width=True)
            st.download_button(
                "Download JSON",
                data=json.dumps(results, indent=2, ensure_ascii=False),
                file_name="ranked_candidates.json",
                mime="application/json",
            )
