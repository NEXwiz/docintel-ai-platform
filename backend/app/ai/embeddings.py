import os
import time
import google.generativeai as genai
from typing import List

# Max texts per API call to avoid payload limits
_BATCH_SIZE = 100
# Retry settings
_MAX_RETRIES = 3
_INITIAL_BACKOFF = 2  # seconds


class EmbeddingService:
    def __init__(self):
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Embed a list of texts using Gemini text-embedding-004.

        Handles:
          - Batch splitting (max 100 texts per API call)
          - Retry with exponential backoff on failure
          - Single vs multi text normalization
        """
        if not texts:
            return []

        all_embeddings = []

        # Process in batches
        for i in range(0, len(texts), _BATCH_SIZE):
            batch = texts[i:i + _BATCH_SIZE]
            batch_embeddings = self._embed_batch_with_retry(batch)
            all_embeddings.extend(batch_embeddings)

        return all_embeddings

    def _embed_batch_with_retry(self, texts: List[str]) -> List[List[float]]:
        """Embed a single batch with retry logic."""
        last_error = None

        for attempt in range(_MAX_RETRIES):
            try:
                result = genai.embed_content(
                    model="models/gemini-embedding-001",
                    content=texts
                )
                embeddings = result["embedding"]

                # If single text was passed, Gemini returns a flat list
                if embeddings and not isinstance(embeddings[0], list):
                    embeddings = [embeddings]

                return embeddings

            except Exception as e:
                last_error = e
                if attempt < _MAX_RETRIES - 1:
                    backoff = _INITIAL_BACKOFF * (2 ** attempt)
                    print(f"[EMBEDDING] Retry {attempt + 1}/{_MAX_RETRIES} after {backoff}s: {e}")
                    time.sleep(backoff)

        raise RuntimeError(
            f"Embedding failed after {_MAX_RETRIES} retries: {last_error}"
        )