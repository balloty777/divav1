import os
import logging
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from graph.state import State
from prompts.prompt_builder import create_final_prompt

load_dotenv()

logger = logging.getLogger(__name__)

def get_model() -> ChatOpenAI:
    api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENROUTER_API_KEY1")
    if not api_key:
        raise RuntimeError(
            "OpenRouter is not configured. Set OPENROUTER_API_KEY in the environment."
        )

    return ChatOpenAI(
        model="gryphe/mythomax-l2-13b",
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1",
        temperature=1.15,
        top_p=0.93,
        frequency_penalty=0.7,
        presence_penalty=0.4,
        streaming=True,
    )


def ChatNode(state: State) -> dict:
    prompt = [
        SystemMessage(content=create_final_prompt(state)),
        # Preserve speaker roles for the model. A plain transcript inside the
        # system prompt is much easier for a model to misread or imitate.
        *state.get("messages", [])[-20:],
        HumanMessage(content=state["query"]),
    ]

    response = get_model().invoke(prompt)

    return {"response": response.content}
