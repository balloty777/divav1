from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.runnables import RunnableConfig
from graph.state import State
from repositories.message_repository import MessageRepository


def save_messages(state: State, config: RunnableConfig) -> dict:
    db = config["configurable"]["db"]
    conversation_id = state["conversation_id"]
    repository = MessageRepository(db)
    repository.store_message(conversation_id=conversation_id,role="user",content=state["query"])
    repository.store_message(conversation_id=conversation_id,role="assistant",content=state["response"])
    db.flush()

    return {
        "messages": [
            *state.get("messages", []),
            HumanMessage(content=state["query"]),
            AIMessage(content=state["response"]),
        ]
    }