from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from models.character_summary import CharacterSummary


class CharacterSummaryRepository:
    def __init__(self, db: Session):
        self.db = db
    def create_character_summary(self,character_id: UUID,content: dict) -> CharacterSummary:
        character_summary = CharacterSummary(character_id=character_id,content=content)
        self.db.add(character_summary)
        return character_summary
    def get_by_character_id(self,character_id: UUID) -> CharacterSummary | None:
        stmt = select(CharacterSummary).where(CharacterSummary.character_id == character_id)
        return self.db.scalar(stmt)
    def update_character_summary(self,character_summary: CharacterSummary,content: dict) -> CharacterSummary:
        character_summary.content = content
        return character_summary
    def delete_character_summary(self,character_summary: CharacterSummary,) -> None:
        self.db.delete(character_summary)