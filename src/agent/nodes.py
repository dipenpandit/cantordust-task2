import json
from agent.schema import PipelineState, Reconciliation, Extraction
from pathlib import Path
from src.agent.llm import get_llama_cloud, call_structured
from src.core.logger import logger
from collections import defaultdict
from src.agent.prompts import EXTRACT_SYSTEM_PROMPT, RECONCILE_SYSTEM_PROMPT
from src.agent.render import render_markdown

CHECKLIST = {
    "Product identity": ["model_number", "rated_output_power", "max_efficiency", "weight",
                         "ingress_protection", "operating_phase"],
    "Manufacturer identity": ["manufacturer_legal_name", "factory_address", "country_of_manufacture"],
    "Test evidence": ["grid_connection_standards_claimed", "safety_emc_standards_claimed",
                      "third_party_test_body", "certificates_on_file", "declaration_of_conformity"],
    "Labeling": ["label_photo_available", "nameplate_contents"],
    "Importer paperwork": ["buyer_legal_name", "destination_country", "order_reference",
                           "required_by_date", "documents_attached"],
}


SOURCE_LABELS = {
    "datasheet": "manufacturer datasheet",
    "buyer_form": "buyer form",
    "call_notes": "call notes",
}


# Node for fetching source files
def fetch_sources(state: PipelineState) -> PipelineState:
    """
    Fetch all the source files and verify their existence.
    """
    sources_dir = Path(state["sources_dir"])

    datasheet_path = sources_dir / "datasheet.pdf"
    buyer_form_path = sources_dir / "buyer_form.json"
    call_notes_path = sources_dir / "call_notes.txt"

    source_paths = {
        "datasheet": datasheet_path,
        "buyer_form": buyer_form_path,
        "call_notes": call_notes_path
    }
    for path in source_paths.values():
        if not path.exists():
            raise FileNotFoundError(f"Missing source file: {path}.")

    logger.info("All source files found.")
    return {"source_paths": source_paths}


