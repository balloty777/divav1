from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from auth.dependencies import get_current_user
from database.dependencies import get_db
from models.user import User

from schemas.long_term_memory import LongTermMemoryCreate
from services.long_term_memory_service import LongTermMemoryService


router = APIRouter(
    prefix="/conversations/{conversation_id}/long-term-memory",
    tags=["Long-Term Memory"],
)


@router.post("/")
def create_long_term_memory(
    conversation_id: UUID,
    data: LongTermMemoryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = LongTermMemoryService(db)

    return service.create_long_term_memory(
        user_id=current_user.user_id,
        conversation_id=conversation_id,
        content=data.content,
    )


@router.get("/")
def get_long_term_memory(
    conversation_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = LongTermMemoryService(db)

    return service.get_long_term_memory(
        user_id=current_user.user_id,
        conversation_id=conversation_id,
    )


@router.put("/")
def update_long_term_memory(
    conversation_id: UUID,
    data: LongTermMemoryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = LongTermMemoryService(db)

    return service.update_long_term_memory(
        user_id=current_user.user_id,
        conversation_id=conversation_id,
        content=data.content,
    )


@router.delete("/")
def delete_long_term_memory(
    conversation_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = LongTermMemoryService(db)

    service.delete_long_term_memory(
        user_id=current_user.user_id,
        conversation_id=conversation_id,
    )

    return {
        "detail": "Long-term memory deleted successfully"
    }