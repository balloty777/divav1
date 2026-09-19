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


def _serialize_public(character) -> dict:
    return {
        "character_id": character.character_id,
        "name": character.name,
        "avatar_url": character.avatar_url,
        "summary": character.character_summary.content if character.character_summary else None,
    }


@router.get("/")
def list_public_characters(
    db: Session = Depends(get_db),
):
    """Public, no-login-required list of chattable characters with their summaries."""
    service = CharacterService(db)

    return [_serialize_public(character) for character in service.get_public_characters()]


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
        avatar_url=data.avatar_url,
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
        avatar_url=data.avatar_url,
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
        avatar_url=data.avatar_url,
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