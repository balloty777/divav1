from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from auth.dependencies import get_current_user
from database.dependencies import get_db
from models.user import User
from schemas.user import UserCreate, UserUpdate, UserResponse
from services.user_service import UserService


router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.post(
    "/",
    response_model=UserResponse,
)
def create_user(
    data: UserCreate,
    db: Session = Depends(get_db),
):
    service = UserService(db)

    return service.create_user(
        email=data.email,
        password=data.password,
    )


@router.put(
    "/me",
    response_model=UserResponse,
)
def update_current_user(
    data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = UserService(db)

    return service.update_user(
        user_id=current_user.user_id,
        email=data.email,
    )


@router.delete(
    "/me",
)
def delete_current_user(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = UserService(db)

    service.delete_user(
        user_id=current_user.user_id,
    )

    return {
        "detail": "User deleted successfully",
    }