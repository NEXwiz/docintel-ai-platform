import os
import google.generativeai as genai
from typing import List

class EmbeddingService:
    def __init__(self):
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        result = genai.embed_content(
            model="models/text-embedding-004",
            content=texts
        )
        return result["embedding"]