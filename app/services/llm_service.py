import httpx
import asyncio
from typing import AsyncGenerator
from app.core.config import settings


class LLMService:
    def __init__(self):
        self.render_url = settings.punjab_api_url
        self.api_key = settings.punjab_api_key

        print("✅ LLMService initialized")
        print(f"   URL: {self.render_url}")
        print(f"   Key: {self.api_key[:3]}***")

    async def generate_response(
        self,
        messages: list,
        session_id: str = None,
        query: str = None,
        stream: bool = True
    ) -> AsyncGenerator[str, None]:

        user_query = query or ""
        if not user_query:
            for msg in reversed(messages):
                if msg.get("sender") == "user":
                    user_query = msg.get("content", "")
                    break

        if not user_query:
            yield "Please ask a Punjab textbook question."
            return

        url = f"{self.render_url}/ask"
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key
        }

        payload = {"question": user_query, "k": 3}

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(url, json=payload, headers=headers)

        if response.status_code != 200:
            yield f"Punjab API error: {response.status_code}"
            return

        data = response.json()
        answer = data.get("answer", "No answer found.")

        if stream:
            for w in answer.split():
                yield w + " "
                await asyncio.sleep(0.02)
        else:
            yield answer


llm_service = LLMService()
