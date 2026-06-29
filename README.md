# 🚀 MiraiKhoj - Intelligent Candidate Discovery System


## Overview

MiraiKhoj is an AI-powered candidate discovery and ranking platform designed to identify the most relevant candidates for a given Job Description (JD).

Unlike traditional keyword-based recruitment systems, MiraiKhoj combines:

* Semantic Search
* Retrieval Intelligence
* Career Analysis
* Behavioral Intelligence
* Honeypot Detection
* Explainable AI Ranking

to rank candidates based on both relevance and recruitability.

---

## Problem Statement

Recruiters often receive thousands of candidate profiles for a single role.

Traditional ATS systems rely heavily on keyword matching, which results in:

* Poor candidate relevance
* High false positives
* Keyword-stuffed profiles
* Lack of explainability
* Ignoring behavioral hiring signals

MiraiKhoj solves this by combining semantic understanding, career intelligence, behavioral signals, and trust-based scoring.

---

# Quick Start

## 1. Clone Repository

```bash
git clone <repository_url>
cd MiraiKhoj
```

## 2. Install Backend Dependencies

```bash
pip install -r requirements.txt
```

## Run Candidate Ranking
This command generates the final Top-100 ranked candidate submission.

```bash
python scripts/run_full_pipeline.py --jd data/sample_jd.txt --top-k 100
```

or, if using a Word document:

```bash
python scripts/run_full_pipeline.py --jd data/sample_jd.docx --top-k 100
```

The pipeline will:

- Parse the Job Description
- Retrieve candidates from the indexed corpus
- Rank candidates using semantic, career, behavioral, and credibility signals
- Generate the **Top 100** ranked candidates
- Save the output to:

```text
data/outputs/ranked_candidates.csv
```
## Pre-computation

MiraiKhoj precomputes candidate embeddings and the FAISS index during the data preparation stage.

Generated artifacts:

- data/processed/candidate_embeddings.npy
- data/processed/candidate_index.faiss
- data/processed/candidate_index_ids.json

During ranking, these precomputed artifacts are loaded directly, allowing the complete ranking pipeline to run offline on CPU without regenerating embeddings.

## 3. Start Backend

```bash
uvicorn backend.app:app --reload
```

Backend:
http://localhost:8000

---

## 4. Start Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend:
http://localhost:8080

---

### Streamlit Sandbox

```text
For reproducibility and evaluation, MiraiKhoj also includes a lightweight Streamlit sandbox.
The Streamlit sandbox is intended for reproducibility on small candidate samples (≤100 candidates), while the full pipeline supports large-scale candidate ranking.
```

Features:

- Upload Job Description (`.txt` or `.docx`)
- Or paste the Job Description directly
- Run the complete ranking pipeline
- Preview the Top 20 ranked candidates
- Download the final Top 100 submission CSV

Run locally:

```bash
streamlit run streamlit-app.py
```

Deployed Sandbox:

> https://mirai-khoj.streamlit.app
---


## 5. Open

http://localhost:8080

# System Architecture

