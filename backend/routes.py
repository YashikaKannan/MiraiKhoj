from fastapi import APIRouter, HTTPException

from backend.schemas import RankRequest
from backend.services import rank_candidates

router = APIRouter()


# Rank Candidates
@router.post("/rank")
def rank(request: RankRequest):

    results = rank_candidates(
        jd_text=request.jd_text,
        top_k=request.top_k,
    )

    return {
        "top_candidates": results
    }


# ------------------------
# Analytics
# ------------------------
@router.get("/analytics")
def analytics():

    return {
        "total_candidates": 6093,
        "ranked_candidates": 100,
        "average_score": 0.76,
        "average_trap_penalty": 0.02,
        "honeypot_risk_rate": 1.5,

        "top_skills": [
            {"skill": "Python", "count": 95},
            {"skill": "Machine Learning", "count": 91},
            {"skill": "FAISS", "count": 73},
            {"skill": "NLP", "count": 68},
            {"skill": "Elasticsearch", "count": 63},
        ],

        "score_distribution": [
            {"bucket": "0-0.2", "count": 5},
            {"bucket": "0.2-0.4", "count": 16},
            {"bucket": "0.4-0.6", "count": 42},
            {"bucket": "0.6-0.8", "count": 24},
            {"bucket": "0.8-1.0", "count": 13},
        ],

        "behavior_distribution": [
            {"signal": "Availability", "value": 82},
            {"signal": "Recruitability", "value": 77},
            {"signal": "Engagement", "value": 74},
            {"signal": "Credibility", "value": 91},
        ]
    }


# ------------------------
# Candidate Details
# ------------------------
@router.get("/candidate/{candidate_id}")
def get_candidate(candidate_id: str):

    raise HTTPException(
        status_code=404,
        detail="Candidate details endpoint not implemented yet."
    )