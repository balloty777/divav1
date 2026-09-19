from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from auth.security import create_access_token
from database.dependencies import get_db
from schemas.user import UserLogin
from services.user_service import UserService


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post("/login")
def login(
    data: UserLogin,
    db: Session = Depends(get_db),
):
    service = UserService(db)

    user = service.authenticate_user(
        email=data.email,
        password=data.password,
    )

    access_token = create_access_token(
        user_id=user.user_id,
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }