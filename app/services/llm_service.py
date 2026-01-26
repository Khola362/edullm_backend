import httpx
import asyncio
from typing import AsyncGenerator
from app.core.config import settings


class LLMService:
    def __init__(self):
        # ✅ MATCH config.py EXACTLY
        self.render_url = settings.punjab_api_url
        self.api_key = settings.punjab_api_key

        if self.api_key:
            print("✅ Punjab Text Book API configured")
            print(f"   URL: {self.render_url}")
            print(f"   Key: {self.api_key[:3]}***")
        else:
            print("❌ Punjab Text Book API key not configured")


    async def generate_response(
        self,
        messages: list,
        session_id: str = None,
        query: str = None,
        stream: bool = True
    ) -> AsyncGenerator[str, None]:
        """Generate response using Punjab Text Book API"""

        # Extract user query
        user_query = query or ""
        if not user_query:
            for msg in reversed(messages):
                if msg.get("sender") == "user":
                    user_query = msg.get("content", "")
                    break

        if not user_query:
            yield "Please ask a question related to Punjab textbooks."
            return

        if not self.api_key:
            yield "Punjab Textbook service is not configured."
            return

        try:
            url = f"{self.render_url}/ask"
            headers = {
                "Content-Type": "application/json",
                "x-api-key": self.api_key
            }
            payload = {
                "question": user_query,
                "k": 3
            }

            print(f"\n📤 [Punjab API] Question: {user_query}")
            print(f"   URL: {url}")

            timeout = httpx.Timeout(30.0, connect=10.0)

            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(
                    url,
                    json=payload,
                    headers=headers
                )

            print(f"   Status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()

                answer = data.get("answer", "").strip()
                reference = data.get("reference", "").strip()

                if not answer:
                    formatted = (
                        "I couldn't find a clear answer in the Punjab "
                        "Textbook Board content for this question."
                    )
                else:
                    formatted = answer
                    if reference:
                        formatted += f"\n\n📚 *{reference}*"
                    formatted += (
                        "\n\n💡 *Answer based on Punjab Textbook Board content*"
                    )

                if stream:
                    for word in formatted.split():
                        yield word + " "
                        await asyncio.sleep(0.02)
                else:
                    yield formatted

            elif response.status_code == 401:
                yield "🔐 Invalid Punjab API key. Please check Render environment variables."

            else:
                try:
                    error_detail = response.json()
                except Exception:
                    error_detail = response.text[:200]

                yield f"⚠️ Punjab API error ({response.status_code}): {error_detail}"

        except httpx.RequestError as e:
            print(f"❌ Network error: {e}")
            yield "🔌 Unable to connect to Punjab Textbook service."

        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            yield "⚠️ An unexpected error occurred while processing your request."


# ✅ SINGLETON INSTANCE (SAFE)
# llm_service = LLMService()
