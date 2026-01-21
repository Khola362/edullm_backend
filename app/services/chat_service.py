from sqlalchemy.orm import Session
from typing import List
from app.models.chat import ChatSession, ChatMessage
from datetime import datetime

class ChatService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_chat_session(self, user_id: str, title: str = "New Chat") -> ChatSession:
        session = ChatSession(user_id=user_id, title=title)
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session
    
    def get_user_sessions(self, user_id: str) -> List[ChatSession]:
        return self.db.query(ChatSession)\
            .filter(ChatSession.user_id == user_id)\
            .order_by(ChatSession.updated_at.desc())\
            .all()
    
    def get_session_messages(self, session_id: int, user_id: str) -> List[ChatMessage]:
        # First verify the session belongs to the user
        session = self.db.query(ChatSession).filter(
            ChatSession.id == session_id,
            ChatSession.user_id == user_id
        ).first()
        
        if not session:
            return []
        
        # Get messages for this session
        return self.db.query(ChatMessage)\
            .filter(ChatMessage.session_id == session_id)\
            .order_by(ChatMessage.timestamp.asc())\
            .all()
    
    def add_message(self, session_id: int, sender: str, content: str) -> ChatMessage:
        message = ChatMessage(
            session_id=session_id,
            sender=sender,
            content=content
        )
        self.db.add(message)
        
        # Update session timestamp
        session = self.db.query(ChatSession).get(session_id)
        if session:
            session.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(message)
        return message