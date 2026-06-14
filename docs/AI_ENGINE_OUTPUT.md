# AI Engine Output Contract

## Purpose

This document defines the output interface produced by the AI Ranking Engine and consumed by the Behavioral Intelligence and Score Fusion modules.

---

## AI Engine Pipeline

```text
Candidate Dataset
        ↓
Candidate Processing
        ↓
Embeddings
        ↓
FAISS Retrieval
        ↓
Career Intelligence
        ↓
Retrieval Expertise Detection
        ↓
Semantic Ranking
        ↓
Explainability
        ↓
AI Engine Output
```

---

## Output Schema

Each candidate returned by the AI Engine should contain:

```json
{
  "candidate_id": "string",

  "semantic_score": 0.0,
  "career_score": 0.0,
  "retrieval_expertise_score": 0.0,

  "matched_skills": [
    "python",
    "machine learning",
    "faiss"
  ],

  "candidate_reason": "string",

  "final_score": 0.0
}
```

---

## Field Definitions

| Field                     | Description                                     |
| ------------------------- | ----------------------------------------------- |
| candidate_id              | Unique candidate identifier                     |
| semantic_score            | JD ↔ Candidate semantic similarity score        |
| career_score              | Career progression and role-fit score           |
| retrieval_expertise_score | Search, retrieval, ranking expertise score      |
| matched_skills            | Skills matched between JD and candidate profile |
| candidate_reason          | Human-readable explanation for ranking          |
| final_score               | AI ranking score before behavioral fusion       |

---

## Example Output

```json
{
  "candidate_id": "CAND_0030953",

  "semantic_score": 0.91,
  "career_score": 0.84,
  "retrieval_expertise_score": 0.88,

  "matched_skills": [
    "python",
    "machine learning",
    "nlp",
    "faiss",
    "elasticsearch",
    "search",
    "ranking",
    "recommendation"
  ],

  "candidate_reason": "7.8 years of relevant experience. Currently working as Search Engineer at Nykaa. Matched 8 JD skills including python, machine learning, search, faiss and ranking. Hands-on experience with FAISS, ELASTICSEARCH, QDRANT and WEAVIATE. Strong retrieval and ranking expertise.",

  "final_score": 0.7567
}
```

---

## Integration with Behavioral Engine

The Behavioral Engine enriches the AI output with:

```json
{
  "availability_score": 0.0,
  "recruitability_score": 0.0,
  "credibility_score": 0.0,
  "engagement_score": 0.0,
  "trap_penalty": 0.0
}
```

---

## Final Fusion Contract

```json
{
  "candidate_id": "CAND_0030953",

  "semantic_score": 0.91,
  "career_score": 0.84,
  "retrieval_expertise_score": 0.88,

  "availability_score": 0.73,
  "recruitability_score": 0.81,
  "credibility_score": 0.92,
  "engagement_score": 0.77,

  "trap_penalty": 0.00,

  "final_score": 0.82
}
```

---

## Final Deliverables Produced by AI Engine

* ranked_candidates.csv
* candidate_embeddings.npy
* candidate_index.faiss
* candidate_index_ids.json
* candidate_reason explanations
* Top-K ranked candidate list
* AI ranking scores
* JD skill match analysis
