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
└── README.md
```

---

# Output

The system generates:

## Ranked Candidates

```csv
candidate_id
rank
final_score
candidate_reason
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
* NumPy
* Pandas

### Backend

* Python
* FastAPI

### Retrieval

* Vector Search
* Semantic Search

### Explainability

* Rule-Based AI Explanations

---

# Team Contributions

### AI Ranking Engine

* JD Intelligence
* Candidate Retrieval
* Embeddings
* FAISS Indexing
* Career Intelligence
* Retrieval Expertise Detection
* Semantic Ranking
* Explainability

### Behavioral Intelligence Engine

* Behavioral Scoring
* Recruitability Analysis
* Trap Detection
* Submission Generation
* Evaluation Framework

---

# Vision

MiraiKhoj focuses on:

> "Ranking candidates based on recruitability, credibility, and relevance — not just keywords."

The system helps recruiters discover high-quality candidates faster while providing transparent and explainable ranking decisions.
