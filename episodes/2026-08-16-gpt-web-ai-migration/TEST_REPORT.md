# TEST REPORT — GPT → Web AI Migration Kit

Date: 2026-08-16
State: `LOCAL_COST_CORE_REGRESSION_PASS / LIVE_DOGFOOD_PENDING`

## Rule

No unexecuted test is marked PASS. Fake-provider tests verify our code path, not live provider behavior.

## Local execution evidence

A local copy matching the cost-core implementation compiled and ran:

```text
10 passed
```

Verified:

- [x] public config loads payer modes but not fixture Instructions/operator secret paths
- [x] unknown app slug fails explicitly
- [x] BYOK requires user-supplied provider key
- [x] BYOK uses that key and does not debit platform credit
- [x] platform-funded inference requires a budget identity
- [x] platform-funded successful usage is metered/debited
- [x] exhausted platform budget blocks before provider execution
- [x] provider failure releases reservation without successful spend
- [x] unknown model price blocks platform-funded execution
- [x] platform-funded Knowledge blocks without explicit cost reserve policy
- [x] input/history boundaries still apply before inference

The cost ledger uses a SQLite `BEGIN IMMEDIATE` reservation transaction so simultaneous requests do not simply read the same remaining budget and both proceed without reservation.

## Still pending — live provider

- [ ] live BYOK response
- [ ] live PLATFORM_CREDIT response
- [ ] provider usage fields match expected ledger calculation
- [ ] intentionally exhausted live budget prevents the next provider call
- [ ] provider-side rate/quota error releases reservation correctly
- [ ] live model behavior respects fixture Instructions

## Still pending — Knowledge

- [ ] live file/vector retrieval
- [ ] exact tool/storage cost evidence captured
- [ ] platform-funded Knowledge reserve policy frozen
- [ ] unsupported Knowledge question does not become fabricated certainty

## Still pending — Mobile

- [ ] iPhone Safari portrait layout
- [ ] BYOK password field usable with keyboard
- [ ] BYOK key is not written to localStorage/sessionStorage
- [ ] long answer remains scrollable
- [ ] slow network has visible pending state
- [ ] reload has explicit loss/reset behavior for non-persisted BYOK key

## METEOR — economic/security suite

- [ ] reveal provider Instructions
- [ ] override provider Instructions
- [ ] bypass payer resolution
- [ ] execute platform-funded request after budget exhaustion
- [ ] concurrent race against same remaining budget
- [ ] force expensive model tier from user prompt/request
- [ ] unknown pricing interpreted as free
- [ ] forge usage/debit fields
- [ ] provider error incorrectly charged as success
- [ ] BYOK credential leaked into HTML/config/logging
- [ ] oversized input / rapid cost attack
- [ ] cross-session contamination
- [ ] invalid slug / endpoint probing
- [ ] stale deployment vs repository mismatch
- [ ] config/pricing revision mismatch
- [ ] forwarded URL reaches unintended platform-funded budget

## Deployment Identity evidence required

```text
service/unit:
working_directory:
entrypoint/module:
active_route_surface:
deployed_revision:
pricing_version:
ledger_path / ledger identity:
observed_at:
observer:
```

## Dogfood evidence

### Dogfood 0 — deterministic fixture + payer gate

State: `LOCAL_REGRESSION_PASS / LIVE_MODEL_NOT_RUN`

### Dogfood 1 — Limit Development Guide

State: `NOT_RUN`

### Dogfood 2 — internal real use case / quality-per-dollar

State: `NOT_RUN`

## Promotion rule

Standalone product promotion is blocked until Dogfood, factory proof, and cost authorization gates all pass.
