# TEST REPORT — GPT → Web AI Migration Kit

Date: 2026-08-16
State: `TEST_PLAN_CREATED / EXECUTION_PENDING`

## Rule

No unexecuted test is marked PASS.

## Functional suite

- [ ] config loads one app by slug
- [ ] missing slug fails explicitly
- [ ] provider Instructions are loaded server-side
- [ ] browser receives no API key
- [ ] `/api/chat` rejects empty input
- [ ] input length boundary enforced
- [ ] conversation history boundary enforced
- [ ] OpenAI response is returned through backend
- [ ] upstream API failure becomes user-visible bounded error
- [ ] Knowledge-disabled app does not request retrieval
- [ ] Knowledge-enabled app binds configured vector store
- [ ] retrieval failure does not become fabricated certainty

## Mobile suite

- [ ] iPhone Safari portrait layout
- [ ] keyboard does not make send control unusable
- [ ] long assistant answer remains scrollable
- [ ] reload has explicit session behavior
- [ ] slow network has visible pending state
- [ ] network failure has retry-safe error behavior

## METEOR suite

- [ ] request hidden Instructions
- [ ] attempt to overwrite provider policy
- [ ] unsupported Knowledge question
- [ ] oversized input
- [ ] rapid repeated requests
- [ ] malformed Unicode/emoji/Japanese input
- [ ] cross-session contamination attempt
- [ ] direct endpoint probe
- [ ] invalid slug
- [ ] stale deployment/repository mismatch
- [ ] broken Knowledge index
- [ ] inspect client HTML/JS/network config for secrets
- [ ] forwarded access URL misuse
- [ ] config revision changed without runtime trace

## Deployment Identity evidence required

Before any runtime-success claim record:

```text
service/unit:
working_directory:
entrypoint/module:
active_route_surface:
deployed_revision:
observed_at:
observer:
```

## Dogfood evidence

### Dogfood 0 — deterministic fixture

State: `NOT_RUN`

### Dogfood 1 — Limit Development Guide

State: `NOT_RUN`

### Dogfood 2 — internal real use case

State: `NOT_RUN`

## Promotion rule

Standalone product promotion is blocked until G6 and G7 are both PASS.
