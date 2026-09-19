from database.db import Base
from datetime import datetime
from sqlalchemy.orm import Mapped,mapped_column,relationship
from sqlalchemy import DateTime,ForeignKey,func
from sqlalchemy.dialects.postgresql import JSONB
from uuid import UUID,uuid4

class CharacterSummary(Base):
    __tablename__='character_summary'
    character_id:Mapped[UUID]=mapped_column(
        ForeignKey(
            "characters.character_id",
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
    character:Mapped["Character"]=relationship(
        back_populates="character_summary"
    )