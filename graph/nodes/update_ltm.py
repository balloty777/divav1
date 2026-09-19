from langchain_core.runnables import RunnableConfig
import logging

from graph.state import State
from memory.long_term_memory import create_long_term_memory
from memory.long_term_memory import LongTermMemory
from repositories.long_term_memory_repository import LongTermMemoryRepository


LONG_TERM_MEMORY_INTERVAL = 20
logger = logging.getLogger(__name__)


def update_long_term_memory(state: State, config: RunnableConfig) -> dict:
    messages = state.get("messages", [])

    # Long-term memory is more expensive and should only track durable facts.
    # Update it every 20 stored messages rather than after every response.
    if not messages or len(messages) % LONG_TERM_MEMORY_INTERVAL != 0:
        return {}

    db = config["configurable"]["db"]
    conversation_id = state["conversation_id"]
    repository = LongTermMemoryRepository(db)

    memory_row = repository.get_memory_by_conversation_id(conversation_id)
    previous_memory = (
        LongTermMemory.model_validate(memory_row.content)
        if memory_row is not None
        else None
    )

    try:
        # A compact recent window plus the previous durable summary is enough
        # context and avoids wasting the roleplay model's context budget.
        new_memory = create_long_term_memory(messages[-60:], previous_memory)
    except Exception:
        # Long-term memory is optional enrichment; never fail the chat turn if
        # the summarizer is unavailable or returns malformed JSON.
        logger.exception("Long-term memory update failed for conversation %s", conversation_id)
        return {"long_term_memory": previous_memory} if previous_memory else {}

    content = new_memory.model_dump(mode="json")

    if memory_row is None:
        repository.create_long_term_memory(conversation_id, content)
    else:
        repository.update_long_term_memory(memory_row, content)

    db.flush()

    return {"long_term_memory": new_memory}
