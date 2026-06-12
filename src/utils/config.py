"""Configuration, defaults, and shared lexicons for MiraiKhoj."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Sequence, Set

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA_DIR = PROJECT_ROOT / "data"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "outputs"

PRIMARY_EMBEDDING_MODEL = "BAAI/bge-large-en-v1.5"
FALLBACK_EMBEDDING_MODEL = "intfloat/e5-large-v2"

SKILL_LEXICON: Set[str] = {
    "python",
    "sql",
    "pytorch",
    "tensorflow",
    "faiss",
    "elasticsearch",
    "opensearch",
    "qdrant",
    "milvus",
    "pinecone",
    "weaviate",
    "retrieval",
    "ranking",
    "recommendation",
    "search",
    "matching",
    "nlp",
    "llm",
    "vector database",
    "vector search",
    "machine learning",
    "deep learning",
    "information retrieval",
    "learning to rank",
    "ndcg",
    "mrr",
    "map",
    "ab testing",
    "feature engineering",
    "candidate ranking",
    "semantic search",
    "embedding",
    "dense retrieval",
    "sparse retrieval",
    "hnsw",
}

ROLE_KEYWORDS: Dict[str, float] = {
    "ai engineer": 1.0,
    "ml engineer": 1.0,
    "machine learning engineer": 1.0,
    "search engineer": 1.0,
    "information retrieval engineer": 1.0,
    "recommendation engineer": 0.95,
    "nlp engineer": 0.9,
    "applied scientist": 0.85,
    "data scientist": 0.75,
    "software engineer": 0.6,
}

RETRIEVAL_TECH_TERMS: Set[str] = {
    "faiss",
    "elasticsearch",
    "opensearch",
    "qdrant",
    "milvus",
    "pinecone",
    "weaviate",
    "lucene",
    "solr",
    "vector search",
    "dense retrieval",
    "sparse retrieval",
    "hybrid search",
    "bm25",
    "hnsw",
    "ann",
}

RETRIEVAL_EVAL_TERMS: Set[str] = {
    "ndcg",
    "mrr",
    "map",
    "precision@k",
    "recall@k",
    "learning to rank",
    "ltr",
    "ab testing",
    "offline evaluation",
    "online evaluation",
}

COMPANY_QUALITY_TERMS: Dict[str, float] = {
    "product": 1.0,
    "saas": 0.95,
    "startup": 0.9,
    "ai": 0.95,
    "search": 0.9,
    "marketplace": 0.9,
    "platform": 0.85,
    "consumer": 0.8,
    "fintech": 0.8,
    "ecommerce": 0.8,
}

CONSULTING_TERMS: Set[str] = {
    "consulting",
    "services",
    "service based",
    "staffing",
    "outsourcing",
    "implementation partner",
}

SENIORITY_ORDER: Sequence[str] = (
    "intern",
    "junior",
    "associate",
    "engineer",
    "senior engineer",
    "staff engineer",
    "lead engineer",
    "principal engineer",
    "architect",
    "manager",
    "director",
    "vp",
    "head",
)

LOCATION_TERMS: Set[str] = {
    "remote",
    "hybrid",
    "onsite",
    "bengaluru",
    "bangalore",
    "hyderabad",
    "chennai",
    "pune",
    "mumbai",
    "delhi",
    "noida",
    "gurgaon",
    "india",
    "us",
    "uk",
    "europe",
    "singapore",
}

EVALUATION_METRICS: Set[str] = {
    "accuracy",
    "precision",
    "recall",
    "f1",
    "mrr",
    "map",
    "ndcg",
    "auc",
    "ab testing",
    "online metrics",
    "offline metrics",
}


@dataclass(slots=True)
class PathConfig:
    """Common file system locations used by the pipeline."""

    data_dir: Path = DEFAULT_DATA_DIR
    output_dir: Path = DEFAULT_OUTPUT_DIR
    processed_candidates: Path = DEFAULT_OUTPUT_DIR / "processed_candidates.parquet"
    candidate_embeddings: Path = DEFAULT_OUTPUT_DIR / "candidate_embeddings.npy"
    candidate_index: Path = DEFAULT_OUTPUT_DIR / "candidate_index.faiss"
    candidate_index_ids: Path = DEFAULT_OUTPUT_DIR / "candidate_index_ids.json"


@dataclass(slots=True)
class EmbeddingConfig:
    """Embedding model and batching settings."""

    primary_model_name: str = PRIMARY_EMBEDDING_MODEL
    fallback_model_name: str = FALLBACK_EMBEDDING_MODEL
    batch_size: int = 64
    max_length: int = 512
    normalize: bool = True
    use_gpu_if_available: bool = True


@dataclass(slots=True)
class RankingWeights:
    """Fusion weights for the final score."""

    semantic: float = 0.45
    career: float = 0.20
    retrieval_expertise: float = 0.15
    behavioral: float = 0.10
    credibility: float = 0.05
    logistics: float = 0.05


@dataclass(slots=True)
class PipelineConfig:
    """Top-level configuration for MiraiKhoj."""

    paths: PathConfig = field(default_factory=PathConfig)
    embedding: EmbeddingConfig = field(default_factory=EmbeddingConfig)
    weights: RankingWeights = field(default_factory=RankingWeights)
    retrieval_top_k: int = 500
    final_top_k: int = 20
