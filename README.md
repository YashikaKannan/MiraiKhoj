# MiraiKhoj

MiraiKhoj is an intelligent candidate discovery and ranking engine for recruiter workflows.

It combines job description understanding, semantic retrieval, career intelligence, behavioral signals, and explainable ranking to surface the most relevant candidates from large profile pools.

## What is included

- Candidate JSONL processing into structured text and parquet output
- JD parsing into structured hiring signals
- Candidate and JD embeddings with GPU-aware batching
- FAISS retrieval for large-scale nearest-neighbor search
- Career intelligence and retrieval expertise scoring
- Behavioral and credibility scoring
- Honeypot detection for suspicious profiles
- Final score fusion and explanation generation
- Streamlit demo dashboard

## Quick start

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Run the Streamlit demo:

```bash
streamlit run streamlit_app.py
```

3. Or call the pipeline directly:

```bash
python src/main_pipeline.py --candidates candidates.jsonl --jd job_description.txt
```

## Project philosophy

The system favors semantic relevance, actual career fit, retrieval/search expertise, behavioral recruitability signals, and transparent explanations over keyword matching.
