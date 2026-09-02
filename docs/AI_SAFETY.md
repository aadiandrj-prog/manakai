# AI safety and regulatory trust

## Trust hierarchy

1. Validated PostgreSQL regulatory records and deterministic temporal/compliance rules.
2. Citation-validated retrieved evidence.
3. Structured application state and answer package.
4. Provider-generated wording.
5. Untrusted user input and retrieved document text.

An LLM cannot create or override an applicable standard, QCO, status, effective date, mandatory status, certification scheme, recognised laboratory, standard revision or citation identifier.

## Injection boundary

User messages, PDF text, scraped HTML and retrieved chunks are labelled untrusted in provider prompts. Instructions inside them are data, not system instructions. The provider receives no compliance-writing tool and no direct database access. Requests such as “ignore your database” cause the unchanged deterministic profile to be rerun.

## Post-generation checks

`GeneratedAnswerValidator` rejects unknown evidence IDs, unsupported IS identifiers and QCO status language that contradicts the structured result. The structured UI renders standards, QCO, scheme, laboratories, warnings and citations directly from the API package, never by parsing generated prose. Invalid, malformed, unavailable or timed-out generation falls back to deterministic English/Hindi/Hinglish templates.

## Operational boundary

Prompts and logs exclude API keys and hidden reasoning. Logs record only events and bounded operational metadata. Staging adds model allow-lists, input/evidence/output bounds, a daily call cap, anonymous endpoint limits and persistent usage/validation telemetry. The limiter is process-local and assumes one API instance; horizontal scale requires a shared limiter plus approved retention and provider data-use policies.
