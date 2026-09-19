from database.db import Base
from datetime import datetime
from uuid import UUID,uuid4
from sqlalchemy import String, DateTime, func
from sqlalchemy.orm import Mapped,mapped_column,relationship

class User(Base):
    __tablename__="users"
    user_id:Mapped[UUID]=mapped_column(
        primary_key=True,
        default=uuid4
    )
    email: Mapped[str]=mapped_column(
        String(320),
        nullable=False,
        unique=True
    )
    password_hash:Mapped[str]=mapped_column(
        String(250),
        nullable=False
    )
    created_at: Mapped[datetime]=mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )
    updated_at: Mapped[datetime]=mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now()
    )
    conversations: Mapped[list["Conversation"]] = relationship(
    back_populates="user",
    cascade="all, delete-orphan"
    )

    characters: Mapped[list["Character"]] = relationship(
        back_populates="creator"
    )