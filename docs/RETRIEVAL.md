# Retrieval

The production target is hybrid evidence retrieval:

1. Detect language and normalise the query while preserving standard numbers and statutory terms.
2. Apply metadata filters for number, document type, status, version, product category, QCO and scheme.
3. Run lexical/BM25 and vector retrieval in parallel.
4. Fuse candidate ranks and rerank against the question.
5. Prefer current authoritative records using version/effective-date precedence.
6. Select only evidence that can support the claim.
7. Generate an explanation in the user’s language with citations.

The prototype implements deterministic keyword retrieval over structured fixtures. When no authoritative chunk exists, the API returns the required boundary: “I could not verify this requirement from the available authorised BIS sources.”

No standard corpus is translated and stored. Hindi/Hinglish requests should become canonical retrieval queries; the answer may be translated only after evidence selection.
