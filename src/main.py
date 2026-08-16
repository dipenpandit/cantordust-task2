"""
Entry point for the SunBridge Bangladesh compliance draft pipeline.
 
    python main.py
    python main.py --sources-dir sources --output-dir output
"""
 
import argparse
from pathlib import Path
from src.core import logger 
from src.agent.graph import build_graph, build_initial_state

 
def main() -> int:
    parser = argparse.ArgumentParser(description="Build the SunBridge compliance draft.")
    parser.add_argument("--sources-dir", default="sources")
    parser.add_argument("--output-dir", default="output")
    parser.add_argument("--log-level", default="INFO")
    args = parser.parse_args()
 
    graph = build_graph()

    graph_view = graph.get_graph()
    logger.info(logger.info("LangGraph Graph:\n{}",graph_view.draw_ascii()))
    with open("langgraph.png", "wb") as f:
        f.write(graph_view.draw_mermaid_png())

    result = graph.invoke(build_initial_state(args.sources_dir, args.output_dir))
 
    logger.info("Done. {}", result["final_json"]["summary"])
 
    output_dir = Path(args.output_dir)
    logger.info(f"  {output_dir / 'draft.md'}   <- final draft, human-readable")
    logger.info(f"  {output_dir / 'extracted_facts.json'} <- extracted facts from the three sources")
    return 0
 

if __name__ == "__main__":
    main()

