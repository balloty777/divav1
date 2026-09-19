from uuid import UUID
from pydantic import BaseModel 
class ConversationCreate(BaseModel):
    character_id:UUID