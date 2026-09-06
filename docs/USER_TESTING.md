# ManakAI usability testing guide

Use this guide with teammates or prospective users who did not build the product. The goal is to discover where the interface is unclear, not to teach participants the “correct” clicks. Run the session on staging with a phone or laptop and reserve about 25 minutes.

## Before the session

1. Confirm the frontend and API readiness checks pass.
2. Use a fresh private/incognito window so a recent compliance profile does not affect the test.
3. Tell the participant ManakAI is a prototype, not legal advice, and ask them not to enter personal information, customer documents, API keys, or confidential product data.
4. Ask them to think aloud. Do not explain the interface unless they are blocked for more than two minutes.
5. Record observations without names or unnecessary personal information.

## Tasks

Give one task at a time. Do not read the success criteria aloud.

| # | Participant task | Suggested input/context | Success criteria |
| --- | --- | --- | --- |
| 1 | Find out what may apply to a household electric kettle you manufacture. | “I manufacture a 1500 W electric kettle for household use in India.” Choose the participant’s actual enterprise size if known. | Starts from the dashboard, reaches a result, and can state the product class, standard, status/date, uncertainty, and next action. |
| 2 | Try a product ManakAI does not cover. | “Electric iron for household use.” | Recognises that ManakAI did not guess and identifies a useful next step. |
| 3 | Enter an ambiguous product. | “Helmet.” | Understands why more detail is required and does not treat a guessed standard as authoritative. |
| 4 | Find a laboratory and judge whether it can be relied upon today. | Use Find testing; search for the kettle standard or a visible standard. | Checks scope, recognition status/date, and source rather than relying only on the lab name. |
| 5 | Ask a follow-up in Hinglish. | “Is standard ka status kya hai aur next step kya hoga?” after establishing product context. | Gets or requests sufficient context, can find the evidence, and identifies AI versus rules-based fallback. |
| 6 | Explain how you would verify a jewellery HUID. | Use Consumer help with a sample format such as `ABC123`; do not use a real personal purchase if avoidable. | Understands that ManakAI only explains the process and opens the official BIS route for actual verification. |
| 7 | Explain why a standard was selected. | From a supported product result, open the compliance plan and evidence. | Finds “Why?”, regulatory basis, source URL, date/status, and warnings without assistance. |
| 8 | Repeat a core task on a phone-sized screen. | Product analysis or compliance journey. | Completes the task without horizontal scrolling, hidden controls, or inaccessible evidence. |

## Observation sheet

Create one row per task. Time is approximate; confusion matters more than speed.

| Participant code | Device | Task | Completed without help? | Time | Wrong turns / confusion | Words the participant expected | Comments |
| --- | --- | --- | --- | --- | --- | --- | --- |
| P01 | Mobile/Desktop | 1–8 | Yes / With help / No | mm:ss |  |  |  |

Do not count a backend refusal or explicit unsupported result as a failure when that is the safe, intended outcome. Do count it as a failure when the participant interprets “unsupported” as “no BIS rules exist”.

## Questions after the tasks

Ask these without suggesting an answer:

1. In one sentence, what does ManakAI do?
2. Which part of the result would you act on first?
3. What information felt official, and why?
4. Where did you feel unsure or distrustful?
5. Did you know whether an answer came from AI or from stored rules?
6. What did you expect the product to do that it did not do?
7. Would you rely on this result without checking the linked BIS source? Why?

## Release signals

For a small staging round of five participants, aim for:

- at least four can begin Product Analyser without help;
- at least four can identify What applies, Status/When, and the next action;
- all five understand that unsupported coverage is not proof that no regulation exists;
- all five understand that HUID is verified in the official BIS service, not ManakAI;
- at least four can find source evidence and distinguish an AI explanation from fallback;
- no participant encounters a dead primary action or an unrecoverable screen.

Treat repeated confusion by two or more participants as a high-priority UX defect. Capture the smallest interface or copy change that addresses the observed problem, retest it, and link the result in `UX_AUDIT.md`.
