import os
#from openai import OpenAI
import google.generativeai as genai

class LLMService:
    def __init__(self):
        genai.configure(
            api_key = os.getenv("GEMINI_API_KEY")
        )
        self.model = genai.GenerativeModel("gemini-3-flash-preview")
    
    def generate_answer(self, query: str, context: str) -> str:
        prompt = f"""
You are a helpful assistant.
Answer the question strictly based on the context below.
If the answer is not present in the context, say "I don't know".

Context:
{context}

Question:
{query}
"""
        response = self.model.generate_content(prompt)

        return response.text.strip()