from pathlib import Path
from src.core import logger
from src.agent.graph import build_graph, build_initial_state


def main() -> int:
    graph = build_graph()

    graph_view = graph.get_graph()
    logger.info("LangGraph Graph:\n{}", graph_view.draw_ascii())
    with open("langgraph.png", "wb") as f:
        f.write(graph_view.draw_mermaid_png())

    result = graph.invoke(build_initial_state())

    logger.info("Done. {}", result["final_json"]["summary"])

    output_dir = Path("output")
    logger.info(f"Final human readable draft --> {output_dir / 'draft.md'}   ")
    logger.info(f"Extracted facts from the three sources --> {output_dir / 'extracted_facts.json'}")
    return 0
 

if __name__ == "__main__":
    main()

