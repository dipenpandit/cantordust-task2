from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI 
from functools import lru_cache
from langchain_core.messages import HumanMessage, SystemMessage
from llama_cloud import LlamaCloud
from src.core import logger, settings
from langchain_core.language_models import BaseLanguageModel
from typing import TypeVar
from langchain_nvidia_ai_endpoints import ChatNVIDIA

T = TypeVar("T")

@lru_cache(maxsize=1)
def get_llm() -> BaseLanguageModel:
    if settings.LLM_PROVIDER == "gemini":
        return ChatGoogleGenerativeAI(
            model=settings.LLM_MODEL,
            api_key=settings.GEMINI_API_KEY
        )
    elif settings.LLM_PROVIDER == "groq":
        return ChatGroq(
            api_key=settings.GROQ_API_KEY,
            model=settings.LLM_MODEL,
        )
    elif settings.LLM_PROVIDER == "nvidia":
        return ChatNVIDIA(
            model="nvidia/nemotron-3-super-120b-a12b",
            api_key=settings.NVIDIA_API_KEY,
            temperature=1,
            top_p=0.95,
            chat_template_kwargs={"enable_thinking":True},
        )


@lru_cache(maxsize=1)
def get_llama_cloud() -> LlamaCloud:
    return LlamaCloud(api_key=settings.LLAMA_CLOUD_API_KEY)


def call_structured(system_prompt: str, user_content: str, schema: type[T]) -> T:
    model = get_llm().with_structured_output(schema)
    result = model.invoke(
        [SystemMessage(content=system_prompt), HumanMessage(content=user_content)]
    )
    if result is None:
        raise RuntimeError(f"Model returned nothing for {schema.__name__}.")
    return result



