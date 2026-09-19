from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import select
from models.long_term_memory import LongTermMemory

class LongTermMemoryRepository:
    def __init__(self,db:Session):
        self.db=db
    def create_long_term_memory(self,conversation_id:UUID,content:dict)->LongTermMemory:
        memory=LongTermMemory(conversation_id=conversation_id,content=content)
        self.db.add(memory)
        return memory
    def get_memory_by_conversation_id(self,conversation_id:UUID)->LongTermMemory|None:
        stmt=select(LongTermMemory).where(LongTermMemory.conversation_id==conversation_id)
        return self.db.scalar(stmt)
    def update_long_term_memory(self,memory:LongTermMemory,content:dict)->LongTermMemory:
        memory.content=content
        return memory
    def delete_long_term_memory(self,memory:LongTermMemory)->None:
        self.db.delete(memory)