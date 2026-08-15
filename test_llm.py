from src.agent.llm import get_llm, call_structured
from src.core import logger
from pydantic import BaseModel, Field

table_md = """
|  # | Name     | Category | Value | Status   | Rating | Notes       |
| -: | -------- | -------- | ----: | -------- | -----: | ----------- |
|  1 | Alpha    | Type A   |    42 | Active   |    4.8 | Excellent   |
|  2 | Bravo    | Type B   |    17 | Pending  |    4.1 | Good        |
|  3 | Charlie  | Type C   |    85 | Active   |    4.6 | Popular     |
|  4 | Delta    | Type A   |    31 | Inactive |    3.9 | Average     |
|  5 | Echo     | Type B   |    64 | Active   |    4.7 | Excellent   |
|  6 | Foxtrot  | Type C   |    23 | Pending  |    4.2 | Good        |
|  7 | Golf     | Type A   |    91 | Active   |    4.9 | Outstanding |
|  8 | Hotel    | Type B   |    56 | Active   |    4.4 | Reliable    |
|  9 | India    | Type C   |    38 | Inactive |    3.7 | Average     |
| 10 | Juliet   | Type A   |    73 | Active   |    4.5 | Very good   |
| 11 | Kilo     | Type B   |    29 | Pending  |    4.0 | Good        |
| 12 | Lima     | Type C   |    47 | Active   |    4.3 | Reliable    |
| 13 | Mike     | Type A   |    68 | Active   |    4.6 | Popular     |
| 14 | November | Type B   |    14 | Inactive |    3.5 | Needs work  |
| 15 | Oscar    | Type C   |    82 | Active   |    4.8 | Excellent   |
| 16 | Papa     | Type A   |    35 | Pending  |    4.1 | Good        |
| 17 | Quebec   | Type B   |    59 | Active   |    4.4 | Reliable    |
| 18 | Romeo    | Type C   |    76 | Active   |    4.7 | Excellent   |
| 19 | Sierra   | Type A   |    21 | Inactive |    3.8 | Average     |
| 20 | Tango    | Type B   |    88 | Active   |    4.9 | Outstanding |
| 21 | Uniform  | Type C   |    44 | Pending  |    4.2 | Good        |
| 22 | Victor   | Type A   |    62 | Active   |    4.5 | Very good   |
| 23 | Whiskey  | Type B   |    27 | Inactive |    3.6 | Average     |
| 24 | X-ray    | Type C   |    94 | Active   |    4.9 | Outstanding |
| 25 | Yankee   | Type A   |    51 | Active   |    4.3 | Reliable    |
| 26 | Zulu     | Type B   |    39 | Pending  |    4.0 | Good        |
| 27 | Atlas    | Type C   |    71 | Active   |    4.6 | Popular     |
| 28 | Nova     | Type A   |    19 | Inactive |    3.4 | Needs work  |
| 29 | Orion    | Type B   |    66 | Active   |    4.5 | Very good   |
| 30 | Phoenix  | Type C   |    97 | Active   |    5.0 | Outstanding |
"""


# Define the target structure for the tabular data
class StructuredTableResponse(BaseModel):
    title: str = Field(description="Title of the comparison table")
    headers: list[str] = Field(description="Column headers in a list")
    rows: list[str] = Field(description="table rows in a list")
    values: dict[str, list[str]] = Field(description="map wach row value to the value in the colum in a list")

# Bind the schema to the chat model
model = get_llm()
result = call_structured(
    system_prompt="You are a data extraction agent. Extract structured data from the table.",
    user_content=f"Please extract the table data into a structured format {table_md}",
    schema=StructuredTableResponse
)

print(f"Extracted structured data:\n{result.model_dump()}")
