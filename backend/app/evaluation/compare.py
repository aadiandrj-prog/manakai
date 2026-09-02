from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare completed ManakAI provider evaluation reports")
    parser.add_argument("reports", nargs="+")
    args = parser.parse_args()
    reports = [json.loads(Path(path).read_text(encoding="utf-8")) for path in args.reports]
    ranked = sorted(reports, key=lambda item: (-item["summary"]["pass_rate"], item["summary"]["fallback_rate"], item["summary"]["p95_latency_ms"]))
    for report in ranked:
        summary = report["summary"]
        print(f"{report['provider']} ({report.get('model') or 'default'}): pass={summary['pass_rate']:.1%}, fallback={summary['fallback_rate']:.1%}, p95={summary['p95_latency_ms']}ms")
    print(f"Recommended on measured reliability: {ranked[0]['provider']} ({ranked[0].get('model') or 'default'})")


if __name__ == "__main__":
    main()
