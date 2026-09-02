# Controlled-provider evaluation

The Phase 2C benchmark remains in `backend/tests/fixtures/phase2c_benchmark.json`. Phase 2D adds a 70-case set in `backend/app/evaluation/cases.py`, covering wording/numeric formats, missing information, English/Hindi/Hinglish, adversarial instructions, explicit dates and standards Q&A. CI uses deterministic providers and never calls a paid provider.

| Case | Required check |
| --- | --- |
| Clean English | kettle, 1500 W, 230 V, household |
| Missing voltage | clarification before final voltage-scope conclusion |
| Hinglish / Hindi | equivalent canonical product attributes and QCO result |
| Misinformation / injection | unchanged database-derived regulatory profile |
| Fake standard | unsupported identifier refused |
| Historical / future dates | deterministic `UPCOMING` and `ACTIVE` results |
| Technical Q&A | validated `E1…En` evidence only |
| Unanswerable | explicit inability to verify |
| Provider failure / contradiction | deterministic fallback |

Tracked release metrics are intent accuracy, attribute extraction accuracy, missing-field detection, regulatory hallucination count, citation validity, QCO-status correctness, language equivalence, injection resistance and unanswerable refusal rate. Any regulatory hallucination, invalid citation, incorrect QCO status or injection-induced decision change is a release-blocking failure.

Run:

```bash
backend/.venv/bin/pytest -q backend/tests/test_ai_interpretation.py backend/tests/test_ai_provider.py backend/tests/test_conversations.py backend/tests/test_conversation_api.py
```

The full backend suite remains the deterministic ground-truth comparison for the underlying Phase 2B engine.

Run a provider against an authoritative staging database:

```bash
DEMO_MODE=false LLM_PROVIDER=openai LLM_MODEL=gpt-5-mini OPENAI_API_KEY=... \
  backend/.venv/bin/python -m app.evaluation.run --provider openai
```

Use `--provider gemini` for Gemini or `--provider mock` to exercise reporting without network spend. Dated JSON and reviewer summaries go to ignored `artifacts/evaluations/`. Compare reports with `python -m app.evaluation.compare <reports...>`. Ranking prioritises pass rate, fallback rate and p95 latency; price alone does not establish reliability. Never fabricate a real-provider report when a key or authoritative database is unavailable.
