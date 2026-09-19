from langchain_core.runnables import RunnableConfig
import logging

from graph.state import State
from memory.short_term_memory import create_short_term_memory
from memory.short_term_memory import ShortTermMemory
from repositories.short_term_memory_repository import ShortTermMemoryRepository

logger = logging.getLogger(__name__)

# Two completed turns are enough to establish a scene. Updating on every reply
# adds latency and makes a summary model overfit greetings and small talk.
SHORT_TERM_MEMORY_INTERVAL = 4

def update_short_term_memory(state: State, config: RunnableConfig) -> dict:
    messages = state.get("messages", [])
    if not messages or len(messages) % SHORT_TERM_MEMORY_INTERVAL != 0:
        return {}

    db = config["configurable"]["db"]
    conversation_id = state["conversation_id"]
    repository = ShortTermMemoryRepository(db)

    memory_row = repository.get_memory_by_conversation_id(conversation_id)
    previous_memory = (
        ShortTermMemory.model_validate(memory_row.content)
        if memory_row is not None
        else None
    )

    try:
        new_memory = create_short_term_memory(messages[-20:], previous_memory)
    except Exception:
        # A malformed or unavailable summary must not roll back the reply that
        # has already been generated and saved for the user.
        logger.exception("Short-term memory update failed for conversation %s", conversation_id)
        return {"short_term_memory": previous_memory} if previous_memory else {}

    content = new_memory.model_dump(mode="json")

    if memory_row is None:
        repository.create_short_term_memory(conversation_id, content)
    else:
        repository.update_short_term_memory(memory_row, content)

    db.flush()

    return {"short_term_memory": new_memory}