# Node for parsing source files
def parse_sources(state: PipelineState) -> PipelineState:
    """
    Parse all sources in one node.
    """
    parsed_sources = state.get("parsed_sources", [])
    logger.info("Starting to parse sources.")

    datasheet_path = state["source_paths"]["datasheet"]
    buyer_form_path = state["source_paths"]["buyer_form"]
    call_notes_path = state["source_paths"]["call_notes"]
    output_dir = Path(state["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. Parse datasheet (pdf with irregular table, so we'll be using LlamaParse)
    logger.info(f"Parsing datasheet: {datasheet_path}")
    llama_parse_client = get_llama_cloud()
    file_obj = llama_parse_client.files.create(file=datasheet_path, purpose="parse")
    result = llama_parse_client.parsing.parse(
        file_id=file_obj.id,
        tier="cost_effective",
        version="latest",
        expand=["markdown_full"],
    )
    parsed_path = output_dir / "parsed_datasheet.md"
    parsed_path.write_text(result.markdown_full or "")

    parsed_sources.append(
        {
            "source_type": "manufacturer_datasheet",
            "path": datasheet_path,
            "markdown": result.markdown_full or "",
        }
    )
    logger.info(f"Finished parsing datasheet: {datasheet_path}")

    # 2. Parse buyer form
    logger.info("Parsing buyer form")
    buyer_form_path = state["source_paths"]["buyer_form"]
    with open(buyer_form_path, "r") as f:
        buyer_form_data = json.load(f)

    parsed_sources.append(
        {
            "source_type": "buyer_form",
            "path": buyer_form_path,
            "json": json.dumps(buyer_form_data),
        }
    )

    logger.info("Parsing call notes")
    # 3. Parse call notes
    call_notes_path = state["source_paths"]["call_notes"]
    call_notes_text = call_notes_path.read_text(encoding="utf-8")
    parsed_sources.append(
        {
            "source_type": "call_notes",
            "path": call_notes_path,
            "text": call_notes_text,
        }
    )
    logger.info("Finished parsing all sources")
    return {"parsed_sources": parsed_sources}


# Node for extracting facts from parsed sources
def extract_facts(state: PipelineState) -> PipelineState:
    """Extract facts from all parsed sources using the LLM."""
    facts = list(state.get("facts", []))
    
    for parsed_source in state["parsed_sources"]:
        source_id = parsed_source.get("source_type", "unknown_source") 
        content = parsed_source.get("markdown") or parsed_source.get("json") or parsed_source.get("text", "")
    
        logger.info("Extracting facts from {}...", source_id)
        user_content = (
            f"source: {source_id}\n"
            f"<document>\n{content}\n</document>"
        )
        extraction = call_structured(EXTRACT_SYSTEM_PROMPT, user_content, Extraction)
  
        facts += [{**fact.model_dump(), "source": source_id} for fact in extraction.facts]
    
    logger.info("Extracted {} facts.", len(facts))
    return {"facts": facts}


# Node for reconciling facts across sources
def reconcile_facts(state: PipelineState) -> PipelineState:
    """Reconcile facts across sources, identifying conflicts and agreements."""
    groups = defaultdict(list)
    for fact in state["facts"]:
        groups[fact["field"]].append(fact)
 
    contested = {f: items for f, items in groups.items() if len({i["source"] for i in items}) > 1}
 
    verdicts = {}
    if contested:
        logger.info("Reconciling {} multi-source fields...", len(contested))
        payload = [{"field": f, "values": items} for f, items in contested.items()]
        result = call_structured(
            RECONCILE_SYSTEM_PROMPT, json.dumps(payload, indent=2), Reconciliation
        )
        verdicts = {v.field: v for v in result.verdicts}
 
    reconciled = []
    for field, items in groups.items():
        sources = sorted({i["source"] for i in items})
        verdict = verdicts.get(field)
        reconciled.append(
            {
                "field": field,
                "values": items,
                "sources": sources,
                "verdict": verdict.verdict if verdict else ("single_source" if len(sources) == 1 else "agreed"),
                "note": verdict.note if verdict else "",
            }
        )
    return {"reconciled": reconciled}

 
def _status(entry):
    if entry is None:
        return "pending"
    if entry["verdict"] == "conflict":
        return "conflict"
    if "datasheet" in entry["sources"]:
        return "established"
    if entry["sources"] == ["call_notes"]:
        return "verbal_only"
    return "unverified"
 
 
def assess_gaps(state: PipelineState) -> PipelineState:
    """Assess the gaps in the reconciled facts against the checklist."""
    by_field = {entry["field"]: entry for entry in state["reconciled"]}
    coverage = []
 
    for section, fields in CHECKLIST.items():
        for field in fields:
            entry = by_field.get(field)
            coverage.append(
                {
                    "section": section,
                    "field": field,
                    "status": _status(entry),
                    "values": entry["values"] if entry else [],
                    "note": entry["note"] if entry else "Not stated in any of the three sources.",
                }
            )
 
    # Extras the model found outside the checklist are kept, not dropped.
    listed = {f for fields in CHECKLIST.values() for f in fields}
    for field, entry in by_field.items():
        if field not in listed:
            coverage.append(
                {
                    "section": "Other extracted fields",
                    "field": field,
                    "status": _status(entry),
                    "values": entry["values"],
                    "note": entry["note"],
                }
            )
 
    return {"coverage": coverage}
 
def _ordered_model(facts) -> str:
    """Extract the model number from the buyer form if available."""
    for fact in facts:
        if fact["field"] == "model_number" and fact["source"] == "buyer_form":
            return fact["value"]


def draft_questions(state: PipelineState) -> PipelineState:
    """Every question traces back to a field that is missing, contested or verbal-only."""
    questions = []
    model = _ordered_model(state["facts"])

    for row in state["coverage"]:
        label = row["field"].replace("_", " ")
        if row["status"] == "conflict":
            claims = "; ".join(
                f"the {SOURCE_LABELS[v['source']]} says \"{v['value']}\"" for v in row["values"]
            )
            questions.append(f"Which value is correct for {label}? {claims}.")
        elif row["status"] == "verbal_only":
            stated = row["values"][0]["value"]
            questions.append(f"Please confirm {label} in writing - we only have \"{stated}\" from a call.")
        elif row["status"] == "pending":
            questions.append(f"Please supply {label} for {model}.")

    logger.info("Drafted {} questions for the factory.", len(questions))
    return {"questions": questions}


def render_outputs(state: PipelineState) -> PipelineState:
    counts = defaultdict(int)
    for row in state["coverage"]:
        counts[row["status"]] += 1
    
    final_json = {
        "target_model": _ordered_model(state["facts"]),
        "destination_country": "Bangladesh",
        "summary": dict(counts),
        "coverage": state["coverage"],
        "questions_for_factory": state["questions"],
        "raw_facts": state["facts"],
    }
    final_md = render_markdown(final_json)
    
    output_dir = Path(state["output_dir"])
    (output_dir / "compliance_facts.json").write_text(json.dumps(final_json, indent=2), encoding="utf-8")
    (output_dir / "compliance_draft.md").write_text(final_md, encoding="utf-8")
    logger.info("Wrote outputs to {}", output_dir)
    
    return {"final_json": final_json, "final_md": final_md}
    