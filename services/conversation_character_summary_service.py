from uuid import UUID
from sqlalchemy.orm import Session
from models.conversation_character_summary import ConversationCharacterSummary
from repositories.conversation_character_summary_repository import (ConversationCharacterSummaryRepository)
from repositories.conversation_repository import ConversationRepository
from exceptions.application import NotFoundException, ConflictException,ForbiddenException



class ConversationCharacterSummaryService:
    def __init__(self, db: Session):
        self.db = db
        self.conversation_character_summary_repository = (ConversationCharacterSummaryRepository(db))
        self.conversation_repository = ConversationRepository(db)
    def create_conversation_character_summary(self,user_id:UUID,conversation_id: UUID,content: dict) -> ConversationCharacterSummary:
        conversation = self.conversation_repository.get_by_id(conversation_id=conversation_id)
        if conversation is None:
            raise NotFoundException("Conversation does not exist")
        if user_id!=conversation.user_id:
            raise ForbiddenException("Not Authorised")
        existing_summary = (self.conversation_character_summary_repository.get_by_conversation_id(conversation_id=conversation_id))
        if existing_summary is not None:
            raise ConflictException("Character summary for this conversation already exists")
        summary = (self.conversation_character_summary_repository.create_conversation_character_summary(conversation_id=conversation_id,content=content))
        try:
            self.db.commit()
            self.db.refresh(summary)
            return summary
        except Exception:
            self.db.rollback()
            raise
    def get_conversation_character_summary(self,user_id:UUID,conversation_id: UUID) -> ConversationCharacterSummary:
        summary = (self.conversation_character_summary_repository.get_by_conversation_id(conversation_id=conversation_id))
        conversation=(self.conversation_repository.get_by_id(conversation_id=conversation_id))
        if summary is None:
            raise NotFoundException("Conversation character summary does not exist")
        if user_id!=conversation.user_id:
            raise ForbiddenException("Not Authorised")
        return summary
    def update_conversation_character_summary(self,user_id:UUID,conversation_id: UUID,content: dict) -> ConversationCharacterSummary:
        summary = (self.conversation_character_summary_repository.get_by_conversation_id(conversation_id=conversation_id))
        conversation=(self.conversation_repository.get_by_id(conversation_id=conversation_id))
        if summary is None:
            raise NotFoundException("Conversation character summary does not exist")
        if user_id!=conversation.user_id:
            raise ForbiddenException("Not Authorised")
        summary = (self.conversation_character_summary_repository.update_conversation_character_summary(summary=summary,content=content))
        try:
            self.db.commit()
            self.db.refresh(summary)
            return summary
        except Exception:
            self.db.rollback()
            raise
    def delete_conversation_character_summary(self,user_id:UUID,conversation_id: UUID) -> None:
        summary = (self.conversation_character_summary_repository.get_by_conversation_id(conversation_id=conversation_id))
        conversation=(self.conversation_repository.get_by_id(conversation_id=conversation_id))
        if summary is None:
            raise NotFoundException("Conversation character summary does not exist")
        if user_id!=conversation.user_id:
            raise ForbiddenException("Not Authorised")
        self.conversation_character_summary_repository.delete_conversation_character_summary(summary=summary)
        try:
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise