from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class CharacterCreate(BaseModel):
    name: str
    avatar_url: Optional[str] = None


class CharacterFromSummaryCreate(BaseModel):
    name: str
    summary: str
    avatar_url: Optional[str] = None


class CharacterUpdate(BaseModel):
    name: str
    avatar_url: Optional[str] = None


class CharacterPublic(BaseModel):
    character_id: UUID
    name: str
    avatar_url: Optional[str] = None
    summary: Optional[dict] = None

    model_config = {
        "from_attributes": True
    }