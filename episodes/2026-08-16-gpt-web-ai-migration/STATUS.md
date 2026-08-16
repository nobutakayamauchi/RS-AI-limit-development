# STATUS — GPT → Web AI Migration Kit

Date: 2026-08-16
State: `PROTOTYPE_BUILT / LOCAL_BOUNDARIES_PASS / NOT_DEPLOYED`
Tracking: Issue #10
Branch: `agent/gpt-web-ai-dogfood`

## Current gates

| Gate | State | Evidence |
|---|---|---|
| G0 Scope Frozen | PASS | `SPEC.md` |
| G1 Local Functional | PARTIAL | prototype compiles + 5 boundary tests pass; live model call not run |
| G2 Knowledge Functional | NOT_RUN | vector-store binding not dogfooded |
| G3 Mobile Functional | NOT_RUN | iPhone Safari test pending |
| G4 Deployment Identity | NOT_RUN | no deployed runtime identity claimed |
| G5 METEOR | NOT_RUN | attack suite pending |
| G6 Dogfood Validated | NOT_RUN | live fixture/Limit Development dogfood pending |
| G7 Factory Proof | NOT_RUN | second app not created |
| G8 Public Launch | NOT_RUN | no public product claim |

## Classification

- Specification: `AS_BUILT`
- Prototype source: `AS_BUILT`
- Locally exercised boundary paths: `AS_BUILT`
- Live OpenAI path: `UNOBSERVED`
- Knowledge path: `UNOBSERVED`
- Deployed runtime: `UNOBSERVED`
- Production availability: `FALSE`
- Commercial availability: `FALSE`

## Implemented prototype surface

- app registry/config loader
- server-side Instructions loading
- `/health`
- `/runtime`
- public UI config boundary
- `/api/chat`
- OpenAI Responses API call path
- optional `file_search` vector-store binding path
- input/history limits
- basic single-process rate limiter
- mobile-first HTML/JS chat UI
- deterministic fixture app

## Local verified evidence

- Python compilation succeeds.
- Five automated tests pass.
- Unknown slug fails explicitly.
- Public config does not expose fixture Instructions/code word.
- Missing API key fails closed with a bounded error.
- Input/history limits are enforced.
- Duplicate slug is rejected.

No live provider call was executed in the test environment because the OpenAI SDK was unavailable there and outbound package installation was blocked. The SDK import was moved inside the live call path so provider-independent boundaries remain testable.

## Next execution order

1. Run prototype on an environment with the OpenAI SDK + server-side `OPENAI_API_KEY` + `WEB_AI_MODEL`.
2. Execute live deterministic fixture.
3. Record provider behavior and upstream failure behavior.
4. Add Limit Development Knowledge/vector-store binding.
5. Deploy on candidate Oracle/Ubuntu service.
6. Capture Deployment Identity.
7. Run iPhone Safari acceptance.
8. Run METEOR attack set.
9. Fix release blockers only.
10. Create second app from config/Knowledge only.
11. Promote survivor to standalone product repo.
12. Connect public front door and launch content pipeline.

## Known blockers

- Live API execution requires a runtime with dependencies and `OPENAI_API_KEY` supplied outside Git.
- Knowledge dogfood requires a vector store or equivalent retrieval binding.
- External mobile acceptance requires a deployed HTTPS route.

No blocker above justifies widening v0 scope.
