# TEST REPORT — GPT → Web AI Migration Kit

Date: 2026-08-16
State: `LOCAL_BOUNDARY_CHECKS_PASS / LIVE_DOGFOOD_PENDING`

## Rule

No unexecuted test is marked PASS.

## Local execution evidence

A local copy matching the published prototype code was compiled and tested before branch publication.

Result:

```text
5 passed
```

Verified tests:

- [x] config loads the fixture app by slug
- [x] missing/unknown slug fails explicitly
- [x] provider Instructions file is required and loaded server-side
- [x] public config does not expose fixture Instructions/code word
- [x] missing API key fails closed with bounded 503
- [x] input length boundary enforced
- [x] conversation history boundary enforced
- [x] duplicate app slug rejected at registry load

The first attempted local test run failed because the OpenAI SDK was not installed in the isolated execution environment. The prototype was then changed so the SDK is imported only inside the live model-call path. This lets configuration/security-boundary tests run without provider/network dependencies. The environment could not install the SDK because outbound package-network access was unavailable, so no live API assertion is claimed.

## Functional suite still pending

- [ ] browser/static bundle inspection confirms no API key path
- [ ] `/api/chat` empty input behavior recorded
- [ ] OpenAI response is returned through backend
- [ ] upstream API failure becomes user-visible bounded error
- [ ] Knowledge-disabled app does not request retrieval in a live provider call
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

State: `LOCAL_BOUNDARIES_PASS / LIVE_MODEL_NOT_RUN`

### Dogfood 1 — Limit Development Guide

State: `NOT_RUN`

### Dogfood 2 — internal real use case

State: `NOT_RUN`

## Promotion rule

Standalone product promotion is blocked until G6 and G7 are both PASS.
