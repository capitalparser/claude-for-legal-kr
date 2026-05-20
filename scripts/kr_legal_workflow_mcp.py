#!/usr/bin/env python3
"""Provider-neutral MCP server for Korean legal workflow helpers.

This server intentionally does not call an LLM provider. It exposes Korean
legal source lookup and review-payload assembly as MCP tools so Claude,
OpenAI, Cursor, Windsurf, LangChain, local models, or another MCP-capable
client can decide how to use the returned context.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
GENERAL_REVIEW_WORKFLOW = ROOT / "references" / "korea" / "general-legal-review-workflow.md"
PRIVACY_REVIEW_SKILL = ROOT / "privacy-legal" / "skills" / "kr-pipa-dpa-review" / "SKILL.md"
PRIVACY_PLAYBOOK = ROOT / "privacy-legal" / "references" / "korea-pipa-dpa-playbook.md"

SOURCE_STATUS_RULES = [
    "Use verified_source only for law text or official guidance actually retrieved in this run.",
    "Use user_supplied_unverified when the user provides facts or citations not independently retrieved.",
    "Use model_inference when a conclusion is inferred from the document or question without live source confirmation.",
    "Always include requires_professional_review before external reliance, filing, sending, signing, or business execution.",
]

DEFAULT_SOURCE_PLAN = [
    "Identify the legal domain and likely Korean source family.",
    "Search Korean statutes and official sources for the named law, issue, or article.",
    "Retrieve controlling article text when a statute is identified.",
    "Separate verified source text from model inference in the final answer.",
]


def _jsonrpc_result(request_id: Any, result: Any) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": request_id, "result": result}


def _jsonrpc_error(request_id: Any, code: int, message: str) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": request_id, "error": {"code": code, "message": message}}


def _content(data: dict[str, Any]) -> dict[str, Any]:
    return {
        "content": [
            {
                "type": "text",
                "text": json.dumps(data, ensure_ascii=False, indent=2),
            }
        ]
    }


def _read_optional(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def _run_korean_law_mcp(args: list[str], timeout: int = 45) -> dict[str, Any]:
    env = os.environ.copy()
    oc = env.get("LAW_OC") or env.get("KOREAN_LAW_API_KEY")
    if not oc:
        return {
            "status": "skipped",
            "reason": "LAW_OC or KOREAN_LAW_API_KEY is not set.",
        }

    env["LAW_OC"] = oc
    result = subprocess.run(
        ["npx", "-y", "korean-law-mcp@latest", *args],
        check=False,
        capture_output=True,
        text=True,
        timeout=timeout,
        env=env,
    )
    return {
        "status": "ok" if result.returncode == 0 else "error",
        "command": ["npx", "-y", "korean-law-mcp@latest", *args],
        "returncode": result.returncode,
        "stdout": result.stdout[:12000],
        "stderr": result.stderr[:4000],
    }


def list_tools() -> dict[str, Any]:
    return {
        "tools": [
            {
                "name": "kr_legal_source_search",
                "description": (
                    "Plan or run Korean legal source lookup through korean-law-mcp. "
                    "Use this before legal review so citations can be tagged as verified_source."
                ),
                "inputSchema": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "query": {"type": "string"},
                        "law_name": {"type": "string"},
                        "article_numbers": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                        "live_lookup": {
                            "type": "boolean",
                            "description": "When true, calls korean-law-mcp via npx. Defaults to false.",
                        },
                    },
                },
            },
            {
                "name": "kr_legal_review",
                "description": (
                    "Build a provider-neutral Korean legal review payload for a question, "
                    "document, or business situation. The client LLM performs the final drafting."
                ),
                "inputSchema": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "question": {"type": "string"},
                        "document_text": {"type": "string"},
                        "matter_context": {"type": "string"},
                        "preset": {
                            "type": "string",
                            "enum": [
                                "general",
                                "privacy",
                                "commercial_contract",
                                "employment",
                                "corporate",
                                "tax",
                                "regulatory",
                                "litigation",
                            ],
                        },
                    },
                },
            },
        ]
    }


def kr_legal_source_search(arguments: dict[str, Any]) -> dict[str, Any]:
    query = str(arguments.get("query") or arguments.get("law_name") or "").strip()
    law_name = str(arguments.get("law_name") or query or "").strip()
    article_numbers = arguments.get("article_numbers") or []
    live_lookup = bool(arguments.get("live_lookup", False))

    response: dict[str, Any] = {
        "status": "planned",
        "source_connector": "korean-law-mcp",
        "query": query,
        "law_name": law_name,
        "article_numbers": article_numbers,
        "source_status_rules": SOURCE_STATUS_RULES,
        "lookup_plan": DEFAULT_SOURCE_PLAN,
        "review_gate": "requires_professional_review",
    }

    if not live_lookup:
        response["note"] = "Set live_lookup=true and LAW_OC to retrieve live law text."
        return _content(response)

    live_results: list[dict[str, Any]] = []
    if query:
        live_results.append(_run_korean_law_mcp(["search_law", "--query", query, "--display", "5"]))
    for article in article_numbers:
        if law_name:
            live_results.append(
                _run_korean_law_mcp(["get_law_text", "--law", law_name, "--article", str(article)])
            )
    response["status"] = "retrieved"
    response["live_results"] = live_results
    return _content(response)


def kr_legal_review(arguments: dict[str, Any]) -> dict[str, Any]:
    preset = str(arguments.get("preset") or "general")
    question = str(arguments.get("question") or "").strip()
    document_text = str(arguments.get("document_text") or "").strip()
    matter_context = str(arguments.get("matter_context") or "").strip()

    skill_text = _read_optional(GENERAL_REVIEW_WORKFLOW)
    playbook_text = ""
    if preset == "privacy":
        skill_text = _read_optional(PRIVACY_REVIEW_SKILL)
        playbook_text = _read_optional(PRIVACY_PLAYBOOK)

    payload = {
        "workflow": "kr_legal_review",
        "audience": "legal non-specialist, company operator, or individual preparing a question for counsel",
        "preset": preset,
        "question": question,
        "document_text": document_text,
        "matter_context": matter_context,
        "source_lookup_plan": DEFAULT_SOURCE_PLAN,
        "source_status_rules": SOURCE_STATUS_RULES,
        "output_contract": {
            "verdict": "pass / conditional / fail / unknown",
            "issue_summary": "plain Korean summary of what matters",
            "required_gaps": "blocking facts, documents, or source lookups needed before reliance",
            "recommended_next_steps": "practical next actions for the business user",
            "source_log": "retrieved sources and whether each point is verified_source/model_inference",
            "review_gate": "requires_professional_review",
        },
        "llm_instruction": (
            "Use the returned workflow material to draft a practical Korean legal issue memo. "
            "Do not present the output as legal advice or a final legal conclusion. "
            "When source text is missing, say what must be checked instead of inventing citations."
        ),
        "workflow_materials": {
            "skill": skill_text,
            "playbook": playbook_text,
        },
    }
    return _content(payload)


def call_tool(params: dict[str, Any]) -> dict[str, Any]:
    name = params.get("name")
    arguments = params.get("arguments") or {}
    if name == "kr_legal_source_search":
        return kr_legal_source_search(arguments)
    if name == "kr_legal_review":
        return kr_legal_review(arguments)
    raise KeyError(str(name))


def handle(request: dict[str, Any]) -> dict[str, Any] | None:
    method = request.get("method")
    request_id = request.get("id")

    try:
        if method == "initialize":
            return _jsonrpc_result(
                request_id,
                {
                    "protocolVersion": "2024-11-05",
                    "serverInfo": {"name": "claude-for-legal-kr", "version": "0.1.0"},
                    "capabilities": {"tools": {}},
                },
            )
        if method == "notifications/initialized":
            return None
        if method == "tools/list":
            return _jsonrpc_result(request_id, list_tools())
        if method == "tools/call":
            return _jsonrpc_result(request_id, call_tool(request.get("params") or {}))
        return _jsonrpc_error(request_id, -32601, f"Method not found: {method}")
    except KeyError as exc:
        return _jsonrpc_error(request_id, -32602, f"Unknown tool: {exc}")
    except Exception as exc:  # pragma: no cover - defensive JSON-RPC boundary
        return _jsonrpc_error(request_id, -32000, str(exc))


def main() -> int:
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        response = handle(json.loads(line))
        if response is None:
            continue
        print(json.dumps(response, ensure_ascii=False), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
