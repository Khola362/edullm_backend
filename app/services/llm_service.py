import httpx
import asyncio
import os
from typing import AsyncGenerator
from app.core.config import settings


class LLMService:
    def __init__(self):
        # Priority: ENV > settings
        self.render_url = os.getenv("RENDER_URL", settings.render_url)
        self.api_key = os.getenv("RENDER_API_KEY", settings.render_api_key)

        if self.api_key and self.api_key != "YOUR_API_KEY_HERE":
            print("✅ Render Textbook API configured")
            print(f"   Key: {self.api_key[:3]}***")
            print(f"   URL: {self.render_url}")
        else:
            print("❌ ERROR: No valid API key found!")
            print("   Please set RENDER_API_KEY in .env file")
            print("   Example: RENDER_API_KEY=rameez-secret-key-2026")

    async def generate_response(
        self,
        messages: list,
        session_id: str | None = None,
        query: str | None = None,
        stream: bool = True
    ) -> AsyncGenerator[str, None]:
        """Generate response using Render-hosted Punjab Textbook API"""

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

        # Validate API key
        if not self.api_key or self.api_key == "YOUR_API_KEY_HERE":
            yield (
                "📚 **Textbook Assistant Not Configured**\n\n"
                "Please set the following in `backend/.env`:\n\n"
                "RENDER_API_KEY=rameez-secret-key-2026\n"
                "RENDER_URL=https://6399df36b31b.ngrok-free.app\n\n"
                "Then restart the server."
            )
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

            print(f"\n📤 [Render API] Question: {user_query[:80]}...")
            print(f"   URL: {url}")
            print(f"   API Key: {self.api_key[:3]}***")

            timeout = httpx.Timeout(30.0, connect=10.0)

            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(url, json=payload, headers=headers)

            print(f"   Status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()

                answer = data.get("answer", "").strip()
                reference = data.get("reference", "").strip()

                if answer.startswith("• "):
                    answer = answer[2:]

                if answer:
                    formatted = answer
                    if reference:
                        formatted += f"\n\n📚 *{reference}*"
                    formatted += "\n\n💡 *Based on Punjab Textbook Board content*"
                else:
                    formatted = (
                        "I couldn't find a specific answer in the Punjab textbooks "
                        "for that question."
                    )

                if stream:
                    for word in formatted.split():
                        yield word + " "
                        await asyncio.sleep(0.02)
                else:
                    yield formatted

            elif response.status_code == 401:
                yield (
                    "🔐 **Invalid API Key**\n\n"
                    "Please check `RENDER_API_KEY` in `.env`.\n"
                    f"Current key: {self.api_key[:3]}***"
                )

            else:
                try:
                    error_data = response.json()
                    detail = error_data.get("detail", error_data)
                except Exception:
                    detail = response.text[:200]

                yield f"⚠️ Textbook service error ({response.status_code}): {detail}"

        except httpx.RequestError as e:
            print(f"❌ Network error: {e}")
            yield "🔌 Cannot connect to textbook service. Service may be down."

        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            yield f"⚠️ Unexpected error: {str(e)[:120]}"


llm_service = LLMService()


# -------------------------------
# Test utility
# -------------------------------
async def test_connection():
    print("\n🧪 Testing Render Textbook API connection...")

    messages = [{"sender": "user", "content": "What is science?"}]

    try:
        async for response in llm_service.generate_response(messages, stream=False):
            print("✅ Response received:")
            print(response[:300])
            return True
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

# Run manually:
# asyncio.run(test_connection())