```text
                        ┌─────────────────────┐
                        │ Job Description (JD)│
                        └──────────┬──────────┘
                                   │
                                   ▼

                    ┌──────────────────────────┐
                    │ JD Intelligence Engine   │
                    └──────────────────────────┘

                     • Skill Extraction
                     • Experience Extraction
                     • Seniority Detection
                     • Domain Understanding
                     • Location Detection

                                   │
                                   ▼

                         JD Embedding Vector

        ══════════════════════════════════════════════════════

                        Candidate Knowledge Base

                Profiles + Skills + Career History +
                Certifications + Behavioral Signals

        ══════════════════════════════════════════════════════

                                   │
                                   ▼

                    ┌──────────────────────────┐
                    │ Embedding Engine         │
                    └──────────────────────────┘

                     Sentence Transformers
                     (all-MiniLM-L6-v2)

                                   │
                                   ▼

                    ┌──────────────────────────┐
                    │ FAISS Retrieval Layer    │
                    └──────────────────────────┘

                     Top-K Relevant Candidates

                                   │
                                   ▼

                    ┌──────────────────────────┐
                    │ Career Intelligence      │
                    └──────────────────────────┘

                     • Career Progression
                     • Product Experience
                     • AI Experience
                     • Search & Ranking
                     • Retrieval Expertise

                                   │
                                   ▼

                    ┌──────────────────────────┐
                    │ Behavioral Intelligence  │
                    └──────────────────────────┘

                     • Availability
                     • Recruitability
                     • Engagement
                     • Credibility

                                   │
                                   ▼

                    ┌──────────────────────────┐
                    │ Trap Detection Engine    │
                    └──────────────────────────┘

                     • Keyword Stuffing
                     • Fake Seniority
                     • Career Mismatch
                     • Honeypot Profiles

                                   │
                                   ▼

                    ┌──────────────────────────┐
                    │ Score Fusion Engine      │
                    └──────────────────────────┘

                     Semantic Score
                     Career Score
                     Retrieval Score
                     Behavioral Score
                     Credibility Score
                     − Trap Penalty

                                   │
                                   ▼

                    ┌──────────────────────────┐
                    │ Explainability Engine    │
                    └──────────────────────────┘

                     • Matched Skills
                     • Retrieval Evidence
                     • Career Fit
                     • Ranking Reason

                                   │
                                   ▼

                    ┌──────────────────────────┐
                    │ Top 100 Candidates       │
                    └──────────────────────────┘

                                   │
                                   ▼

                         Final Submission CSV
```

---

# Key Features

## 1. JD Intelligence Engine

Parses Job Descriptions and extracts:

* Required Skills
* Preferred Skills
* Seniority Level
* Experience Requirements
* Domain Keywords
* Evaluation Metrics

Example:

```text
Python
Machine Learning
FAISS
Elasticsearch
Ranking
Recommendation Systems
```

---

## 2. Semantic Candidate Retrieval

Uses:

* Sentence Transformers
* Dense Embeddings
* FAISS Vector Search

Workflow:

```text
Candidate Profiles
      ↓
Embeddings
      ↓
FAISS Index
      ↓
Top Relevant Candidates
```

Supports retrieval across thousands of candidate profiles in milliseconds.

---

## 3. Career Intelligence Engine

Analyzes:

* Career Progression
* Product vs Service Experience
* AI Engineering Experience
* Search & Ranking Experience
* Recommendation System Experience

Produces:

```python
career_score
```

---

## 4. Retrieval Expertise Detection

Detects expertise in:

* FAISS
* Elasticsearch
* OpenSearch
* Pinecone
* Weaviate
* Milvus
* Qdrant
* BM25
* Vector Search

Produces:

```python
retrieval_expertise_score
```

---

## 5. Behavioral Intelligence Engine

Analyzes recruiter-oriented signals such as:

* Open To Work
* Recruitability
* Engagement
* Profile Completeness
* Availability

Produces:

```python
availability_score
recruitability_score
engagement_score
credibility_score
behavioral_score
```

---

## 6. Trap / Honeypot Detection

Detects suspicious candidate profiles:

### Keyword Stuffing

Example:

```text
FAISS
LLM
RAG
GPT
Pinecone
```

without actual career evidence.

### Fake Seniority

Example:

```text
Lead Engineer
2 Years Experience
```

### Career Mismatch

Example:

```text
Marketing Manager
Claiming Advanced AI Search Skills
```

Produces:

```python
trap_penalty
```

---

## 7. Explainable AI Ranking

Each candidate receives recruiter-friendly explanations.

Example:

```text
7.8 years of relevant experience.

Currently working as Search Engineer at Nykaa.

Matched 8 JD skills including
Python, Machine Learning,
FAISS, Search and Ranking.

Hands-on experience with
FAISS, Elasticsearch,
Qdrant and Weaviate.

Strong retrieval and ranking expertise.
```

