from pydantic import BaseModel


class CharacterCreate(BaseModel):
    name: str


class CharacterFromSummaryCreate(BaseModel):
    name: str
    summary: str


class CharacterUpdate(BaseModel):
    name: str
