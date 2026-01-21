import httpx
import asyncio
import os
import json
from typing import AsyncGenerator
from app.core.config import settings

class LLMService:
    def __init__(self):
        self.render_url = "https://punjabtextbook-production.up.railway.app"
        # Use your API key - priority: env var > config
        self.api_key = os.getenv("RENDER_API_KEY", settings.punjab_api_key)
        
        if self.api_key and self.api_key != "YOUR_API_KEY_HERE":
            print(f"✅ Punjab Text Book API configured")
            print(f"   Key: {self.api_key[:3]}***")
            print(f"   URL: {self.render_url}")
        else:
            print("❌ ERROR: No valid API key found!")
            print("   Please set RENDER_API_KEY in .env file")
            print("   Example: RENDER_API_KEY=punjab123")
    
    async def generate_response(self, messages: list, session_id: str = None, query: str = None, stream: bool = True) -> AsyncGenerator[str, None]:
        """Generate response using Punjab Text Book API"""
        
        # Get user query
        user_query = query or ""
        if not user_query:
            for msg in reversed(messages):
                if msg.get("sender") == "user":
                    user_query = msg.get("content", "")
                    break
        
        if not user_query:
            yield "Please ask a question about Punjab textbooks."
            return
        
        # Check if API key is configured
        if not self.api_key or self.api_key == "YOUR_API_KEY_HERE":
            yield """📚 **Textbook Assistant Not Configured**
            
Please set up the API key in the backend/.env file:

RENDER_API_KEY=punjab123
RENDER_URLhttps://punjabtextbook-production.up.railway.app

Then restart the server."""
            return
        
        try:
            # Prepare request - EXACTLY as your API expects
            url = f"{self.render_url}/ask"
            headers = {
                "Content-Type": "application/json",
                "x-api-key": self.api_key  # Must be lowercase with hyphens
            }
            payload = {"question": user_query, "k": 3}
            
            print(f"\n📤 [Textbook API] Question: {user_query[:60]}...")
            print(f"   URL: {url}")
            print(f"   Headers: x-api-key: {self.api_key[:3]}***")
            
            # Make request with timeout
            timeout = httpx.Timeout(30.0, connect=10.0)
            
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(url, json=payload, headers=headers)
                
                print(f"   Status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"   ✅ Response received")
                    
                    # Extract answer based on your API's response format
                    answer = data.get("answer", "").strip()
                    reference = data.get("reference", "").strip()
                    
                    # Format the response
                    if answer:
                        # Remove bullet if present
                        if answer.startswith("• "):
                            answer = answer[2:]
                        
                        formatted = answer
                        
                        # Add reference if available
                        if reference:
                            formatted += f"\n\n📚 *{reference}*"
                        
                        # Add note about textbook source
                        formatted += "\n\n💡 *Answer based on Punjab Textbook Board content*"
                        
                    else:
                        formatted = "I couldn't find a specific answer in the Punjab textbooks for that question."
                    
                    # Stream or return complete
                    if stream:
                        words = formatted.split()
                        for word in words:
                            yield word + " "
                            await asyncio.sleep(0.02)
                    else:
                        yield formatted
                        
                elif response.status_code == 401:
                    error_msg = "Invalid API key. Please check RENDER_API_KEY in .env file."
                    print(f"   ❌ {error_msg}")
                    yield f"🔐 {error_msg}\n\nCurrent key: {self.api_key[:3]}***"
                    
                else:
                    error_msg = f"API Error {response.status_code}"
                    try:
                        error_data = response.json()
                        detail = error_data.get("detail", str(error_data))
                        error_msg = f"{error_msg}: {detail}"
                    except:
                        error_text = response.text[:200]
                        error_msg = f"{error_msg}: {error_text}"
                    
                    print(f"   ❌ {error_msg}")
                    yield f"⚠️ Textbook service error: {error_msg}"
                        
        except httpx.RequestError as e:
            print(f"   ❌ Network error: {e}")
            yield "🔌 Cannot connect to textbook service. The service might be down."
        except Exception as e:
            print(f"   ❌ Unexpected error: {e}")
            yield f"An error occurred: {str(e)[:100]}"

llm_service = LLMService()

# Test function
async def test_connection():
    """Test the API connection"""
    service = LLMService()
    
    if not service.api_key or service.api_key == "YOUR_API_KEY_HERE":
        print("❌ No API key configured")
        return
    
    print("\n🧪 Testing connection to Punjab Text Book API...")
    
    test_messages = [{"sender": "user", "content": "What is science?"}]
    
    try:
        async for chunk in service.generate_response(test_messages, stream=False):
            print(f"✅ Test response: {chunk[:100]}...")
            return True
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

# To run test: asyncio.run(test_connection())