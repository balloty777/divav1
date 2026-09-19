from dotenv import load_dotenv
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from graph.state import State
from database.repository import MessageRepository
from prompts.prompt_builder import create_final_prompt
import os
load_dotenv()
def get_model() -> ChatOpenAI:
    return ChatOpenAI(
        model="gryphe/mythomax-l2-13b",
        api_key=os.getenv("OPENROUTER_API_KEY3"),
        base_url="https://openrouter.ai/api/v1",
        temperature=0.5,
        streaming=False
    )
def ChatNode(state: State) -> dict:
    system_prompt = create_final_prompt(state)
    messages = [
        SystemMessage(content=system_prompt),
        *MessageRepository.get_recent_messages(
            session_id=state["session_id"],
            limit=20,
        ),
        HumanMessage(content=state["query"]),
    ]

    response = get_model().invoke(messages)

    return {
        "response": response.content
    }