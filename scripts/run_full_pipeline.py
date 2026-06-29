from __future__ import annotations

import json
import logging
import time
from pathlib import Path
from typing import List

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT / "src"))

import numpy as np
import pandas as pd
from docx import Document

from llm.gemini_reasoner import GeminiReasoner
from career.career_analyzer import CareerAnalyzer
from career.retrieval_expertise import RetrievalExpertiseDetector
from behavior.signal_engine import BehavioralSignalEngine
from explainability.explainer import CandidateExplainer
from ranking.ai_ranker import CandidateScoreBundle, FinalRanker, TrapDetector
from ranking.semantic_ranker import SemanticRanker
from retrieval.retriever import FaissRetriever
from embeddings.embedder import EmbeddingEngine
from utils.config import PathConfig, PipelineConfig, EmbeddingConfig
from jd.jd_parser import JDParser

# USE_GEMINI = False

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s - %(message)s")
logger = logging.getLogger(__name__)


def run(jd_text: str, top_k: int = 100) -> dict:
    cfg = PathConfig()
    pipeline_cfg = PipelineConfig()
    jd_parser = JDParser()
    parsed_jd = jd_parser.parse(jd_text)

    df = pd.read_csv("data/processed/processed_candidates.csv")
    
    emb = np.load(cfg.candidate_embeddings, mmap_mode="r")
    print("Candidates:", len(df))
    print("Embeddings:", emb.shape[0])
    retriever = FaissRetriever.from_files(cfg.candidate_index, cfg.candidate_index_ids)

    engine = EmbeddingEngine(EmbeddingConfig())
    jd_emb = engine.encode_single(jd_text)

    hits = retriever.search(jd_emb, top_k=min(pipeline_cfg.retrieval_top_k, len(df)))

    candidate_lookup = df.set_index("candidate_id").to_dict(orient="index")
    candidate_embeddings = {cid: emb[idx] for idx, cid in enumerate(df["candidate_id"].astype(str).tolist())}
    filtered_hits = []

    for hit in hits:
        candidate = candidate_lookup.get(hit.candidate_id)

        if candidate is None:
            continue

        title = str(candidate.get("current_title", "")).lower()

        # keep if title matches any target role
        if any(role in title for role in parsed_jd.target_roles):
            filtered_hits.append(hit)
            continue

        # also keep generic engineering titles
        if any(x in title for x in [
            "software engineer",
            "backend engineer",
            "full stack engineer",
            "platform engineer",
            "engineer",
            "developer",
        ]):
           filtered_hits.append(hit)

    hits = filtered_hits

    print("=" * 100)

    for h in hits[:20]:
        c = candidate_lookup[h.candidate_id]
        print(
            h.candidate_id,
            c["current_title"],
            c["current_company"],
            h.score,
        )

    print("=" * 100)
    

    career = CareerAnalyzer()
    retrieval_exp = RetrievalExpertiseDetector()
    behavior = BehavioralSignalEngine()
    trap_detector = TrapDetector()    
    semantic = SemanticRanker()
    final_ranker = FinalRanker()
    explainer = CandidateExplainer()
    try:
        gemini = GeminiReasoner() if USE_GEMINI else None
    except Exception:
        gemini = None

    bundles: List[CandidateScoreBundle] = []
    for hit in hits:
        candidate = candidate_lookup.get(hit.candidate_id)
        if not candidate:
            continue
        cand_payload = dict(candidate)
        # print("=" * 80)
        # print(cand_payload)
        # break
        sem = semantic.score(jd_emb, candidate_embeddings[hit.candidate_id])
        matched_skills = []

        for skill in parsed_jd.required_skills:
            if skill.lower() in cand_payload["candidate_text"].lower():
                matched_skills.append(skill)

        skill_score = semantic.skill_match_score(
            parsed_jd.required_skills,
            cand_payload["candidate_text"]
        )
        career_analysis = career.analyze(cand_payload, parsed_jd.target_roles,)
        retr_analysis = retrieval_exp.analyze(cand_payload)
        beh = behavior.analyze(cand_payload)
        
        trap_result = trap_detector.detect(cand_payload)
        trap_penalty = trap_result["trap_penalty"] / 40.0
        
        print(
            hit.candidate_id,
            sem,
            career_analysis.career_score,
            retr_analysis.retrieval_expertise_score,
            beh.behavioral_score,
            beh.credibility_score,
            beh.logistics_score,
            trap_result
        )
        bundles.append(
            CandidateScoreBundle(
                candidate_id=hit.candidate_id,
                semantic_score=(
                    0.65 * sem +
                    0.35 * skill_score
                ),
                career_score=career_analysis.career_score,
                retrieval_expertise_score=retr_analysis.retrieval_expertise_score,
                behavioral_score=beh.behavioral_score,
                credibility_score=beh.credibility_score,
                logistics_score=beh.logistics_score,
                trap_penalty=trap_penalty,
                evidence=career_analysis.evidence + retr_analysis.technology_hits + retr_analysis.evaluation_hits + beh.evidence,
                candidate_payload=cand_payload,
                matched_skills=matched_skills,

            )
        )

    # ranked = final_ranker.rank(bundles)[:top_k]
    ranked = final_ranker.rank(bundles)

    
    # ----------------------------
    # LLM Re-ranking (Batch Mode)
    # ----------------------------
    # if USE_GEMINI:
    #     top_candidates = ranked[:20]

    #     batch_size = 5

    #     for i in range(0, len(top_candidates), batch_size):

    #         batch = top_candidates[i:i + batch_size]

    #         payload = []

    #         for c in batch:
    #             payload.append({
    #                 "candidate_id": c.candidate_id,
    #                 "current_title": c.candidate_payload.get("current_title"),
    #                 "current_company": c.candidate_payload.get("current_company"),
    #                 "years_of_experience": c.candidate_payload.get("years_of_experience"),
    #                 "candidate_text": c.candidate_payload.get("candidate_text"),
    #                 "current_score": round(c.final_score, 3)
    #             })

    #         if gemini is not None:
    #             results = gemini.evaluate_batch(jd_text, payload)
    #         else:
    #             results = [
    #                 {
    #                     "candidate_id": c["candidate_id"],
    #                     "fit_score": int(c["current_score"] * 100),
    #                     "reason": "Offline ranking used.",
    #                 }
    #                 for c in payload
    #             ]

    #         result_lookup = {
    #             r["candidate_id"]: r
    #             for r in results
    #         }

    #         for c in batch:

    #             if c.candidate_id not in result_lookup:
    #                 continue

    #             llm = result_lookup[c.candidate_id]

    #             llm_score = llm["fit_score"] / 100

    #             recommendation_bonus = {
    #                 "Strong Yes": 0.05,
    #                 "Yes": 0.03,
    #                 "Maybe": 0.00,
    #                 "No": -0.03,
    #                 "Strong No": -0.05,
    #             }

    #             bonus = recommendation_bonus.get(
    #                 llm.get("interview_recommendation", "Maybe"),
    #                 0.0,
    #             )

    #             c.final_score = min(
    #                 1.0,
    #                 0.80 * c.final_score +
    #                 0.20 * llm_score +
    #                 bonus,
    #             )
    #             if "reason" in llm:
    #                 c.candidate_payload["llm_reason"] = llm["reason"]
    #             if "strengths" in llm:
    #                 c.candidate_payload["strengths"] = llm.get("strengths", [])
    #             if "risks" in llm:
    #                 c.candidate_payload["risks"] = llm.get("risks", [])

            

    #         # Final sort
    #         ranked = sorted(
    #             top_candidates + ranked[20:],
    #             key=lambda x: x.final_score,
    #             reverse=True,
    #         )[:top_k]
    # except Exception as e:
    #     logger.warning("Gemini unavailable. Using local ranking only: %s", e)


    rows = []
    for rank, r in enumerate(ranked, start=1):
        reason = explainer.explain(r)
        rows.append({
            "candidate_id": r.candidate_id,
            "rank": rank,
            "score": round(r.final_score, 3),
            "reasoning": reason,
        })

    out = pd.DataFrame.from_records(rows)
    # out_path = Path(cfg.ranked_candidates_csv)
    out_path = Path("data/outputs/final_submission.csv")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    print(ranked[0].candidate_payload)
    print(ranked[0].evidence)
    out.to_csv(out_path, index=False)

    report = {
        "total_ranked": len(out),
        "output_file": str(out_path),
    }
    # minimal report
    rpt_path = cfg.data_dir / "docs" / "RANKING_REPORT.md"
    rpt_path.parent.mkdir(parents=True, exist_ok=True)
    rpt_md = ["# Ranking Report\n\n", f"- Total ranked: {report['total_ranked']}\n", f"- Output: {report['output_file']}\n"]
    rpt_path.write_text("".join(rpt_md), encoding="utf-8")
    logger.info("Wrote ranked candidates to %s", out_path)
    return report


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--jd", required=True, help="Path to a JD text file")
    parser.add_argument("--top-k", type=int, default=100)
    args = parser.parse_args()

    jd_path = Path(args.jd)

    if jd_path.suffix == ".docx":
        doc = Document(jd_path)
        jd_text = "\n".join(p.text for p in doc.paragraphs)
    else:
        jd_text = Path(args.jd).read_text(encoding="utf-8")
    
    parser = JDParser()
    parsed_jd = parser.parse(jd_text)

    print(parsed_jd)

    run(jd_text, top_k=args.top_k)



if __name__ == "__main__":
    main()


