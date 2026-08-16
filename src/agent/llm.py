from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI 
from functools import lru_cache
from langchain_core.messages import HumanMessage, SystemMessage
from llama_cloud import LlamaCloud
from src.core import logger, settings
from typing import TypeVar
from pydantic import ValidationError
import json
import re
from langchain_nvidia_ai_endpoints import ChatNVIDIA

T = TypeVar("T")

# @lru_cache(maxsize=1)
def get_llm():
    return ChatGoogleGenerativeAI(
        model=settings.GEMINI_MODEL,
        api_key=settings.GEMINI_API_KEY
    )


def _extract_json_object(text: str) -> str:
    match = re.search(r"```json\s*(\{.*\})\s*```", text, flags=re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1)
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        return text[start : end + 1]
    return text


@lru_cache(maxsize=1)
def get_llama_cloud() -> LlamaCloud:
    return LlamaCloud(api_key=settings.LLAMA_CLOUD_API_KEY)


def call_structured(system_prompt: str, user_content: str, schema):
    messages = [SystemMessage(content=system_prompt), HumanMessage(content=user_content)]

    model = get_llm().with_structured_output(schema)
    result = model.invoke(messages)
    if result is None:
        raise RuntimeError(f"Model returned nothing for {schema.__name__}.")
    return result