---

# Scoring Methodology

Final ranking combines:

```python
final_score =
semantic_score +
career_score +
retrieval_expertise_score +
behavioral_score +
credibility_score +
logistics_score -
trap_penalty
```

The objective is to rank candidates based on:

* Relevance
* Expertise
* Recruitability
* Credibility

instead of keyword frequency.

---

# Project Structure

```text
MiraiKhoj
│
├── data/
│
├── docs/
│
├── scripts/
│
├── src/
│   │
│   ├── jd/
│   │   └── jd_parser.py
│   │
│   ├── embeddings/
│   │   └── embedder.py
│   │
│   ├── data/
│   │
│   ├── evaluation/
│   │
│   ├── retrieval/
│   │   ├── faiss_builder.py
│   │   └── retriever.py
│   │
│   ├── career/
│   │   ├── career_analyzer.py
│   │   └── retrieval_expertise.py
│   │
│   ├── behavior/
│   │   ├── signal_engine.py
│   │   └── signal_scorer.py
│   │
│   ├── honeypot/
│   │   └── trap_detector.py
│   │
│   ├── ranking/
│   │   ├── semantic_ranker.py
│   │   ├── ai_ranker.py
│   │   └── score_fusion.py
│   │
│   ├── explainability/
│   │   └── explainer.py
│   │
│   ├── submission/
│   │   ├── submission_generator.py
│   │   └── validate_submission.py
│   │
│   └── utils/
│
├── tests/
│
├── streamlit-app.py
│
├── frontend/
│
├── backend/
│
└── README.md
```

# Output

The system generates:

## Top 100 Ranked Candidates

```csv
candidate_id
rank
score
reasoning
```

## The final submission file is generated as:
```text
data/outputs/final_submission.csv
```

## Candidate Explanations

Human-readable recruiter explanations.

## FAISS Index

```text
candidate_index.faiss
candidate_index_ids.json
```

## Candidate Embeddings

```text
candidate_embeddings.npy
```

---

# Technology Stack

### AI / ML

* Sentence Transformers
* FAISS
* Gemini 2.5 Flash (LLM Re-ranking)
* NumPy
* Pandas

### Frontend

* React
* TypeScript
* Vite
* Tailwind CSS
* Streamlit (Sandbox)
  
### Backend

* Python
* FastAPI
* Uvicorn

### API Endpoints

POST /rank
GET /analytics
GET /candidate/{candidate_id}

### Retrieval

* FAISS Vector Search
* Semantic Search

### Explainability

* Rule-Based AI Explanations
* LLM-Based Recruiter Reasoning (with fallback)

---


## User Interface

MiraiKhoj includes an interactive recruiter dashboard that allows users to:

• Paste any Job Description
• Rank Top 100 Candidates
• View Explainable AI Reasons
• Explore Candidate Analytics
• Inspect Individual Candidate Profiles

---

# Team Contributions

### AI Ranking Engine

* JD Intelligence
* Candidate Retrieval
* Embeddings Generation
* FAISS Indexing
* Career Intelligence
* Retrieval Expertise Detection
* Score Fusion
* Semantic Ranking
* Explainability

### Behavioral Intelligence Engine

* Behavioral Scoring
* Recruitability Analysis
* Trap Detection
* Submission Generation
* Evaluation Framework

### Frontend & API

• Recruiter Dashboard
• Analytics Dashboard
• Candidate Explorer
• FastAPI Backend
• Submission Pipeline

---

# Vision

MiraiKhoj focuses on:

> "Ranking candidates based on recruitability, credibility, and relevance — not just keywords."

The system helps recruiters discover high-quality candidates faster while providing transparent and explainable ranking decisions.

---

# The ranking pipeline runs completely offline after the candidate embeddings and FAISS index have been precomputed. No external API calls are required during ranking.

## License

Developed for the Redrob India Runs Data & AI Challenge.
