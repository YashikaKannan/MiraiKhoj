# MiraiKhoj — Finding Talent Beyond Keywords

Frontend for the **Redrob Data & AI Challenge** submission. MiraiKhoj turns a job
description into an explainable **Top 100** candidate shortlist with semantic
retrieval, career intelligence, behavioral signals, honeypot detection, and
explainable score fusion — then exports a Redrob-compliant `final_submission.csv`.

> **This repository is frontend only.** No backend, no auth, no database. The UI
> talks to a FastAPI backend if one is reachable and gracefully falls back to
> deterministic mock data so the full demo flow works offline.

---

## Demo flow

```
Open Dashboard
   ↓
Click "Start Ranking"
   ↓
Paste Job Description
   ↓
Click "Rank Candidates"
   ↓
View Top 100 Ranked Candidates
   ↓
Open Candidate Details
   ↓
Inspect Score Breakdown & Trap Penalty
   ↓
Return to Results
   ↓
View Submission Preview
   ↓
Check Validation Status
   ↓
Download final_submission.csv
```

A status badge on the Rank page tells you whether the UI is in
**Backend Mode** (connected to FastAPI) or **Demo Mode** (mock candidates).

---

## Submission format (Redrob)

The downloaded file is named **`final_submission.csv`** with these exact columns,
in this exact order:

```
candidate_id,rank,score,reasoning
```

Rules enforced by the **Validation Status** card before download is enabled:

- Exactly **100 rows** generated
- **Ranks 1–100** present
- **No duplicate** `candidate_id`s
- `score` is **non-increasing** (rank 1 has the highest score)
- `reasoning` is non-empty for every row
- Required columns present and in order

CSV escaping is RFC-4180 compliant (commas, quotes, and newlines inside
`reasoning` are quoted/escaped). UTF-8 encoded.

---

## Pages

| Route | Purpose |
| --- | --- |
| `/` | Dashboard — product framing, KPIs, pipeline diagram. |
| `/rank` | Paste JD → Top 100 table, Submission Preview, Validation, CSV download. |
| `/candidate/$candidateId` | Candidate Details — title, location, experience, reasoning, **Score Breakdown** (semantic, career, retrieval, availability, recruitability, engagement, credibility), trap-penalty warning. |
| `/analytics` | Lightweight: Average Final Score, Honeypot Risk Rate, Top Skills, Score Distribution. |

---

## Backend contract (optional)

When `VITE_API_BASE` is reachable, the frontend calls:

### `POST /rank`
```json
{ "jd_text": "..." }
```
**Response**
```json
{
  "top_candidates": [
    {
      "candidate_id": "CAND_0000001",
      "rank": 1,
      "final_score": 91.2,
      "semantic_score": 88.0,
      "career_score": 84.0,
      "retrieval_score": 90.0,
      "availability_score": 70.0,
      "recruitability_score": 75.0,
      "engagement_score": 80.0,
      "credibility_score": 92.0,
      "trap_penalty": 3.1,
      "reasoning": "Strong semantic alignment with retrieval and ranking experience.",
      "current_title": "Senior Search Engineer",
      "location": "Bengaluru, India",
      "years_of_experience": 6.5,
      "skills": ["Python", "FAISS", "Vector Search"]
    }
  ]
}
```

### `GET /candidate/{id}`
Returns a single candidate with the same shape.

### `GET /analytics`
```json
{
  "total_candidates": 100000,
  "ranked_candidates": 100,
  "average_score": 78.4,
  "average_trap_penalty": 4.2,
  "honeypot_risk_rate": 6.0,
  "top_skills": [{ "skill": "Python", "count": 86 }],
  "score_distribution": [{ "bucket": "70-80", "count": 34 }]
}
```

### Field normalization
The frontend accepts legacy field names from the backend and normalizes them:
- `candidate_reason` → `reasoning`
- `final_score` → also exposed as `score`

If the backend returns fewer than 100 candidates, the frontend pads with mock
entries so the submission CSV always contains exactly 100 rows.

---

## Demo / sandbox mode

If the backend is unreachable within ~2.5s, the UI switches to **Demo Mode** and
serves 100 deterministic mock candidates (seeded RNG). The entire submission
flow — preview, validation, and CSV download — works in this mode, which is what
hackathon judges will see if they run only the frontend.

---

## Run

### Frontend (this repo)
```bash
bun install
bun dev
```
Open the printed URL. Configure backend with:
```bash
VITE_API_BASE=http://localhost:8000 bun dev
```

### Backend (expected, not included here)
The backend team should expose a single command that produces the same CSV the
frontend builds, e.g.:
```bash
python -m miraikhoj.rank --jd jd.txt --out final_submission.csv
```

---

## Tech stack

React 19 · TanStack Start / Router · Vite 7 · Tailwind CSS v4 · shadcn/ui ·
TanStack Query · Recharts · Lucide icons.

---

## Product messaging

- Beyond keyword matching
- Explainable score fusion
- Behavioral intelligence
- Honeypot-aware ranking
- Recruiter-ready shortlist
