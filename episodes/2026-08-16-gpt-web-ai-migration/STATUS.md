# STATUS — GPT → Web AI Migration Kit

Date: 2026-08-16
State: `PROTOTYPE_BUILT / COST_CORE_ADDED / LOCAL_REGRESSION_PASS / NOT_DEPLOYED`
Tracking: Issue #10
Branch: `agent/gpt-web-ai-dogfood`

## Current gates

| Gate | State | Evidence |
|---|---|---|
| G0 Scope + Cost Core Frozen | PASS | `SPEC.md`, `COST_ROUTER.md` |
| G1 Local Functional | PARTIAL | prototype compiles; fake-provider path exercised |
| G2 Cost Authorization Functional | PARTIAL | BYOK/platform-budget regressions pass; live provider not run |
| G3 Knowledge Functional | NOT_RUN | live vector-store retrieval not dogfooded |
| G4 Mobile Functional | NOT_RUN | iPhone Safari test pending |
| G5 Deployment Identity | NOT_RUN | no deployed runtime identity claimed |
| G6 METEOR | NOT_RUN | economic + security attack suite pending |
| G7 Dogfood Validated | NOT_RUN | live fixture/Limit Development dogfood pending |
| G8 Factory Proof | NOT_RUN | second app not created |
| G9 Public Launch | NOT_RUN | no public product claim |

## Classification

- Specification: `AS_BUILT`
- Cost Router specification: `AS_BUILT`
- Prototype source: `AS_BUILT`
- Local regression paths: `AS_BUILT`
- Live OpenAI path: `UNOBSERVED`
- Live Knowledge path: `UNOBSERVED`
- Deployed runtime: `UNOBSERVED`
- Production availability: `FALSE`
- Commercial availability: `FALSE`

## Implemented prototype surface

### Runtime
- app registry/config loader
- server-side Instructions loading
- `/health`
- `/runtime`
- public UI config boundary
- `/api/chat`
- Responses API call path
- optional `file_search` vector-store path
- input/history limits
- mobile-first chat UI

### Cost Core
- payer modes: `BYOK`, `PLATFORM_CREDIT`
- BYOK request/session credential path; no intentional persistence
- platform credential kept server-side
- versioned pricing registry
- server-controlled model allowlist/default
- pre-execution conservative cost reservation
- persistent SQLite budget/spend/reservation ledger
- atomic reservation transaction to reduce concurrent double-spend risk
- provider failure releases reservation
- missing model price fails closed
- platform-funded Knowledge fails closed without explicit tool/retrieval reserve policy
- successful platform usage creates a metered debit record
- UI exposes payer choice without exposing operator secret

## Local verified evidence

A matching local copy compiled and ran:

```text
10 passed
```

Verified classes:

- public config excludes fixture Instructions/operator secret paths;
- BYOK cannot run without the user credential;
- BYOK uses the user credential and does not consume platform credit;
- platform-funded inference requires a budget identity;
- platform-funded usage settles into the ledger;
- exhausted platform budget blocks before provider execution;
- provider failure releases reservation with zero successful spend;
- unknown model price blocks platform-funded execution;
- platform-funded Knowledge is blocked when cost policy is unknown;
- input/history boundaries still execute before inference.

Provider success/failure behavior was simulated with a fake OpenAI client. This validates our authorization/request/ledger logic, not live external compatibility.

## Pricing evidence note

The v0 registry is tied to the OpenAI price-change snapshot effective 2026-07-30. Pricing is explicitly external mutable evidence; it is not inferred permanently from model names.

Tool/search/storage costs are not silently treated as zero. Until exact platform-funded Knowledge pricing/reserve policy is established, that path fails closed.

## Next execution order

1. Run Dogfood 0 on an environment with current OpenAI SDK.
2. Test BYOK against the live provider.
3. Test a tiny bounded PLATFORM_CREDIT budget against the live provider.
4. Verify provider usage fields against ledger calculations.
5. Intentionally exhaust the budget and prove the next call never reaches provider execution.
6. Add live Limit Development Knowledge and explicit retrieval-cost policy.
7. Deploy on candidate Oracle/Ubuntu service.
8. Capture Deployment Identity + persistent ledger identity.
9. Run iPhone Safari acceptance.
10. Run METEOR including budget-race/model-escalation/credential-leak attacks.
11. Create second app from config + Instructions + Knowledge + billing/routing policy only.
12. Promote survivor to standalone product repo.
13. Connect public front door and launch content pipeline.

## Hard blocker for public launch

No public launch while an unauthenticated or unbounded platform-funded provider route exists.
