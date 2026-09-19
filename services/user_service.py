from uuid import UUID
from sqlalchemy.orm import Session
from models.user import User
from repositories.user_repository import UserRepository
from exceptions.application import NotFoundException,ConflictException,ForbiddenException
from auth.security import hash_password,verify_password
class UserService:
    def __init__(self,db:Session):
        self.db=db
        self.user_repository = UserRepository(db)
    def create_user(self,email:str,password:str)->User:
        existing_user=self.user_repository.get_by_email(email)
        if existing_user:
            raise ConflictException("User with this email already exists")
        password_hash=hash_password(password)
        user=self.user_repository.create_user(email=email,password_hash=password_hash)
        try:
            self.db.commit()
            self.db.refresh(user)
            return user
        except Exception:
            self.db.rollback()
            raise
    def authenticate_user(self,email: str,password: str) -> User:
        user = self.user_repository.get_by_email(email)
        if user is None:
            raise NotFoundException("User does not exist")
        if not verify_password(password,user.password_hash):
            raise ForbiddenException("Invalid credentials")
        return user
    def update_user(self,user_id:UUID,email:str)->User:
        user=self.user_repository.get_by_id(user_id)
        if user is None:
            raise NotFoundException("User not found")
        db_user=self.user_repository.get_by_email(email)
        if db_user and db_user.user_id!=user.user_id:
            raise ConflictException("EmailID already exist")
        user=self.user_repository.update_user(user,email)
        try:
            self.db.commit()
            self.db.refresh(user)
            return user
        except Exception:
            self.db.rollback()
            raise   
    def delete_user(self,user_id:UUID)->None:
        user=self.user_repository.get_by_id(user_id)
        if user is None:
            raise NotFoundException("User not found")
        self.user_repository.delete_user(user)
        try:
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise