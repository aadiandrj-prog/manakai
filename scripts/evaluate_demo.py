#!/usr/bin/env python3
"""Small deterministic smoke benchmark for the demo orchestrator."""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.services.intent import classify_intent  # noqa: E402


def main() -> int:
    cases = json.loads((ROOT / "data/fixtures/evaluation.json").read_text())
    passed = 0
    for case in cases:
        actual = classify_intent(case["query"]).value
        ok = actual == case["expected_intent"]
        passed += int(ok)
        print(f"{'PASS' if ok else 'FAIL'} {case['id']}: {actual}")
    print(f"{passed}/{len(cases)} intent checks passed")
    return 0 if passed == len(cases) else 1


if __name__ == "__main__":
    raise SystemExit(main())
