from pydantic import BaseModel


class RankRequest(BaseModel):
    jd_text: str
    top_k: int = 100


class CandidateResponse(BaseModel):
    candidate_id: str
    final_score: float
    rank: int
    candidate_reason: str