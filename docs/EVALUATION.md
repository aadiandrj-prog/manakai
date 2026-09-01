# Phase 2C evaluation

The benchmark fixture is `backend/tests/fixtures/phase2c_benchmark.json`. CI uses deterministic and recorded providers; it never calls a paid provider.

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
