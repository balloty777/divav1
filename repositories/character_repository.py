from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import Session
from models.character import Character

class CharacterRepository:
    def __init__(self, db: Session):
        self.db = db
    def create_character(self,creator_id: UUID,name: str,status: str = "draft") -> Character:
        character = Character(creator_id=creator_id,name=name,status=status)
        self.db.add(character)
        return character
    def get_by_id(self,character_id: UUID) -> Character | None:
        stmt = select(Character).where(Character.character_id == character_id)
        return self.db.scalar(stmt)
    def get_by_creator(self,creator_id: UUID) -> list[Character]:
        stmt = (select(Character).where(Character.creator_id == creator_id).order_by(Character.created_at.desc()))
        return list(self.db.scalars(stmt).all())
    def update_character(self,character: Character,name: str) -> Character:
        character.name = name
        return character
    def delete_character(self,character: Character,) -> None:
        self.db.delete(character)