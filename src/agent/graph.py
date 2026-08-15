from langgraph.graph import StateGraph, END
from src.agent.nodes import (
    fetch_sources,
    parse_sources,
)
from agent.schema import PipelineState



def build_graph():
    graph = StateGraph(PipelineState)

    graph.add_node("fetch_sources", fetch_sources)
    graph.add_node("parse_sources", parse_sources)

    graph.set_entry_point("fetch_sources")

    graph.add_edge("fetch_sources", "parse_sources")
    graph.add_edge("parse_sources", END)

    return graph.compile()


initial_state: PipelineState = {
    "sources_dir": "sources",
    "output_dir": "output",
    "source_paths": {},
    "parsed_sources": [],
    "facts": [],
    "final_json": {},
    "final_md": "",
}

graph = build_graph()
graph.invoke(initial_state)

