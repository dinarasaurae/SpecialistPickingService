from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from typing import List
from app.core.database import get_db
from app.models.chat import Chat
from app.schemas.chat import ChatCreate, ChatRead
from app.core.security import get_current_user

router = APIRouter(prefix="/chat", tags=["Chat"])

@router.post("/", response_model=ChatRead)
def send_message(
    chat_data: ChatCreate,
    db: Session = Depends(get_db),
    sender_id: int = Depends(get_current_user)
) -> ChatRead:
    new_message = Chat(
        sender_id=sender_id,  # из токена
        receiver_id=chat_data.receiver_id,
        message=chat_data.message,
        sent_at=datetime.now(timezone.utc)
    )
    db.add(new_message)
    db.commit()
    db.refresh(new_message)
    return ChatRead.model_validate(new_message)

@router.get("/", response_model=list[ChatRead])
def get_user_messages(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user)
) -> List[ChatRead]:
    messages = db.query(Chat).filter(
        (Chat.sender_id == user_id) | (Chat.receiver_id == user_id)
    ).all()
    
    if not messages:
        raise HTTPException(status_code=404, detail="Сообщения не найдены")

    return [ChatRead.model_validate(msg) for msg in messages]
