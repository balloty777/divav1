from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from uuid import UUID

from database.dependencies import get_db
from auth.dependencies import get_current_user
from models.user import User

from schemas.conversation_schema import ConversationCreate
from services.conversation_service import ConversationService


router = APIRouter(
    prefix="/conversations",
    tags=["Conversations"],
)


@router.get("/")
def get_conversations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    conversations = ConversationService(db).get_conversations(current_user.user_id)
    return [
        {
            "conversation_id": conversation.conversation_id,
            "character_id": conversation.character_id,
            "character_name": conversation.character.name,
            "character_avatar_url": conversation.character.avatar_url,
            "title": conversation.title,
            "updated_at": conversation.updated_at,
        }
        for conversation in conversations
    ]


@router.post("/")
def create_conversation(
    data: ConversationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = ConversationService(db)

    return service.create_conversation(
        current_user_id=current_user.user_id,
        character_id=data.character_id,
    )


@router.get("/{conversation_id}")
def get_conversation(
    conversation_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = ConversationService(db)

    return service.get_conversation(
        current_user_id=current_user.user_id,
        conversation_id=conversation_id,
    )


@router.delete("/{conversation_id}")
def delete_conversation(
    conversation_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = ConversationService(db)

    service.delete_conversation(
        user_id=current_user.user_id,
        conversation_id=conversation_id,
    )

    return {"detail": "Conversation deleted successfully"}
