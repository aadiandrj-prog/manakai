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
