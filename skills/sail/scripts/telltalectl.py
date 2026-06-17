#!/usr/bin/env python3
"""Deterministic helper for Telltale M1.

This is a control-plane helper, not an agent runtime.
Allowed: file IO, branch key, event append, state reduction, schema/event
validation, report writing, and deterministic island scoring helpers.
Forbidden: LLM calls, product-code edits, commits, releases, background scheduling.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional

ROOT = Path.cwd()
STATE_ROOT = ROOT / ".claude" / "telltale"
SCHEMA_ROOT = ROOT / "schemas"

REQUIRED_SCHEMA_FILES = {
    "destination": "destination.schema.json",
    "island": "island.schema.json",
    "island-scorecard": "island-scorecard.schema.json",
    "event": "event.schema.json",
    "route": "route.schema.json",
    "report": "report.schema.json",
    "state": "state.schema.json",
}

REQUIRED_EVENTS = {
    "run_started",
    "loop_authority_claimed",
    "destination_extracted",
    "island_map_created",
    "island_scored",
    "island_selected",
    "island_started",
    "sailor_result",
    "verification_result",
    "inspector_residual",
    "signal_classified",
    "island_reached",
    "verified_route_recorded",
    "island_recharted",
    "run_blocked",
    "run_aborted",
    "max_iterations_reached",
    "convergence_report_written",
    "loop_authority_released",
}

SCORECARD_FIELDS = [
    "value_to_destination",
    "cost_to_try",
    "verification_distance",
    "dependency_readiness",
    "information_gain_if_fail",
    "unknown_surface",
    "coordination_cost",
    "reversibility",
]

TERMINAL_STATUSES = {"SUCCESS", "PARTIAL", "BLOCKED", "ABORTED", "MAX_ITERATIONS"}


def now_iso() -> str:
    return dt.datetime.now().astimezone().isoformat(timespec="seconds")


def branch_key() -> str:
    try:
        name = subprocess.check_output(
            ["git", "branch", "--show-current"], text=True, stderr=subprocess.DEVNULL
        ).strip()
    except Exception:
        name = "detached"
    safe = "".join(c if c.isalnum() or c in "-_." else "-" for c in name).strip("-")
    return safe or "detached"


def branch_dir(key: str | None = None) -> Path:
    return STATE_ROOT / "branches" / (key or branch_key())


def trace_path(key: str | None = None) -> Path:
    return branch_dir(key) / "event-trace.jsonl"


def current_run_id(key: str | None = None) -> str:
    events = list(read_events(key))
    for event in reversed(events):
        if event.get("run_id"):
            return str(event["run_id"])
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    return f"tt-{stamp}"


def append_event(event: Dict[str, Any], key: str | None = None) -> None:
    event.setdefault("ts", now_iso())
    event.setdefault("run_id", current_run_id(key))
    validate_known_event_name(event.get("event"))
    validate_schema_object(event, load_schema("event"))
    path = trace_path(key)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")


def read_events(key: str | None = None, path: Path | None = None) -> Iterable[Dict[str, Any]]:
    trace = path or trace_path(key)
    if not trace.exists():
        return []
    events = []
    with trace.open("r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            if not line.strip():
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError as exc:
                raise SystemExit(f"{trace}:{line_no}: invalid JSONL event: {exc}") from exc
            if not isinstance(event, dict):
                raise SystemExit(f"{trace}:{line_no}: event must be a JSON object")
            events.append(event)
    return events


def load_schema(kind: str) -> Dict[str, Any]:
    try:
        filename = REQUIRED_SCHEMA_FILES[kind]
    except KeyError as exc:
        raise SystemExit(f"Unknown schema kind: {kind}") from exc
    path = SCHEMA_ROOT / filename
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SystemExit(f"Missing schema file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid schema JSON {path}: {exc}") from exc


def resolve_ref(schema: Mapping[str, Any], ref: str) -> Mapping[str, Any]:
    prefix = "#/definitions/"
    if not ref.startswith(prefix):
        raise SystemExit(f"Unsupported schema $ref: {ref}")
    name = ref[len(prefix) :]
    try:
        return schema["definitions"][name]
    except KeyError as exc:
        raise SystemExit(f"Unresolvable schema $ref: {ref}") from exc


def validate_schema_object(value: Any, schema: Mapping[str, Any], root_schema: Optional[Mapping[str, Any]] = None, path: str = "$" ) -> None:
    root_schema = root_schema or schema
    if "$ref" in schema:
        return validate_schema_object(value, resolve_ref(root_schema, str(schema["$ref"])), root_schema, path)

    if "enum" in schema and value not in schema["enum"]:
        raise SystemExit(f"{path}: expected one of {schema['enum']!r}, got {value!r}")

    expected_type = schema.get("type")
    if isinstance(expected_type, list):
        if not any(_type_matches(value, t) for t in expected_type):
            raise SystemExit(f"{path}: expected type {expected_type!r}, got {type(value).__name__}")
    elif expected_type and not _type_matches(value, expected_type):
        raise SystemExit(f"{path}: expected type {expected_type!r}, got {type(value).__name__}")

    if expected_type == "object" or isinstance(value, dict):
        required = schema.get("required", [])
        for field in required:
            if field not in value:
                raise SystemExit(f"{path}: missing required field {field!r}")
        properties = schema.get("properties", {})
        for field, subschema in properties.items():
            if isinstance(value, dict) and field in value:
                validate_schema_object(value[field], subschema, root_schema, f"{path}.{field}")
    elif expected_type == "array" or isinstance(value, list):
        if "minItems" in schema and len(value) < int(schema["minItems"]):
            raise SystemExit(f"{path}: expected at least {schema['minItems']} items")
        item_schema = schema.get("items")
        if item_schema:
            for index, item in enumerate(value):
                validate_schema_object(item, item_schema, root_schema, f"{path}[{index}]")

    if expected_type == "integer" and isinstance(value, int):
        if "minimum" in schema and value < int(schema["minimum"]):
            raise SystemExit(f"{path}: expected >= {schema['minimum']}, got {value}")
        if "maximum" in schema and value > int(schema["maximum"]):
            raise SystemExit(f"{path}: expected <= {schema['maximum']}, got {value}")


def _type_matches(value: Any, expected_type: str) -> bool:
    if expected_type == "object":
        return isinstance(value, dict)
    if expected_type == "array":
        return isinstance(value, list)
    if expected_type == "string":
        return isinstance(value, str)
    if expected_type == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected_type == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if expected_type == "boolean":
        return isinstance(value, bool)
    if expected_type == "null":
        return value is None
    raise SystemExit(f"Unsupported JSON schema type: {expected_type}")


def validate_known_event_name(name: Any) -> None:
    if not isinstance(name, str) or not name:
        raise SystemExit("event.event must be a non-empty string")
    if name not in REQUIRED_EVENTS:
        raise SystemExit(f"Unknown M1 event {name!r}; update RFC before extending the trace")


def validate_scorecard(scorecard: Mapping[str, Any]) -> None:
    validate_schema_object(scorecard, load_schema("island-scorecard"))
    for field in SCORECARD_FIELDS:
        entry = scorecard[field]
        basis = entry.get("basis")
        if not isinstance(basis, list) or not basis or not all(isinstance(item, str) and item.strip() for item in basis):
            raise SystemExit(f"scorecard.{field}.basis must contain non-empty evidence strings")


def score_value(scorecard: Mapping[str, Any], field: str) -> int:
    return int(scorecard[field]["score"])


def priority(scorecard: Mapping[str, Any]) -> int:
    validate_scorecard(scorecard)
    usefulness = (
        score_value(scorecard, "value_to_destination")
        + score_value(scorecard, "information_gain_if_fail")
        + score_value(scorecard, "dependency_readiness")
        + score_value(scorecard, "reversibility")
    )
    cost = (
        score_value(scorecard, "cost_to_try")
        + score_value(scorecard, "verification_distance")
        + score_value(scorecard, "unknown_surface")
        + score_value(scorecard, "coordination_cost")
    )
    return usefulness - cost


def select_island(islands: List[Mapping[str, Any]]) -> Mapping[str, Any]:
    ready: List[tuple[int, int, str, Mapping[str, Any]]] = []
    for island in islands:
        validate_schema_object(island, load_schema("island"))
        scorecard = island["scorecard"]
        validate_scorecard(scorecard)
        if score_value(scorecard, "value_to_destination") <= 0:
            continue
        if score_value(scorecard, "dependency_readiness") == 0:
            continue
        if score_value(scorecard, "verification_distance") >= 4:
            continue
        if score_value(scorecard, "unknown_surface") >= 4 and score_value(scorecard, "information_gain_if_fail") < 4:
            continue
        cost = (
            score_value(scorecard, "cost_to_try")
            + score_value(scorecard, "verification_distance")
            + score_value(scorecard, "unknown_surface")
            + score_value(scorecard, "coordination_cost")
        )
        ready.append((priority(scorecard), -cost, str(island["id"]), island))
    if not ready:
        raise SystemExit("No ready useful island; re-chart or ask Advisor/user")
    ready.sort(key=lambda item: (item[0], item[1], item[2]), reverse=True)
    return ready[0][3]


def init_run(args: argparse.Namespace) -> None:
    key = branch_key()
    bd = branch_dir(key)
    for sub in ["islands", "routes", "verification", "reports"]:
        (bd / sub).mkdir(parents=True, exist_ok=True)
    run_id = f"tt-{dt.datetime.now().strftime('%Y%m%d-%H%M%S')}"
    append_event({"event": "run_started", "run_id": run_id, "payload": {"input_source": args.input_source}}, key)
    append_event({"event": "loop_authority_claimed", "run_id": run_id, "payload": {"branch_key": key}}, key)
    reduce_state(argparse.Namespace(branch=key))
    print(run_id)


def reduce_state(args: argparse.Namespace) -> None:
    key = args.branch or branch_key()
    events = list(read_events(key))
    state: Dict[str, Any] = {
        "run_id": events[-1].get("run_id") if events else current_run_id(key),
        "status": "EMPTY" if not events else "RUNNING",
        "current_island": "",
        "reached_islands": [],
        "last_event": events[-1].get("event") if events else None,
    }
    for event in events:
        name = event.get("event")
        payload = event.get("payload", {})
        if name == "island_selected":
            state["current_island"] = event.get("island_id") or payload.get("island_id") or ""
        elif name == "island_reached":
            island_id = event.get("island_id") or payload.get("island_id")
            if island_id and island_id not in state["reached_islands"]:
                state["reached_islands"].append(island_id)
        elif name == "run_blocked":
            state["status"] = "BLOCKED"
        elif name == "run_aborted":
            state["status"] = "ABORTED"
        elif name == "max_iterations_reached":
            state["status"] = "MAX_ITERATIONS"
        elif name == "convergence_report_written":
            result = payload.get("result")
            if result in TERMINAL_STATUSES:
                state["status"] = result
    validate_schema_object(state, load_schema("state"))
    out = branch_dir(key) / "state.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(state, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def cmd_append_event(args: argparse.Namespace) -> None:
    if bool(args.event_json) == bool(args.event_file):
        raise SystemExit("Provide exactly one of --event-json or --event-file")
    if args.event_json:
        event = json.loads(args.event_json)
    else:
        event = json.loads(Path(args.event_file).read_text(encoding="utf-8"))
    append_event(event, args.branch)
    reduce_state(argparse.Namespace(branch=args.branch))


def cmd_current_state(args: argparse.Namespace) -> None:
    path = branch_dir(args.branch) / "state.json"
    if not path.exists():
        reduce_state(args)
    print(path.read_text(encoding="utf-8"), end="")


def cmd_branch_key(args: argparse.Namespace) -> None:
    print(branch_key())


def cmd_validate(args: argparse.Namespace) -> None:
    data = json.loads(Path(args.file).read_text(encoding="utf-8"))
    if args.kind == "island-scorecard":
        validate_scorecard(data)
    else:
        validate_schema_object(data, load_schema(args.kind))
    print("ok")


def cmd_validate_schemas(args: argparse.Namespace) -> None:
    for kind, filename in sorted(REQUIRED_SCHEMA_FILES.items()):
        schema = load_schema(kind)
        if schema.get("type") != "object":
            raise SystemExit(f"{filename}: top-level schema must be object")
        if "required" not in schema:
            raise SystemExit(f"{filename}: missing required[] contract")
    print(f"ok: {len(REQUIRED_SCHEMA_FILES)} schemas")


def cmd_validate_trace(args: argparse.Namespace) -> None:
    path = Path(args.file) if args.file else trace_path(args.branch)
    events = list(read_events(args.branch, path=path))
    for index, event in enumerate(events, start=1):
        validate_known_event_name(event.get("event"))
        validate_schema_object(event, load_schema("event"), path=f"event[{index}]")
    if args.require_close and events:
        names = {event["event"] for event in events}
        if "convergence_report_written" not in names or "loop_authority_released" not in names:
            raise SystemExit("trace is not closed: missing convergence_report_written or loop_authority_released")
    print(f"ok: {len(events)} events")


def cmd_select_island(args: argparse.Namespace) -> None:
    data = json.loads(Path(args.file).read_text(encoding="utf-8"))
    islands = data.get("islands", data if isinstance(data, list) else None)
    if not isinstance(islands, list):
        raise SystemExit("Expected a list of islands or an object with islands[]")
    selected = select_island(islands)
    print(json.dumps(selected, ensure_ascii=False, indent=2, sort_keys=True))


def cmd_write_report(args: argparse.Namespace) -> None:
    if args.result not in TERMINAL_STATUSES:
        raise SystemExit(f"result must be one of {sorted(TERMINAL_STATUSES)}")
    key = args.branch or branch_key()
    bd = branch_dir(key)
    report_dir = bd / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    events = list(read_events(key))
    state_path = bd / "state.json"
    if not state_path.exists():
        reduce_state(argparse.Namespace(branch=key))
    state = json.loads(state_path.read_text(encoding="utf-8"))
    destination = args.destination or _first_payload_value(events, "destination_extracted", "summary") or "unspecified"
    report = {
        "result": args.result,
        "destination": destination,
        "reached_islands": state.get("reached_islands", []),
        "next_recommended_island": args.next_recommended_island,
    }
    validate_schema_object(report, load_schema("report"))
    (report_dir / "convergence-report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown = [
        "# Telltale Convergence Report",
        "",
        f"- Result: {args.result}",
        f"- Destination: {destination}",
        f"- Reached islands: {', '.join(report['reached_islands']) if report['reached_islands'] else 'none'}",
        f"- Next recommended island: {args.next_recommended_island or 'none'}",
        "",
        "## Summary",
        args.summary or "No summary provided.",
        "",
        "## Event count",
        str(len(events)),
        "",
    ]
    (report_dir / "convergence-report.md").write_text("\n".join(markdown), encoding="utf-8")
    append_event({"event": "convergence_report_written", "payload": {"result": args.result, "report": str(report_dir / "convergence-report.md")}}, key)
    append_event({"event": "loop_authority_released", "payload": {"branch_key": key}}, key)
    reduce_state(argparse.Namespace(branch=key))
    print(report_dir / "convergence-report.md")


def _first_payload_value(events: Iterable[Mapping[str, Any]], event_name: str, key: str) -> str:
    for event in events:
        if event.get("event") != event_name:
            continue
        payload = event.get("payload", {})
        if key in payload:
            return str(payload[key])
        destination = payload.get("destination")
        if isinstance(destination, dict) and key in destination:
            return str(destination[key])
    return ""


def cmd_smoke(args: argparse.Namespace) -> None:
    cmd_validate_schemas(args)
    stamp = dt.datetime.now().strftime('%Y%m%d-%H%M%S-%f')
    key = f"smoke-{stamp}-{os.getpid()}"
    bd = branch_dir(key)
    if bd.exists():
        raise SystemExit(f"Smoke branch already exists: {bd}")
    run_id = f"tt-smoke-{stamp}"
    append_event({"event": "run_started", "run_id": run_id, "payload": {"input_source": "smoke"}}, key)
    append_event({"event": "loop_authority_claimed", "run_id": run_id, "payload": {"branch_key": key}}, key)
    append_event({"event": "destination_extracted", "run_id": run_id, "payload": {"destination": sample_destination()}}, key)
    scorecard = sample_scorecard()
    island = sample_island(scorecard)
    append_event({"event": "island_map_created", "run_id": run_id, "payload": {"islands": [island]}}, key)
    append_event({"event": "island_scored", "run_id": run_id, "island_id": island["id"], "payload": {"scorecard": scorecard}}, key)
    selected = select_island([island])
    append_event({"event": "island_selected", "run_id": run_id, "island_id": selected["id"], "payload": {"island_id": selected["id"]}}, key)
    append_event({"event": "island_started", "run_id": run_id, "island_id": selected["id"], "payload": {}}, key)
    append_event({"event": "sailor_result", "run_id": run_id, "island_id": selected["id"], "payload": {"actions_taken": ["smoke"]}}, key)
    append_event({"event": "verification_result", "run_id": run_id, "island_id": selected["id"], "payload": {"passed": True, "checks": ["smoke"]}}, key)
    append_event({"event": "inspector_residual", "run_id": run_id, "island_id": selected["id"], "payload": {"unknowns": []}}, key)
    append_event({"event": "signal_classified", "run_id": run_id, "island_id": selected["id"], "payload": {"accepted": [], "deferred": [], "rejected": []}}, key)
    append_event({"event": "island_reached", "run_id": run_id, "island_id": selected["id"], "payload": {"island_id": selected["id"]}}, key)
    append_event({"event": "verified_route_recorded", "run_id": run_id, "island_id": selected["id"], "payload": {"route": sample_route(selected["id"])}}, key)
    reduce_state(argparse.Namespace(branch=key))
    cmd_write_report(argparse.Namespace(branch=key, result="SUCCESS", destination="Smoke destination", next_recommended_island="", summary="Smoke run completed."))
    cmd_validate_trace(argparse.Namespace(branch=key, file=None, require_close=True))
    print(f"ok: smoke branch {key}")


def sample_scorecard() -> Dict[str, Dict[str, Any]]:
    def s(score: int, basis: str) -> Dict[str, Any]:
        return {"score": score, "basis": [basis]}
    return {
        "value_to_destination": s(4, "smoke destination requires one small island"),
        "cost_to_try": s(1, "no product code edits"),
        "verification_distance": s(1, "helper validates state locally"),
        "dependency_readiness": s(5, "all files are in the repository"),
        "information_gain_if_fail": s(3, "failure would identify helper/schema wiring"),
        "unknown_surface": s(1, "bounded smoke fixture"),
        "coordination_cost": s(1, "single island"),
        "reversibility": s(5, "generated state is gitignored"),
    }


def sample_destination() -> Dict[str, Any]:
    return {
        "id": "dest-smoke",
        "summary": "Smoke destination",
        "source": "telltalectl smoke",
        "in_scope": ["validate helper loop"],
        "out_of_scope": ["edit product code"],
        "close_criteria": ["smoke report written"],
    }


def sample_island(scorecard: Mapping[str, Any]) -> Dict[str, Any]:
    return {
        "id": "island-smoke",
        "title": "Validate helper loop",
        "status": "ready",
        "scope": ["scripts/telltalectl.py"],
        "dependencies": [],
        "close_criteria": ["state and report validate"],
        "scorecard": dict(scorecard),
    }


def sample_route(island_id: str) -> Dict[str, Any]:
    return {
        "from_island": island_id,
        "facts": ["smoke fixture executed"],
        "decisions": ["helper can record verified route"],
        "constraints": ["no LLM calls"],
        "passed_checks": ["validate-trace"],
        "deferred_signals": [],
        "rejected_signals": [],
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Telltale M1 deterministic helper")
    sub = parser.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("branch-key")
    s.set_defaults(func=cmd_branch_key)

    s = sub.add_parser("init-run")
    s.add_argument("--input-source", default="user_prompt")
    s.set_defaults(func=init_run)

    s = sub.add_parser("append-event")
    s.add_argument("--event-json")
    s.add_argument("--event-file")
    s.add_argument("--branch")
    s.set_defaults(func=cmd_append_event)

    s = sub.add_parser("reduce-state")
    s.add_argument("--branch")
    s.set_defaults(func=reduce_state)

    s = sub.add_parser("current-state")
    s.add_argument("--branch")
    s.set_defaults(func=cmd_current_state)

    s = sub.add_parser("validate")
    s.add_argument("--kind", required=True, choices=sorted(REQUIRED_SCHEMA_FILES))
    s.add_argument("--file", required=True)
    s.set_defaults(func=cmd_validate)

    s = sub.add_parser("validate-schemas")
    s.set_defaults(func=cmd_validate_schemas)

    s = sub.add_parser("validate-trace")
    s.add_argument("--branch")
    s.add_argument("--file")
    s.add_argument("--require-close", action="store_true")
    s.set_defaults(func=cmd_validate_trace)

    s = sub.add_parser("select-island")
    s.add_argument("--file", required=True)
    s.set_defaults(func=cmd_select_island)

    s = sub.add_parser("write-report")
    s.add_argument("--branch")
    s.add_argument("--result", required=True, choices=sorted(TERMINAL_STATUSES))
    s.add_argument("--destination", default="")
    s.add_argument("--next-recommended-island", default="")
    s.add_argument("--summary", default="")
    s.set_defaults(func=cmd_write_report)

    s = sub.add_parser("smoke")
    s.set_defaults(func=cmd_smoke)

    return parser


def main(argv: Optional[List[str]] = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
