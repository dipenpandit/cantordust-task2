from langgraph.graph import StateGraph, END
from src.agent.nodes import (
    fetch_sources,
    parse_sources,
    extract_facts,
    reconcile_facts,
    assess_gaps,
    draft_questions,
    render_outputs,
)
from src.agent.schema import PipelineState


def build_graph():
    graph = StateGraph(PipelineState)
 
    graph.add_node("fetch_sources", fetch_sources)
    graph.add_node("parse_sources", parse_sources)
    graph.add_node("extract_facts", extract_facts)
    graph.add_node("reconcile_facts", reconcile_facts)
    graph.add_node("assess_gaps", assess_gaps)
    graph.add_node("draft_questions", draft_questions)
    graph.add_node("render_outputs", render_outputs)
 
    graph.set_entry_point("fetch_sources")
 
    graph.add_edge("fetch_sources", "parse_sources")
    graph.add_edge("parse_sources", "extract_facts")
    graph.add_edge("extract_facts", "reconcile_facts")
    graph.add_edge("reconcile_facts", "assess_gaps")
    graph.add_edge("assess_gaps", "draft_questions")
    graph.add_edge("draft_questions", "render_outputs")
    graph.add_edge("render_outputs", END)
 
    return graph.compile()
 
 
def build_initial_state(sources_dir: str = "sources", output_dir: str = "output") -> PipelineState:
    return {
        "sources_dir": sources_dir,
        "output_dir": output_dir,
        "source_paths": {},
        "parsed_sources": [],
        "facts": [],
        "reconciled": [],
        "coverage": [],
        "questions": [],
        "final_json": {},
        "final_md": "",
    }
 
