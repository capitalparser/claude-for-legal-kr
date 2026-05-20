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
LEGAL_REVIEW_MEMO_TEMPLATE = ROOT / "references" / "korea" / "legal-review-memo-template.md"
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
                        "output_style": {
                            "type": "string",
                            "enum": ["legal_review_memo_ko", "internal_json"],
                            "description": (
                                "Defaults to legal_review_memo_ko, a Korean legal review memo "
                                "for non-lawyer business users."
                            ),
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


def _first_line_or_empty(text: str, limit: int = 160) -> str:
    normalized = " ".join(text.split())
    if not normalized:
        return ""
    if len(normalized) <= limit:
        return normalized
    return normalized[: limit - 1].rstrip() + "..."


def _display_source_table() -> str:
    return (
        "| 구분 | 법령/자료 | 조문/식별자 | 확인상태 | 비고 |\n"
        "|---|---|---|---|---|\n"
        "| 법령 | 관련 한국 법령 | 미특정 | 미조회 | `kr_legal_source_search`로 우선 조회 필요 |\n"
        "| 사실관계 | 사용자 제공 내용 | 질문/문서/맥락 | 사용자 제공 | 원문 및 사실관계 확인 필요 |\n"
    )


def _build_legal_review_memo(
    *,
    question: str,
    document_text: str,
    matter_context: str,
    preset: str,
) -> str:
    issue = question or "사용자가 제공한 문서 또는 업무 상황에 관한 법무 검토"
    document_summary = _first_line_or_empty(document_text) or "구체적인 문서 원문은 제공되지 않음."
    context_summary = _first_line_or_empty(matter_context) or "구체적인 업무 배경은 제공되지 않음."

    return f"""# 법률검토 내역서

## 1. 검토 결론
현재 제공된 자료만으로는 최종 법률 판단을 확정하기 어려움. 다만 본 사안은 `{preset}` 영역의 법무 검토가 필요한 사안으로 보이며, 관련 한국 법령 조회와 사실관계 보완 후 법무팀 또는 변호사 검토를 거치는 것이 바람직함.

## 2. 사안의 개요
사용자는 다음 사안에 관하여 법무 검토 전 쟁점 정리를 요청함.

- 질의: {issue}
- 업무 배경: {context_summary}
- 문서 요약: {document_summary}

## 3. 질의의 취지
본 검토는 사용자가 계약 체결, 내부 의사결정, 외부 발송 또는 실행 전에 확인해야 할 법무 쟁점과 추가 확인자료를 정리하기 위한 것임. 최종 법률의견이 아니라 법무팀 또는 변호사에게 전달할 1차 검토 내역서 초안임.

## 4. 검토 대상 및 전제사실
- 검토 대상 문서: {document_summary}
- 관련 업무: {context_summary}
- 당사자: 사용자 제공 정보만으로는 특정되지 않음.
- 확인된 사실: 사용자가 입력한 질의와 업무 배경.
- 미확인 사실: 계약 상대방, 적용 법령, 거래 구조, 문서 전문, 관할, 일정, 금액, 개인정보ㆍ근로자ㆍ소비자 등 보호대상 포함 여부.

## 5. 관련 법령 및 확인 근거
{_display_source_table()}

## 6. 주요 쟁점별 검토
### 쟁점 1. 적용 법령 및 규제 영역 특정
**검토의견:**  
현재 입력만으로는 적용 법령을 단정하기 어려우므로, 먼저 사안의 법률 영역과 관련 법령을 특정해야 함. 계약, 개인정보, 노무, 소비자, 표시광고, 전자상거래, 회사법, 세무, 인허가 규제 중 어느 영역에 해당하는지 확인이 필요함.

**근거:**  
현재 단계에서는 법령 원문이 조회되지 않았으므로 `verified_source`가 아니라 `model_inference` 및 `user_supplied_unverified` 단계의 검토임.

**위험도:** 판단 유보

**보완 필요사항:**  
`kr_legal_source_search`를 통해 관련 법령과 조문을 실제 조회하고, 조회된 근거를 기준으로 쟁점을 다시 정리해야 함.

### 쟁점 2. 사실관계 및 문서 누락
**검토의견:**  
법률 검토는 사실관계와 문서 문언에 따라 결론이 달라질 수 있음. 현재 제공된 정보만으로는 체결 가능 여부, 위법 여부, 신고 필요 여부, 분쟁 가능성을 확정할 수 없음.

**근거:**  
문서 전문, 당사자 지위, 거래 구조, 이행 방식, 대상자 범위, 대외 발송 여부가 확인되지 않음.

**위험도:** 중간

**보완 필요사항:**  
계약서 또는 문서 전문, 관련 일정, 당사자, 업무 목적, 처리 데이터 또는 금전 흐름, 기존 내부 정책을 추가로 확인해야 함.

## 7. 필수 보완사항
계약 체결, 발송, 제출, 실행 전에 반드시 확인해야 할 사항:
1. 관련 법령 및 조문을 실제 조회하여 근거를 확보할 것.
2. 검토 대상 문서 전문 또는 핵심 조항을 확보할 것.
3. 당사자 지위, 거래 구조, 일정, 금액, 대상자 범위 등 핵심 사실관계를 정리할 것.
4. 법무팀 또는 변호사에게 최종 검토를 요청할 것.

## 8. 권고사항
필수는 아니지만 분쟁 예방 또는 내부통제상 권장되는 사항:
1. 법무팀 전달용으로 `사실관계`, `질문`, `관련 문서`, `희망 일정`을 한 번에 정리할 것.
2. 법령 조회 결과와 모델 추론을 구분하여 기록할 것.
3. 상대방에게 바로 발송하기 전 내부 검토 이력을 남길 것.

## 9. 법무팀/변호사에게 전달할 질문
1. 본 사안에서 우선 확인해야 할 한국 법령과 조문은 무엇인지?
2. 현재 문서 또는 업무 방식에서 반드시 수정해야 할 조항이나 절차가 있는지?
3. 계약 체결, 대외 발송, 신고, 내부 승인 전에 추가로 확보해야 할 자료는 무엇인지?
4. 본 사안의 위험도는 높음/중간/낮음 중 어디에 해당하며, 그 이유는 무엇인지?

## 10. 종합 의견
현재 자료 기준으로는 법률상 최종 결론을 확정하기 어렵고, 관련 법령 조회와 사실관계 보완이 선행되어야 함. 다만 사용자가 법무팀 또는 변호사에게 질의하기 전 단계에서는 위 필수 보완사항과 질문 목록을 기준으로 자료를 정리하는 것이 적절함.

## 11. 검토 한계 및 주의문구
본 문서는 AI가 작성한 법률검토 초안이며, 법률자문 또는 최종 법률의견이 아님. 외부 제출, 계약 체결, 분쟁 대응, 신고, 고소ㆍ고발, 행정기관 제출 전에는 변호사 등 전문가 검토가 필요함.
"""


def kr_legal_review(arguments: dict[str, Any]) -> dict[str, Any]:
    preset = str(arguments.get("preset") or "general")
    output_style = str(arguments.get("output_style") or "legal_review_memo_ko")
    question = str(arguments.get("question") or "").strip()
    document_text = str(arguments.get("document_text") or "").strip()
    matter_context = str(arguments.get("matter_context") or "").strip()

    skill_text = _read_optional(GENERAL_REVIEW_WORKFLOW)
    playbook_text = ""
    if preset == "privacy":
        skill_text = _read_optional(PRIVACY_REVIEW_SKILL)
        playbook_text = _read_optional(PRIVACY_PLAYBOOK)

    machine_readable = {
        "verdict": "unknown",
        "issue_summary": "Korean legal review memo draft; source lookup and professional review required.",
        "required_gaps": [
            "Retrieve relevant Korean law or official guidance before claiming verified_source.",
            "Collect the full document text and missing matter facts.",
            "Route final conclusion to counsel or a responsible professional.",
        ],
        "recommended_next_steps": [
            "Use kr_legal_source_search for source lookup.",
            "Convert the display document into an internal legal intake memo.",
        ],
        "source_log": [],
        "review_gate": "requires_professional_review",
    }

    payload = {
        "workflow": "kr_legal_review",
        "audience": "legal non-specialist, company operator, or individual preparing a question for counsel",
        "preset": preset,
        "output_style": output_style,
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
            "legal_review_memo_template": _read_optional(LEGAL_REVIEW_MEMO_TEMPLATE),
            "playbook": playbook_text,
        },
        "machine_readable": machine_readable,
    }

    if output_style == "legal_review_memo_ko":
        payload["display_document"] = _build_legal_review_memo(
            question=question,
            document_text=document_text,
            matter_context=matter_context,
            preset=preset,
        )

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
