from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import select
from models.short_term_memory import ShortTermMemory

class ShortTermMemoryRepository:
    def __init__(self,db:Session):
        self.db=db
    def create_short_term_memory(self,conversation_id:UUID,content:dict)->ShortTermMemory:
        memory=ShortTermMemory(conversation_id=conversation_id,content=content)
        self.db.add(memory)
        return memory
    def get_memory_by_conversation_id(self,conversation_id:UUID)->ShortTermMemory|None:
        stmt=select(ShortTermMemory).where(ShortTermMemory.conversation_id==conversation_id)
        return self.db.scalar(stmt)
    def update_short_term_memory(self,memory:ShortTermMemory,content:dict)->ShortTermMemory:
        memory.content=content
        return memory
    def delete_short_term_memory(self,memory:ShortTermMemory)->None:
        self.db.delete(memory)