from typing import TypeVar

from pydantic import BaseModel


ModelT = TypeVar("ModelT", bound=BaseModel)


def parse_json_response(content: str, model_type: type[ModelT]) -> ModelT:
    """Validate a JSON object even when a model wraps it in a code fence."""
    text = content.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else ""
        text = text.rsplit("```", 1)[0].strip()

    try:
        return model_type.model_validate_json(text)
    except ValueError:
        start, end = text.find("{"), text.rfind("}")
        if start < 0 or end <= start:
            raise
        return model_type.model_validate_json(text[start : end + 1])
