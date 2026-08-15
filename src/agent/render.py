STATUS = {
    "established": "Established (datasheet)",
    "conflict": "**Conflict**",
    "verbal_only": "Verbal only",
    "unverified": "Unverified",
    "pending": "**Pending from manufacturer**",
}

LABELS = {"datasheet": "Datasheet", "buyer_form": "Buyer form", "call_notes": "Call notes"}


def render_markdown(data: dict) -> str:
    lines = [
        "# Pre-shipment compliance draft - SunBridge Trading",
        "",
        f"**Product:** {data['target_model']}  ",
        f"**Destination:** {data['destination_country']}  ",
        f"**Generated:** {data['generated_at']} (automated draft)",
        "",
        "> **This is not a compliance file.** It is a working draft built from the manufacturer",
        f"> datasheet ({data['datasheet_url']}), the buyer form and call notes of 2024-10-03.",
        "> Anything marked *pending from manufacturer*, *verbal only* or *conflict* is not",
        "> verified evidence and must not be presented to the import agent as if it were.",
        "",
        "## Status at a glance",
        "",
        "| Status | Fields |",
        "| --- | --- |",
    ]
    for status, count in data["summary"].items():
        lines.append(f"| {STATUS.get(status, status)} | {count} |")

    sections = {}
    for row in data["coverage"]:
        sections.setdefault(row["section"], []).append(row)

    for section, rows in sections.items():
        lines += ["", f"## {section}", ""]
        if all(row["status"] == "pending" for row in rows):
            lines += [
                "Nothing here is established by any of the three sources. The rows are kept so",
                "the gap is visible rather than hidden.",
                "",
            ]
        lines += ["| Field | Value | Source | Confidence | Status |", "| --- | --- | --- | --- | --- |"]
        for row in rows:
            values = row["values"]
            cells = (
                "<br>".join(v["value"] for v in values) if values else "-",
                "<br>".join(LABELS.get(v["source"], v["source"]) for v in values) if values else "-",
                "<br>".join(v.get("confidence") or "-" for v in values) if values else "-",
            )
            lines.append(
                f"| {row['field'].replace('_', ' ')} | {cells[0]} | {cells[1]} | {cells[2]} | "
                f"{STATUS.get(row['status'], row['status'])} |"
            )
        for row in rows:
            if row["status"] in ("conflict", "verbal_only") and row["note"]:
                lines.append("")
                lines.append(f"- **{row['field'].replace('_', ' ')}:** {row['note']}")

    lines += ["", "## Questions to send the factory", ""]
    for index, question in enumerate(data["questions_for_factory"], start=1):
        lines.append(f"{index}. {question}")

    return "\n".join(lines)