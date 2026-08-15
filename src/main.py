"""
Entry point for the SunBridge Bangladesh compliance draft pipeline.
 
    python main.py
    python main.py --sources-dir sources --output-dir output
"""
 
import argparse
import sys
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
    result = graph.invoke(build_initial_state(args.sources_dir, args.output_dir))
 
    logger.info("Done. {}", result["final_json"]["summary"])
 
    output_dir = Path(args.output_dir)
    print()
    print(f"  {output_dir / 'compliance_draft.md'}   <- hand this to the import agent")
    print(f"  {output_dir / 'compliance_facts.json'} <- structured output, source-attributed")
    return 0
 
 
if __name__ == "__main__":
    sys.exit(main())