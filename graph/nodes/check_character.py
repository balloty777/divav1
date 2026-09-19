from character.character_summary import create_character
from database.repository import CharacterRepository
from graph.state import State
from database.repository import SessionRepository
import uuid
def initialize_session(state: State):

    session_id=state['session_id']
    if session_id is None:
        session_id=str(uuid.uuid4())
    if not SessionRepository.session_exists(session_id):
        SessionRepository.create_session(session_id)
    return {'session_id':session_id}

def character_initialization(state: State) -> dict:
    if state.get("character_summary") is not None:
        return {}
    character_summary = create_character(state["character_init"])
    CharacterRepository.save_character_summary(state["session_id"],character_summary)
    return {"character_summary": character_summary}
