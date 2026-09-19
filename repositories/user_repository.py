from sqlalchemy.orm import Session
from models.user import User
from uuid import UUID
from sqlalchemy import select
class UserRepository:
    def __init__(self,db:Session):
        self.db=db
    def create_user(self,email:str,password_hash:str)->User:
        user=User(email=email,password_hash=password_hash)
        self.db.add(user)
        return user
    def get_by_email(self,email:str):
        stmt=select(User).where(User.email==email)
        return self.db.scalar(stmt)
    def get_by_id(self,id:UUID):
        stmt=select(User).where(User.user_id==id)
        return self.db.scalar(stmt)
    def delete_user(self,user:User)->None:
        self.db.delete(user)
    def update_user(self,user:User,email:str)->User:
        user.email=email
        return user
