# Project Overview

**Project Name:** MiraiKhoj

**Tagline:** _Finding Talent Beyond Keywords._

## Challenge Context

The Redrob Data & AI Challenge calls for a production-grade candidate ranking system that can surface the most relevant candidates from a large pool using AI rather than simple keyword matching. MiraiKhoj is built to address that problem.

Traditional applicant tracking systems usually reward keyword overlap. MiraiKhoj instead ranks candidates using semantic understanding, career fit, retrieval/search expertise, behavioral signals, credibility signals, and explainable fusion.

## Problem Statement

Given:

- a raw job description,
- a candidate corpus with 100,000+ profiles,
- and optional behavioral metadata,

MiraiKhoj returns a ranked list of candidates with reasons for each ranking decision.

## Why This Is Different

MiraiKhoj does not treat candidates as bags of keywords. It evaluates:

- whether the candidate has actually worked in the right domain,
- whether the career path reflects relevant growth,
- whether the candidate has hands-on retrieval or ranking expertise,
- whether the candidate appears recruitable and available,
- whether the profile looks credible,
- and whether the profile contains fraud or stuffing signals.

## Primary Use Cases

- Recruiters screening AI, ML, search, and ranking talent
- Hiring teams looking for applied retrieval or recommendation expertise
- Talent intelligence teams ranking candidates from large internal corpora
- Challenge judges evaluating explainable AI ranking systems

## Key Inputs and Outputs

### Inputs

- Candidate corpus in JSONL format
- Raw job description text
- Optional behavioral signals such as availability, engagement, and recruiter interest

### Outputs

- Ranked candidate list
- Final score for each candidate
- Component score breakdowns
- Human-readable explanation text
- Persisted artifacts for retrieval and scoring

## High-Level Workflow

```mermaid
flowchart LR
    JD[Job Description] --> JDX[JD Intelligence]
    CAND[Candidate JSONL] --> PROC[Candidate Processing]
    PROC --> EMB1[Candidate Embeddings]
    JDX --> EMB2[JD Embedding]
    EMB1 --> RET[FAISS Retrieval]
    EMB2 --> RET
    RET --> SCORE[Multi-Signal Scoring]
    SCORE --> FUSE[Final Rank Fusion]
    FUSE --> EXPLAIN[Explainability]
    EXPLAIN --> OUT[Ranked Candidates]
```

## Value Proposition

MiraiKhoj helps recruiters find candidates who are not just syntactically similar to the job description, but strategically aligned with the role. It is especially useful for roles involving:

- AI and machine learning engineering
- search and information retrieval
- recommendation systems
- ranking and relevance optimization
- semantic search and vector databases

## System Qualities

- **Modular:** each capability lives in a dedicated module
- **Explainable:** each ranking is justified in plain language
- **Scalable:** retrieval is designed for large profile pools
- **Extensible:** scoring rules and models can be improved without rewriting the pipeline
- **Demo-ready:** includes a Streamlit dashboard for challenge submission and review

## Expected Deployment Story

For challenge submission, the likely demo flow is:

1. Load candidate corpus.
2. Enter or paste a job description.
3. Generate embeddings and retrieve candidates.
4. Display ranked candidates with explanations.
5. Allow judges to inspect score components and output quality.
