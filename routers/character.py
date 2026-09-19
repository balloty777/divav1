from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from auth.dependencies import get_current_user
from database.dependencies import get_db
from models.user import User
from schemas.character import CharacterCreate, CharacterFromSummaryCreate, CharacterUpdate
from services.character_service import CharacterService


router = APIRouter(
    prefix="/characters",
    tags=["Characters"],
)


@router.post("/from-summary")
def create_character_from_summary(
    data: CharacterFromSummaryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return CharacterService(db).create_character_from_summary(
        creator_id=current_user.user_id,
        name=data.name,
        summary=data.summary,
    )


@router.post("/")
def create_character(
    data: CharacterCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = CharacterService(db)

    return service.create_character(
        creator_id=current_user.user_id,
        name=data.name,
    )


@router.get("/{character_id}")
def get_character(
    character_id: UUID,
    db: Session = Depends(get_db),
):
    service = CharacterService(db)

    return service.get_character(
        character_id=character_id,
    )


@router.put("/{character_id}")
def update_character(
    character_id: UUID,
    data: CharacterUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = CharacterService(db)

    return service.update_character(
        creator_id=current_user.user_id,
        character_id=character_id,
        name=data.name,
    )


@router.delete("/{character_id}")
def delete_character(
    character_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = CharacterService(db)

    service.delete_character(
        creator_id=current_user.user_id,
        character_id=character_id,
    )

    return {"detail": "Character deleted successfully"}
