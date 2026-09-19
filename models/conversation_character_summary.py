from datetime import datetime
from uuid import UUID,uuid4
from sqlalchemy import DateTime,ForeignKey,func
from sqlalchemy.orm import mapped_column,Mapped,relationship
from sqlalchemy.dialects.postgresql import JSONB
from database.db import Base

class ConversationCharacterSummary(Base):
    __tablename__="conversation_character_summary"
    conversation_id:Mapped[UUID]=mapped_column(ForeignKey(
        "conversations.conversation_id",
        ondelete="CASCADE"
    ),primary_key=True)
    content:Mapped[dict]=mapped_column(JSONB,nullable=False)
    updated_at:Mapped[datetime]=mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now()
    )
    conversation:Mapped["Conversation"]=relationship(
        back_populates="character_summary"
    )