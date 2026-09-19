from uuid import UUID
from sqlalchemy import case, select
from sqlalchemy.orm import Session
from models.message import Message
class MessageRepository:
    def __init__(self,db:Session):
        self.db=db
    def store_message(self,conversation_id:UUID,content:str,role:str)->Message:
        message=Message(conversation_id=conversation_id,content=content,role=role)
        self.db.add(message)
        return message
    def get_message_by_id(self,message_id:UUID)->Message|None:
        return self.db.get(Message,message_id)
    def get_message_by_conversation_id(self,conversation_id:UUID)->list[Message]:
        # PostgreSQL's now() is transaction-scoped, so the user message and its
        # reply often have the same timestamp. Keep the pair in speaker order.
        role_order = case((Message.role == "user", 0), else_=1)
        stmt=(select(Message).where(Message.conversation_id==conversation_id).order_by(Message.created_at.asc(), role_order.asc()))
        return list(self.db.scalars(stmt).all())
    def get_message_by_role(self,conversation_id:UUID,role:str)->list[Message]:
        stmt = (select(Message).where(Message.role==role, Message.conversation_id==conversation_id).order_by(Message.created_at.asc()))
        return list(self.db.scalars(stmt).all())
    def delete_message(self,message:Message)->None:
        self.db.delete(message)

