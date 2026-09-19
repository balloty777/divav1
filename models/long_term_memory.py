from database.db import Base
from uuid import UUID,uuid4
from datetime import datetime
from sqlalchemy import DateTime,ForeignKey,func
from sqlalchemy.orm import Mapped,mapped_column,relationship
from sqlalchemy.dialects.postgresql import JSONB

class LongTermMemory(Base):
    __tablename__="long_term_memory"
    conversation_id:Mapped[UUID]=mapped_column(
        ForeignKey(
            "conversations.conversation_id",
            ondelete="CASCADE"
        ),
        primary_key=True
    )
    content:Mapped[dict]=mapped_column(
        JSONB,
        nullable=False
    )
    updated_at:Mapped[datetime]=mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now()
    )
    conversation:Mapped["Conversation"]=relationship(
        back_populates="long_term_memory"
    )