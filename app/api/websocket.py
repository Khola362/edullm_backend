from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
import json
import asyncio

from app.database.database import get_db
from app.services.chat_service import ChatService
from app.services.llm_service import llm_service

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: dict = {}
    
    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        self.active_connections[session_id] = websocket
    
    def disconnect(self, session_id: str):
        if session_id in self.active_connections:
            del self.active_connections[session_id]
    
    async def send_message(self, message: str, session_id: str):
        if session_id in self.active_connections:
            await self.active_connections[session_id].send_text(message)

manager = ConnectionManager()

@router.websocket("/chat/{session_id}")
async def websocket_chat(websocket: WebSocket, session_id: str):
    await manager.connect(websocket, session_id)
    
    try:
        # Get user_id from query params
        query_params = dict(websocket.query_params)
        user_id = query_params.get("user_id", "anonymous")
        
        print(f"✅ WebSocket connected: session={session_id}, user={user_id}")
        
        await websocket.send_text(json.dumps({
            "type": "info",
            "content": f"Connected to chat session {session_id}"
        }))
        
        # Get database session
        db = next(get_db())
        chat_service = ChatService(db)
        
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            user_message = message_data.get("message", "").strip()
            
            if not user_message:
                continue
            
            print(f"📨 Received message from user {user_id}: {user_message}")
            
            # Save user message to database
            try:
                chat_service.add_message(int(session_id), "user", user_message)
            except Exception as e:
                print(f"❌ Failed to save user message: {e}")
            
            # Get chat history for context
            messages = chat_service.get_session_messages(int(session_id), user_id)
            print(f"📚 Chat history has {len(messages)} messages")
            
            # Prepare messages for LLM
            llm_messages = []
            for msg in messages[-10:]:  # Last 10 messages for context
                llm_messages.append({
                    "sender": msg.sender,
                    "content": msg.content
                })
            
            # Send processing status
            await websocket.send_text(json.dumps({
                "type": "status",
                "content": "Processing your question..."
            }))
            
            # Generate and stream LLM response
            full_response = ""
            try:
                async for chunk in llm_service.generate_response(
                    llm_messages, 
                    session_id=str(session_id), 
                    query=user_message, 
                    stream=True
                ):
                    full_response += chunk
                    await websocket.send_text(json.dumps({
                        "type": "chunk",
                        "content": chunk
                    }))
                    await asyncio.sleep(0.01)
            except Exception as e:
                print(f"❌ LLM generation error: {e}")
                error_message = "I apologize, but I encountered an error processing your request."
                await websocket.send_text(json.dumps({
                    "type": "chunk",
                    "content": error_message
                }))
                full_response = error_message
            
            # Save bot response to database
            try:
                chat_service.add_message(int(session_id), "bot", full_response)
                print(f"✅ Bot response saved to database")
            except Exception as e:
                print(f"❌ Failed to save bot response: {e}")
            
            # Send completion message
            await websocket.send_text(json.dumps({
                "type": "complete",
                "content": "Response complete"
            }))
            print(f"✅ Response sent to user {user_id}")
            
    except WebSocketDisconnect:
        print(f"🔌 Client disconnected from session {session_id}")
        manager.disconnect(session_id)
    except Exception as e:
        print(f"❌ WebSocket error: {e}")
        try:
            await websocket.send_text(json.dumps({
                "type": "error",
                "content": str(e)
            }))
        except:
            pass
        manager.disconnect(session_id)