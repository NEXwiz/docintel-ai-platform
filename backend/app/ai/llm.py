import os
#from openai import OpenAI
import google.generativeai as genai
from typing import Generator, List

class LLMService:
    def __init__(self):
        genai.configure(
            api_key = os.getenv("GEMINI_API_KEY")
        )
        self.model = genai.GenerativeModel("gemini-2.5-flash")

    def _build_prompt(self, query: str, context: str, chat_history: List[dict] | None = None) -> str:
        """Build the full prompt with optional conversation history."""
        history_block = ""
        if chat_history:
            turns = []
            for msg in chat_history:
                role = "User" if msg["role"] == "user" else "Assistant"
                turns.append(f"{role}: {msg['content']}")
            history_block = "Conversation so far:\n" + "\n".join(turns) + "\n\n"

        return f"""You are a helpful assistant.
Answer the question based on the context below.
If the answer is not present in the context, say "I don't know".
Use the conversation history to understand follow-up questions.

{history_block}Context:
{context}

Question:
{query}
"""

    def generate_answer(self, query: str, context: str, chat_history: List[dict] | None = None) -> str:
        prompt = self._build_prompt(query, context, chat_history)
        response = self.model.generate_content(prompt)
        return response.text.strip()

    def generate_answer_stream(self, query: str, context: str, chat_history: List[dict] | None = None) -> Generator[str, None, None]:
        """Stream answer token-by-token using Gemini's streaming mode."""
        prompt = self._build_prompt(query, context, chat_history)
        response = self.model.generate_content(prompt, stream=True)
        for chunk in response:
            if chunk.text:
                yield chunk.text