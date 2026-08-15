from typing import Any, TypedDict, Literal
from pydantic import BaseModel, Field, field_validator
 
 
CONFIDENCE = ("high", "medium", "low")

class PipelineState(TypedDict):
    sources_dir: str
    output_dir: str
    source_paths: dict[str, str]
    parsed_sources: list
    facts: list
    final_json: dict[str, Any]
    final_md: str


class Fact(BaseModel):
    """A single factual claim extracted from one source document."""
 
    field: str = Field(description="snake_case field name, from the canonical list where one fits")
    value: str = Field(description="the value exactly as the source states it")
    quote: str | None = Field(default=None, description="short supporting quote or row name")
    confidence: Literal["high", "medium", "low"] = Field(
        default="low", description="low if the document layout made the value ambiguous"
    )
 
    @field_validator("field", mode="before")
    @classmethod
    def _snake_case(cls, v) -> str:
        return str(v).strip().lower().replace(" ", "_")
 
    @field_validator("value", mode="before")
    @classmethod
    def _as_text(cls, v) -> str:
        return "" if v is None else str(v)
 
    @field_validator("confidence", mode="before")
    @classmethod
    def _known_level(cls, v) -> str:
        level = str(v).strip().lower()
        return level if level in CONFIDENCE else "low"
 
 
class Extraction(BaseModel):
    """Everything found in one source document."""
    facts: list[Fact] = Field(default_factory=list)
 
 
class Verdict(BaseModel):
    """Whether the sources agree about one field."""
 
    field: str = Field(description="the field being compared")
    verdict: Literal["agreed", "conflict"]
    note: str = Field(description="one plain sentence a non-technical import agent can read")
 
    @field_validator("field", mode="before")
    @classmethod
    def _snake_case(cls, v) -> str:
        return str(v).strip().lower().replace(" ", "_")
 
    @field_validator("verdict", mode="before")
    @classmethod
    def _known_verdict(cls, v) -> str:
        return "conflict" if "conflict" in str(v).lower() else "agreed"
 
 
class Reconciliation(BaseModel):
    verdicts: list[Verdict] = Field(default_factory=list)
 