# Compliance engine

Legal status is a structured decision, not a model prediction. `evaluate_certification` accepts a QCO record, evaluation date and source-verification flag.

```text
missing or unverified source  -> UNVERIFIED
verified active QCO, effective -> MANDATORY
verified QCO, future date      -> UPCOMING
otherwise                      -> NOT_MANDATORY_FROM_THIS_QCO
```

The last outcome is deliberately narrow: it does not mean the product is universally voluntary; it only means that one evaluated QCO did not make it mandatory. Additional rules may still apply.

Rules should be versioned data with conditions, outcome, priority, source citation and effective interval. Every decision event should record the evaluated rule IDs and source versions.

For S.O. 1739(E), the engine selects an implementation row using product category and enterprise category, then compares it with `as_of_date`. Before notification the status is `UNKNOWN`; between notification and implementation it is `UPCOMING`; on/after implementation it is `ACTIVE` and produces `MANDATORY`. Superseded/withdrawn instruments never become active.

The kettle explanation graph is constructed from stored relationships. It shows classification, product-specific/general standards, QCO notification, enterprise date, query date and result. Rated voltage remains an explicit uncertainty because the QCO contains voltage limits while the example states only 1500 W.

## Multi-vertical resolution

Phase 2E first resolves an explicit coverage record. `UNSUPPORTED` and ambiguous products produce no standard or mandatory claim. For supported categories the same algorithm loads the primary standard, picks the latest instrument notified on or before `as_of_date`, evaluates its effective interval, selects the stored regulatory regime and builds the explanation/journey from structured relationships.

Phase 3B requires that record to be `PUBLISHED`. Classification comes from the product-family registry rather than route-specific conditions. A broad cross-family term returns candidates and missing attributes. Metadata-only or conflict records can expose a standard while withholding the QCO edge; in that state the engine returns `UNVERIFIED` instead of converting a source listing into a legal conclusion.

Historical instruments may be stored as `SUPERSEDED` today while still having been active on an earlier query date. The engine therefore compares the successor notification date with the query date before applying superseded status. Pressure-cooker history prefers IS 2347:2023 for current queries while retaining IS 2347:2017. Hallmarking resolves the 2020/2021/2023/2026 instrument chain and never treats Scheme I as the hallmarking workflow.
