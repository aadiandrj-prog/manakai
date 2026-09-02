from __future__ import annotations

import argparse
import json
import statistics
import time
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import func, select

from ..config import settings
from ..database import SessionLocal
from ..db_models import SourceRecord
from ..schemas import SourceKind
from ..services.ai_provider import GeminiProvider, MockProvider, OpenAIProvider
from ..services.conversations import ConversationService
from .cases import CASES, EvaluationCase


def _provider(name: str):
    if name == "mock":
        return MockProvider()
    if name == "openai":
        return OpenAIProvider(settings)
    if name == "gemini":
        return GeminiProvider(settings)
    raise ValueError(f"Unsupported evaluation provider: {name}")


def _check(case: EvaluationCase, response) -> dict[str, bool | None]:
    profile = response.compliance_profile
    product = profile.product.structured_attributes if profile else {}
    answer_folded = response.answer.casefold()
    refusal = "cannot verify" in answer_folded or "पुष्टि नहीं" in response.answer or "verify nahi" in answer_folded
    cited = {item.evidence_id for item in response.evidence}
    referenced = {token.rstrip("]") for token in response.answer.split("[")[1:] for token in [token.split()[0]] if token.startswith("E")}
    checks: dict[str, bool | None] = {
        "intent": response.intent.value == case.expected_intent,
        "language": response.language.value == case.expected_language,
        "product_type": None if case.expected_product_type is None else product.get("product_type") == case.expected_product_type,
        "voltage": None if case.expected_voltage_v is None else product.get("rated_voltage_v") == case.expected_voltage_v,
        "power": None if case.expected_power_w is None else product.get("rated_power_w") == case.expected_power_w,
        "intended_use": None if case.expected_use is None else product.get("intended_use") == case.expected_use,
        "missing_fields": None if not case.expected_missing else set(case.expected_missing).issubset(response.unresolved_attributes),
        "qco_status": None if case.expected_qco_status is None else bool(profile and profile.qco and profile.qco.status.value == case.expected_qco_status),
        "refusal": None if not case.should_refuse else refusal,
        "citations_resolve": not referenced or referenced.issubset(cited),
        "no_invented_standard": "IS 99999 applies" not in response.answer and "IS 88888 applies" not in response.answer,
    }
    return checks


def run(provider_name: str, cases: list[EvaluationCase]) -> dict:
    if settings.demo_mode:
        raise RuntimeError("Evaluation requires DEMO_MODE=false and an authoritative database")
    provider = _provider(provider_name)
    rows = []
    with SessionLocal() as session:
        source_count = session.scalar(select(func.count()).select_from(SourceRecord).where(SourceRecord.verification_status == "AUTHORITATIVE")) or 0
        if source_count == 0:
            raise RuntimeError("No authoritative source records are available")
        service = ConversationService(session, provider)
        for case in cases:
            started = time.perf_counter()
            error = None
            response = None
            try:
                conversation = service.create(case.expected_language)
                if case.prelude:
                    service.message(conversation.conversation_id, case.prelude, case.expected_language)
                response = service.message(conversation.conversation_id, case.query, case.expected_language)
                checks = _check(case, response)
            except Exception as exc:  # reports failures without aborting a paid evaluation run
                session.rollback()
                error = f"{type(exc).__name__}: {exc}"
                checks = {"request_succeeded": False}
            elapsed_ms = (time.perf_counter() - started) * 1000
            active = [value for value in checks.values() if value is not None]
            rows.append({
                "case": asdict(case), "latency_ms": round(elapsed_ms, 2), "checks": checks,
                "passed": bool(active) and all(active), "error": error,
                "observed": None if response is None else {
                    "intent": response.intent.value, "language": response.language.value,
                    "clarification_required": response.clarification_required,
                    "unresolved_attributes": response.unresolved_attributes,
                    "provider": response.provider, "used_fallback": response.used_fallback,
                    "qco_status": response.compliance_profile.qco.status.value if response.compliance_profile and response.compliance_profile.qco else None,
                    "evidence_ids": [item.evidence_id for item in response.evidence], "answer": response.answer,
                },
            })
    latencies = [row["latency_ms"] for row in rows]
    passed = sum(row["passed"] for row in rows)
    fallback = sum(bool(row["observed"] and row["observed"]["used_fallback"]) for row in rows)
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(), "provider": provider_name,
        "model": provider.model, "data_mode": SourceKind.AUTHORITATIVE.value,
        "summary": {
            "cases": len(rows), "passed": passed, "failed": len(rows) - passed,
            "pass_rate": round(passed / len(rows), 4), "fallback_rate": round(fallback / len(rows), 4),
            "mean_latency_ms": round(statistics.mean(latencies), 2),
            "median_latency_ms": round(statistics.median(latencies), 2),
            "p95_latency_ms": round(sorted(latencies)[max(0, int(len(latencies) * .95) - 1)], 2),
        },
        "results": rows,
    }


def _markdown(report: dict) -> str:
    summary = report["summary"]
    failures = [row for row in report["results"] if not row["passed"]]
    lines = [
        f"# ManakAI provider evaluation — {report['provider']}", "",
        f"Generated: {report['generated_at']}", "",
        f"- Cases: {summary['cases']}", f"- Passed: {summary['passed']} ({summary['pass_rate']:.1%})",
        f"- Fallback rate: {summary['fallback_rate']:.1%}",
        f"- Latency (mean / median / p95): {summary['mean_latency_ms']} / {summary['median_latency_ms']} / {summary['p95_latency_ms']} ms",
        "", "## Failures", "",
    ]
    if not failures:
        lines.append("None.")
    for row in failures:
        failed = ", ".join(key for key, value in row["checks"].items() if value is False)
        lines.append(f"- `{row['case']['id']}`: {failed or row['error'] or 'unknown'}")
    lines += ["", "This report measures the controlled language layer. It does not independently certify legal correctness.", ""]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the controlled AI evaluation set")
    parser.add_argument("--provider", choices=("mock", "openai", "gemini"), required=True)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--output-dir", default="artifacts/evaluations")
    args = parser.parse_args()
    selected = CASES[: args.limit] if args.limit else CASES
    report = run(args.provider, selected)
    target = Path(args.output_dir)
    target.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    base = target / f"{stamp}-{args.provider}"
    base.with_suffix(".json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    base.with_suffix(".md").write_text(_markdown(report), encoding="utf-8")
    print(json.dumps({"report": str(base.with_suffix('.json')), **report["summary"]}, indent=2))


if __name__ == "__main__":
    main()
