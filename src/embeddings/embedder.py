"""Embedding engine for JD and candidate texts."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Sequence

import numpy as np

from utils.config import EmbeddingConfig

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class EmbeddingEngine:
    """Generate normalized embeddings with GPU-aware batching and fallbacks."""

    config: EmbeddingConfig = field(default_factory=EmbeddingConfig)
    force_fallback: bool = field(default=False)
    _backend: str = field(init=False, default="unknown")
    _model: object | None = field(init=False, default=None)
    _tokenizer: object | None = field(init=False, default=None)
    _vectorizer: object | None = field(init=False, default=None)
    _device: str = field(init=False, default="cpu")

    def __post_init__(self) -> None:
        self._initialize_backend()

    def _initialize_backend(self) -> None:
        try:
            # Try SentenceTransformers with the preferred BAAI model name
            from sentence_transformers import SentenceTransformer  # type: ignore
            import torch

            self._device = "cuda" if self.config.use_gpu_if_available and torch.cuda.is_available() else "cpu"
            self._model = SentenceTransformer(self.config.primary_model_name, device=self._device)
            self._backend = "sentence_transformers"
            logger.info("Loaded SentenceTransformer backend on %s", self._device)
            return
        except Exception as exc:
            logger.warning("SentenceTransformer backend unavailable: %s", exc)

        try:
            from transformers import AutoModel, AutoTokenizer  # type: ignore
            import torch

            self._device = "cuda" if self.config.use_gpu_if_available and torch.cuda.is_available() else "cpu"
            self._tokenizer = AutoTokenizer.from_pretrained(self.config.primary_model_name)
            self._model = AutoModel.from_pretrained(self.config.primary_model_name).to(self._device)
            self._backend = "transformers"
            logger.info("Loaded Transformers backend on %s", self._device)
            return
        except Exception as exc:
            logger.warning("Transformers backend unavailable: %s", exc)

        from sklearn.feature_extraction.text import HashingVectorizer

        self._vectorizer = HashingVectorizer(
            n_features=2 ** 18,
            alternate_sign=False,
            norm=None,
            lowercase=True,
            ngram_range=(1, 2),
        )
        self._backend = "hashing"
        logger.info("Loaded HashingVectorizer fallback backend")

    def save_embeddings(self, embeddings: np.ndarray, path: str | Path) -> None:
        """Persist embeddings as a numpy .npy file to the given path."""

        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        np.save(path, embeddings)
        logger.info("Saved embeddings to %s", path)

    def encode_texts(self, texts: Sequence[str], batch_size: Optional[int] = None) -> np.ndarray:
        """Encode texts into normalized dense vectors."""

        batch_size = batch_size or self.config.batch_size
        cleaned_texts = [text.strip() if text else "" for text in texts]
        if not cleaned_texts:
            return np.zeros((0, 1), dtype=np.float32)

        if self._backend == "sentence_transformers":
            return self._encode_with_sentence_transformers(cleaned_texts, batch_size)

        if self._backend == "transformers":
            return self._encode_with_transformers(cleaned_texts, batch_size)

        return self._encode_with_hashing(cleaned_texts)

    def encode_single(self, text: str) -> np.ndarray:
        """Encode a single string and return a 1D vector."""

        return self.encode_texts([text], batch_size=1)[0]

    def _encode_with_transformers(self, texts: Sequence[str], batch_size: int) -> np.ndarray:
        import torch

        all_embeddings = []
        self._model.eval()  # type: ignore[union-attr]
        total_batches = max(1, (len(texts) + batch_size - 1) // batch_size)
        for batch_index, start in enumerate(range(0, len(texts), batch_size), start=1):
            batch = list(texts[start : start + batch_size])
            encoded = self._tokenizer(  # type: ignore[union-attr]
                batch,
                padding=True,
                truncation=True,
                max_length=self.config.max_length,
                return_tensors="pt",
            )
            encoded = {key: value.to(self._device) for key, value in encoded.items()}
            with torch.no_grad():
                outputs = self._model(**encoded)  # type: ignore[operator]
                token_embeddings = outputs.last_hidden_state
                attention_mask = encoded["attention_mask"].unsqueeze(-1)
                masked_embeddings = token_embeddings * attention_mask
                summed = masked_embeddings.sum(dim=1)
                counts = attention_mask.sum(dim=1).clamp(min=1)
                batch_embeddings = summed / counts
                batch_embeddings = batch_embeddings.detach().cpu().numpy().astype(np.float32)
                if self.config.normalize:
                    norms = np.linalg.norm(batch_embeddings, axis=1, keepdims=True)
                    norms[norms == 0] = 1.0
                    batch_embeddings = batch_embeddings / norms
            all_embeddings.append(batch_embeddings)
            if batch_index == 1 or batch_index % 10 == 0 or batch_index == total_batches:
                logger.info("Encoded embedding batch %s/%s", batch_index, total_batches)
        return np.vstack(all_embeddings)

    def _encode_with_sentence_transformers(self, texts: Sequence[str], batch_size: int) -> np.ndarray:
        all_embeddings = []
        total_batches = max(1, (len(texts) + batch_size - 1) // batch_size)
        for batch_index, start in enumerate(range(0, len(texts), batch_size), start=1):
            batch = list(texts[start : start + batch_size])
            embeddings = self._model.encode(  # type: ignore[union-attr]
                batch,
                batch_size=batch_size,
                convert_to_numpy=True,
                normalize_embeddings=self.config.normalize,
                show_progress_bar=False,
            )
            all_embeddings.append(np.asarray(embeddings, dtype=np.float32))
            if batch_index == 1 or batch_index % 10 == 0 or batch_index == total_batches:
                logger.info("Encoded embedding batch %s/%s", batch_index, total_batches)
        return np.vstack(all_embeddings)

    def _encode_with_hashing(self, texts: Sequence[str]) -> np.ndarray:
        matrix = self._vectorizer.transform(texts)  # type: ignore[union-attr]
        embeddings = matrix.astype(np.float32).toarray()
        if self.config.normalize:
            norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
            norms[norms == 0] = 1.0
            embeddings = embeddings / norms
        return embeddings.astype(np.float32)
