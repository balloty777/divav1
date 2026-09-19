from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from auth.dependencies import get_current_user
from database.dependencies import get_db
from models.user import User

from schemas.short_term_memory import ShortTermMemory
from services.short_term_memory_service import ShortTermMemoryService


router = APIRouter(
    prefix="/conversations/{conversation_id}/short-term-memory",
    tags=["Short-Term Memory"],
)


@router.post("/")
def create_short_term_memory(
    conversation_id: UUID,
    data: ShortTermMemory,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = ShortTermMemoryService(db)

    return service.create_short_term_memory(
        user_id=current_user.user_id,
        conversation_id=conversation_id,
        content=data.content,
    )


@router.get("/")
def get_short_term_memory(
    conversation_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = ShortTermMemoryService(db)

    return service.get_short_term_memory(
        user_id=current_user.user_id,
        conversation_id=conversation_id,
    )


@router.put("/")
def update_short_term_memory(
    conversation_id: UUID,
    data: ShortTermMemory,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = ShortTermMemoryService(db)

    return service.update_short_term_memory(
        user_id=current_user.user_id,
        conversation_id=conversation_id,
        content=data.content,
    )


@router.delete("/")
def delete_short_term_memory(
    conversation_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = ShortTermMemoryService(db)

    service.delete_short_term_memory(
        user_id=current_user.user_id,
        conversation_id=conversation_id,
    )

    return {
        "detail": "Short-term memory deleted successfully"
    }