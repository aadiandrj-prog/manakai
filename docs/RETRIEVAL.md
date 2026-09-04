# Retrieval

The production target is hybrid evidence retrieval:

1. Detect language and normalise the query while preserving standard numbers and statutory terms.
2. Apply metadata filters for number, document type, status, version, product category, QCO and scheme.
3. Run lexical/BM25 and vector retrieval in parallel.
4. Fuse candidate ranks and rerank against the question.
5. Prefer current authoritative records using version/effective-date precedence.
6. Select only evidence that can support the claim.
7. Generate an explanation in the user’s language with citations.

Phase 2B implements this pipeline. PostgreSQL uses a GIN full-text index and an HNSW cosine index over `vector(384)`. SQLite tests use deterministic fallbacks. Reciprocal-rank fusion combines lexical and vector candidates; exact standard and clause matches receive a deterministic boost.

Embeddings are disabled by default. `sentence-transformers/all-MiniLM-L6-v2` is the 384-dimensional local option and is lazy-loaded only for an explicit embeddings command. Without it, lexical/exact retrieval remains available and startup downloads nothing.

`CitationValidationService` checks document existence, current status, chunk ownership and claim/evidence overlap. Failed citations are marked `INVALID` and withheld. When no authoritative chunk exists, the API returns the verification boundary.

No standard corpus is translated and stored. Hindi/Hinglish requests should become canonical retrieval queries; the answer may be translated only after evidence selection.

Phase 2E applies the same hybrid retrieval pipeline to all covered verticals. Metadata filtering includes the coverage category and current document status. Exact identifiers (`IS 4151`, `IS 269`, `IS 2347`, `IS 1417`) continue to outrank embeddings. Superseded product manuals remain queryable for history but are rejected when a current citation is required. Hallmarking guidance is retrieved from its own authoritative document type; the retriever cannot turn a HUID string into a verification result.
