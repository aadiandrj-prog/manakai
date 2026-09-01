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
