# Demo guide

Start with `DEMO_MODE=true` and no provider key.

## Scenario A — manufacturer

Open **Product analyser**, keep “portable rechargeable LED emergency lamp,” and analyse. Show the interpreted attributes, candidate standard, explicit QCO verification gap, then open the compliance profile. Walk through the evidence register and six-stage journey.

## Scenario B — technical question

Open **Ask ManakAI** and retrieve the seeded emergency-luminaire question. Point out that tests are structured cards, the source is marked demo metadata, and the assistant refuses to invent clause numbers.

## Scenario C — consumer

Open **Consumer help**, enter any six-character demo HUID and show the verification sequence. The app explains how to use an official service but does not pretend it performed a live lookup.

## Reset and failure behaviour

The demo is stateless and deterministic. No network or model call is required. Empty searches, invalid HUID length, unknown records and unanswerable questions all have bounded states.
