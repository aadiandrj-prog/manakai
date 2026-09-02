# Controlled AI layer

Phase 2C adds a language layer around, not inside, the regulatory decision engine.

```text
untrusted user message
→ deterministic intent/language/explicit-value extraction
→ optional schema-validated provider interpretation
→ structured conversation state
→ deterministic compliance or hybrid retrieval service
→ immutable RegulatoryAnswerPackage
→ optional schema-validated explanation
→ critical-fact and evidence-ID validation
→ provider answer or deterministic fallback
```

## Provider boundary

`AIProvider` is the only provider-facing interface. `OpenAIProvider` uses the Responses API with JSON Schema output. `GeminiProvider` uses `generateContent` with a JSON response schema. Both validate every response through Pydantic and share bounded timeouts, retry counts and output-token limits. Provider code cannot access repositories directly.

Configuration:

```text
LLM_PROVIDER=disabled|openai|gemini
LLM_MODEL=
OPENAI_API_KEY=
GEMINI_API_KEY=
AI_TIMEOUT_SECONDS=12
AI_MAX_RETRIES=1
AI_MAX_OUTPUT_TOKENS=700
AI_DAILY_REQUEST_LIMIT=500
AI_MAX_INPUT_CHARS=12000
AI_MAX_EVIDENCE_CHARS=8000
OPENAI_ALLOWED_MODELS=gpt-5-mini,gpt-5.4-mini
GEMINI_ALLOWED_MODELS=gemini-3.6-flash,gemini-3.7-flash
```

No key is required. `disabled` is the safe default and uses deterministic interpretation and answer templates.

Staging records provider/model, operation, latency, available tokens and validation outcome without storing secrets or prompt bodies. A model outside its allow-list is rejected. Daily call and input/evidence/output bounds protect the anonymous prototype from unbounded spend.

## Structured state

Machine-consumed AI output is validated as `IntentClassification`, `ProductExtraction`, `ClarificationDecision`, `ConversationInterpretation` or `GeneratedAnswer`. Unknown product values remain null. Numeric regulatory inputs extracted deterministically from explicit text override model output.

Conversations store language, current intent, structured product attributes, unresolved attributes, active compliance profile, relevant standard, evidence references and recent user/assistant messages. They do not store chain-of-thought or long-term vector memory.

## Evidence IDs and answer packages

Each answer package assigns `E1`, `E2`, and so on to already validated citations. The model can return only these IDs. The API expands them into canonical document title, URL, standard, page, clause, dates and status. Unknown IDs make generation invalid and trigger a deterministic fallback.

Only the relevant structured profile and top evidence metadata enter a model prompt. Full documents, the complete database and unrelated conversation history are excluded.

## Multilingual path

English, Hindi Devanagari and Hinglish Latin script share the same structured product state and regulatory engine. Translated explanations preserve IS identifiers, notification numbers, dates and scheme names. An explicit language selection overrides automatic detection.
