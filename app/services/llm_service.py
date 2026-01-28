import httpx
import asyncio
from typing import AsyncGenerator
from app.core.config import settings
import re

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

        # Get question
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
        headers = {"Content-Type": "application/json", "x-api-key": self.api_key}
        payload = {"question": user_query, "top_k": 3, "session_id": session_id or "default"}

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(url, json=payload, headers=headers)
                if response.status_code != 200:
                    yield f"Punjab API error: {response.status_code}"
                    return

                data = response.json()
                answer = data.get("answer", "")

                # Split sections using markers
                book_answer = teacher_explanation = solved_example = final_answer = ""

                # Extract each part if present
                book_match = re.search(r"📘 Book Answer:(.*?)(🧠|✅|$)", answer, re.DOTALL)
                if book_match:
                    book_answer = book_match.group(1).strip()

                teacher_match = re.search(r"🧠 Teacher Explanation:(.*?)(✏️|✅|$)", answer, re.DOTALL)
                if teacher_match:
                    teacher_explanation = teacher_match.group(1).strip()

                solved_match = re.search(r"✏️ Solved Example:(.*?)(✅|$)", answer, re.DOTALL)
                if solved_match:
                    solved_example = solved_match.group(1).strip()

                final_match = re.search(r"✅ Final Answer:(.*)", answer, re.DOTALL)
                if final_match:
                    final_answer = final_match.group(1).strip()

                # Fallback if nothing found
                if not any([book_answer, teacher_explanation, final_answer]):
                    book_answer = answer

                # Compose sections with explicit newlines
                sections = []
                if book_answer:
                    sections.append(f"\n📘 Book Answer---\n{book_answer}\n")
                if teacher_explanation:
                    sections.append(f"\n🧠 Teacher Explanation---\n{teacher_explanation}\n")
                if solved_example:
                    sections.append(f"\n✏️ Solved Example---\n{solved_example}\n")
                if final_answer:
                    sections.append(f"\n✅ Final Answer---\n{final_answer}\n")

                # Stream word by word if needed
                if stream:
                    for section in sections:
                        for word in section.split():
                            yield word + " "
                        yield "\n"
                else:
                    yield "\n".join(sections)

        except httpx.TimeoutException:
            yield "❌ Punjab API timeout. Please try again."
        except httpx.RequestError as e:
            yield "❌ Connection error. Please check Punjab API availability."
        except Exception as e:
            yield f"❌ Unexpected error: {e}"


# Create instance
llm_service = LLMService()
