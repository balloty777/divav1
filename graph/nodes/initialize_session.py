from graph.state import State
import uuid
from database.repository import SessionRepository
def initialize_session(state: State):
    session_id=state['session_id']
    if session_id is None:
        session_id=str(uuid.uuid4())
    if not SessionRepository.session_exists(session_id):
        SessionRepository.create_session(session_id)
    return {'session_id':session_id}