from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel

from app.database.database import get_db
from app.models.chat import ChatSession, ChatMessage
from app.services.chat_service import ChatService

router = APIRouter()

# Define Pydantic models for request/response
class ChatSessionCreate(BaseModel):
    user_id: str
    title: str = "New Chat"

class ChatSessionResponse(BaseModel):
    id: int
    title: str
    created_at: str
    updated_at: str

class ChatMessageResponse(BaseModel):
    id: int
    sender: str
    content: str
    timestamp: str

@router.get("/chat/sessions")
def get_chat_sessions(
    user_id: str,
    db: Session = Depends(get_db)
):
    """Get all chat sessions for a user"""
    try:
        service = ChatService(db)
        sessions = service.get_user_sessions(user_id)
        return [
            {
                "id": session.id,
                "title": session.title,
                "created_at": session.created_at.isoformat() if session.created_at else None,
                "updated_at": session.updated_at.isoformat() if session.updated_at else None
            }
            for session in sessions
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat/sessions")
def create_chat_session(
    session_data: ChatSessionCreate,
    db: Session = Depends(get_db)
):
    """Create a new chat session"""
    try:
        service = ChatService(db)
        session = service.create_chat_session(session_data.user_id, session_data.title)
        return {
            "id": session.id,
            "title": session.title,
            "created_at": session.created_at.isoformat() if session.created_at else None,
            "updated_at": session.updated_at.isoformat() if session.updated_at else None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/chat/{session_id}/messages")
def get_chat_messages(
    session_id: int,
    user_id: str,
    db: Session = Depends(get_db)
):
    """Get messages for a specific chat session"""
    try:
        service = ChatService(db)
        messages = service.get_session_messages(session_id, user_id)
        return [
            {
                "id": msg.id,
                "sender": msg.sender,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat() if msg.timestamp else None
            }
            for msg in messages
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))