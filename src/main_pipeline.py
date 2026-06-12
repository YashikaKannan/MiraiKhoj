"""End-to-end MiraiKhoj pipeline for candidate discovery and ranking."""

from __future__ import annotations

import argparse
import json
import logging
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Dict, List

import numpy as np

from behavior.signal_engine import BehavioralSignalEngine
from career.career_analyzer import CareerAnalyzer
from career.retrieval_expertise import RetrievalExpertiseDetector
from data.loader import load_candidates
from data.preprocess import clean_candidate_text
from embeddings.embedder import EmbeddingEngine
from explainability.explainer import CandidateExplainer
from jd.jd_parser import JDParser
from ranking.ai_ranker import CandidateScoreBundle, FinalRanker, HoneypotDetector
from ranking.semantic_ranker import SemanticRanker
from retrieval.faiss_builder import FaissIndexBuilder
from retrieval.retriever import FaissRetriever
from utils.config import PipelineConfig

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s - %(message)s")
logger = logging.getLogger(__name__)


@dataclass(slots=True)
class MiraiKhojPipeline:
    """Orchestrate the full candidate discovery workflow."""

    config: PipelineConfig = field(default_factory=PipelineConfig)

    def __post_init__(self) -> None:
        self.embedding_engine = EmbeddingEngine(self.config.embedding)
        self.jd_parser = JDParser()
        self.career_analyzer = CareerAnalyzer()
        self.retrieval_expertise_detector = RetrievalExpertiseDetector()
        self.behavior_engine = BehavioralSignalEngine()
        self.honeypot_detector = HoneypotDetector()
        self.semantic_ranker = SemanticRanker()
        self.final_ranker = FinalRanker(self.config.weights)
        self.explainer = CandidateExplainer()
        self.faiss_builder = FaissIndexBuilder()

    def process_candidates(self, candidates_path: str | Path) -> Dict[str, object]:
        """Load, normalize, and embed candidates before building the retrieval index."""

        output_dir = self.config.paths.output_dir
        output_dir.mkdir(parents=True, exist_ok=True)
        df = load_candidates(candidates_path)
        if df.empty:
            raise ValueError("No valid candidate records were found.")

        df["candidate_text"] = df["candidate_text"].fillna("").map(clean_candidate_text)
        df.to_parquet(self.config.paths.processed_candidates, index=False)

        candidate_texts = df["candidate_text"].astype(str).tolist()
        embeddings = self.embedding_engine.encode_texts(candidate_texts)
        np.save(self.config.paths.candidate_embeddings, embeddings)

        candidate_ids = df["candidate_id"].astype(str).tolist()
        bundle = self.faiss_builder.build(embeddings, candidate_ids)
        self.faiss_builder.save(bundle, self.config.paths.candidate_index, self.config.paths.candidate_index_ids)
        return {"dataframe": df, "embeddings": embeddings, "bundle": bundle}

    def rank(self, candidates_path: str | Path, job_description: str, top_k: int | None = None) -> List[Dict[str, object]]:
        """Run the full retrieval and ranking pipeline."""

        top_k = top_k or self.config.final_top_k
        processing = self.process_candidates(candidates_path)
        df = processing["dataframe"]
        embeddings = processing["embeddings"]

        parsed_jd = self.jd_parser.parse(job_description)
        jd_embedding = self.embedding_engine.encode_single(job_description)

        retriever = FaissRetriever.from_files(self.config.paths.candidate_index, self.config.paths.candidate_index_ids)
        retrieval_hits = retriever.search(jd_embedding, top_k=min(self.config.retrieval_top_k, len(df)))

        candidate_lookup = df.set_index("candidate_id").to_dict(orient="index")
        candidate_embeddings = {candidate_id: embeddings[idx] for idx, candidate_id in enumerate(df["candidate_id"].astype(str).tolist())}

        score_bundles: List[CandidateScoreBundle] = []
        for hit in retrieval_hits:
            candidate = candidate_lookup.get(hit.candidate_id)
            if not candidate:
                continue

            candidate_payload = dict(candidate)
            candidate_payload["parsed_jd"] = parsed_jd.to_dict()

            semantic_score = self.semantic_ranker.score(jd_embedding, candidate_embeddings[hit.candidate_id])
            career_analysis = self.career_analyzer.analyze(candidate_payload)
            retrieval_analysis = self.retrieval_expertise_detector.analyze(candidate_payload)
            behavior_analysis = self.behavior_engine.analyze(candidate_payload)
            trap_penalty = self.honeypot_detector.detect(candidate_payload)

            evidence = career_analysis.evidence + retrieval_analysis.technology_hits + retrieval_analysis.evaluation_hits + behavior_analysis.evidence
            score_bundles.append(
                CandidateScoreBundle(
                    candidate_id=hit.candidate_id,
                    semantic_score=semantic_score,
                    career_score=career_analysis.career_score,
                    retrieval_expertise_score=retrieval_analysis.retrieval_expertise_score,
                    behavioral_score=behavior_analysis.behavioral_score,
                    credibility_score=behavior_analysis.credibility_score,
                    logistics_score=behavior_analysis.logistics_score,
                    trap_penalty=trap_penalty,
                    evidence=evidence,
                    candidate_payload=candidate_payload,
                )
            )

        ranked = self.final_ranker.rank(score_bundles)[:top_k]
        output: List[Dict[str, object]] = []
        for ranked_candidate in ranked:
            explanation = self.explainer.explain(ranked_candidate)
            output.append(
                {
                    "candidate_id": ranked_candidate.candidate_id,
                    "final_score": ranked_candidate.final_score,
                    "semantic_score": ranked_candidate.semantic_score,
                    "career_score": ranked_candidate.career_score,
                    "retrieval_expertise_score": ranked_candidate.retrieval_expertise_score,
                    "behavioral_score": ranked_candidate.behavioral_score,
                    "credibility_score": ranked_candidate.credibility_score,
                    "logistics_score": ranked_candidate.logistics_score,
                    "trap_penalty": ranked_candidate.trap_penalty,
                    "candidate_reason": explanation,
                    "candidate": ranked_candidate.candidate_payload,
                }
            )
        return output


def build_argument_parser() -> argparse.ArgumentParser:
    """Create the command-line interface for the pipeline."""

    parser = argparse.ArgumentParser(description="MiraiKhoj candidate ranking pipeline")
    parser.add_argument("--candidates", required=True, help="Path to candidates.jsonl")
    parser.add_argument("--jd", required=True, help="Path to a text file containing the job description")
    parser.add_argument("--output", default="outputs/ranked_candidates.json", help="Path to write the ranking JSON")
    parser.add_argument("--top-k", type=int, default=20, help="Number of final candidates to return")
    return parser


def main() -> None:
    """Run the pipeline from the command line."""

    parser = build_argument_parser()
    args = parser.parse_args()

    candidates_path = Path(args.candidates)
    jd_path = Path(args.jd)
    jd_text = jd_path.read_text(encoding="utf-8")

    pipeline = MiraiKhojPipeline()
    ranked = pipeline.rank(candidates_path, jd_text, top_k=args.top_k)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(ranked, indent=2, ensure_ascii=False), encoding="utf-8")
    logger.info("Wrote %s ranked candidates to %s", len(ranked), output_path)


if __name__ == "__main__":
    main()
