from fastapi  import Depends,Header
from uuid import UUID

from fastapi import Header
from sqlalchemy.orm import Session

from database.dependencies import get_db
from exceptions.application import NotFoundException
from models.user import User
from repositories.user_repository import UserRepository


def get_current_user(
    x_user_id: UUID = Header(..., alias="X-User-ID"),
    db: Session = Depends(get_db),
) -> User:
    user_repository = UserRepository(db)

    user = user_repository.get_by_id(x_user_id)

    if user is None:
        raise NotFoundException("User does not exist")

    return user