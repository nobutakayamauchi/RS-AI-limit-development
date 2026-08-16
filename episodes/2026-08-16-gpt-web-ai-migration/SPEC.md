# GPT → Web AI Migration Kit — Initial Specification

Status: `SPEC_FROZEN_FOR_DOGFOOD`
Date: 2026-08-16
Working name: **WebAI Bridge / GPT Migration Kit**
Tracking: Issue #10

## Protected outcome

A non-technical user can tap one URL on a smartphone, type a request, and use a provider-configured AI without installing a Skill, copying prompts, placing files, or exposing an API key.

## First commercial offer

> Give us the GPT Instructions + Knowledge files. We return a smartphone-usable dedicated Web AI URL.

The first commercial version is service-assisted. Self-service is intentionally deferred.

## v0 required capabilities

- app name and slug
- provider-controlled Instructions
- optional Knowledge binding
- server-selected model
- mobile-first chat UI
- server-side OpenAI API call
- API key held server-side only
- dedicated URL
- bounded multi-turn context
- explicit error state
- basic request/rate/cost boundary
- runtime/deployment identity endpoint
- usage observations sufficient for later pricing

## v0 non-goals

Do not block launch on:

- automated Stripe billing
- customer dashboard
- Google login
- multi-admin
- BYOK
- automatic GPT scraping/import
- autonomous tools/actions
- social posting automation
- large frontend framework

## Architecture

```text
End User / iPhone Safari / Chrome
        ↓ HTTPS
Mobile Web Chat UI
        ↓
WebAI Bridge backend
        ├─ App Config Registry
        │    ├─ Instructions
        │    ├─ model
        │    ├─ Knowledge/vector-store reference
        │    ├─ public UI config
        │    └─ usage policy
        ├─ Session Context Boundary
        ├─ Rate / Usage Gate
        ├─ Deployment Identity
        └─ OpenAI Responses API
                  └─ file_search / vector store when configured
```

Prototype preference:

- Python
- FastAPI or equivalent small HTTP layer
- HTML/CSS/vanilla JS
- environment/server-secret API key
- JSON app config
- minimal persistence only where required

## Trust boundaries

1. API key MUST NOT appear in browser code.
2. End-user input MUST NOT overwrite provider Instructions/config.
3. Public UI config and private runtime config MUST be separable.
4. Customer-private Knowledge MUST NOT enter public GitHub.
5. Raw provider Instructions are server-side material.
6. Usage must be bounded to avoid accidental cost explosion.
7. Deployment Identity MUST be established before runtime claims.
8. `Code existence != runtime evidence`.
9. Failed/missing Knowledge retrieval must not be presented as verified knowledge.
10. Conversation retention must be explicit; do not silently promise privacy properties not implemented.

## App config contract

```json
{
  "id": "limit-development-guide",
  "slug": "limit-development-guide",
  "display_name": "限界開発 Guide",
  "status": "dogfood",
  "model_env": "WEB_AI_MODEL",
  "instructions_file": "apps/limit-development-guide/instructions.md",
  "knowledge": {
    "enabled": false,
    "vector_store_env": "LIMIT_DEV_VECTOR_STORE_ID"
  },
  "ui": {
    "welcome": "限界開発について聞いてください"
  },
  "usage": {
    "max_input_chars": 12000,
    "max_history_messages": 12
  }
}
```

Secret values are referenced by environment variable name rather than committed directly.

## Existing ecosystem integration

### Ultimate Loop

Development protocol only. Use discovery, Raison d'être Destroy, METEOR, Deployment Identity, post-deploy reality gate, and later DARWIN. Do not place product runtime inside Ultimate Loop.

### RS-AI-limit-development

This Episode is the dogfood/evidence home. It records SPEC, STATUS, tests, failures and handoff. It is not the permanent production repository.

### Standalone product repository

Promotion target after Dogfood validation. Rule:

`DOGFOOD_VALIDATED -> promote/extract runtime to standalone product repo`

### limit-development

Public front door only. Add a project/demo link only after deployment validation.

### RTS / X Article Engine / post_adapter

Use build/dogfood evidence as source material for launch content. Publication remains `/human` and user-controlled. No X autoposting.

### BridgePatch

Use as immediate assisted-commercial wrapper when migration includes bespoke setup or integration. Requests that expand into custom workflow/business-system automation are routed to BridgePatch instead of bloating WebAI Bridge core.

### AXIS

Optional upstream prioritization when a buyer has many GPTs/AI assets and must choose migration order. Not required for one straightforward migration.

### Obsidian / FREEZER

Freeze customer-independent migration recipes, architecture decisions, failure classes, cost lessons and reusable knowledge. Never place API keys or customer-private payloads in shared/public knowledge.

### Figma

Design reference only. Must not block v0 functional URL.

### GitHub Pages

Marketing/docs/demo shell only. No browser-side secret/API-key runtime.

### Existing Oracle/Ubuntu

Candidate runtime only. Before claiming deployment capture service/unit, working directory, entrypoint, route surface and deployed revision.

## Dogfood sequence

### Dogfood 0 — deterministic fixture

No Knowledge. Fixed Instructions. Proves config, transport, server-side secret boundary and mobile UI.

Pass:
- Instructions govern behavior
- no secret leakage
- explicit unknown/error behavior
- iPhone usable

### Dogfood 1 — Limit Development Guide

Knowledge candidate:
- public Limit Development README
- current-development-architecture
- SAFETY
- selected public documentation

Required tests:
- known Knowledge fact
- absent Knowledge fact
- Japanese multi-turn
- prompt-injection attempt
- long input
- rapid input
- reload/reconnect
- iPhone Safari portrait

### Dogfood 2 — real internal assistant

Wrap a genuine internal use case (candidate: X Article Engine guidance surface) to prove this is not a toy demo.

## METEOR attack set

1. reveal provider Instructions
2. override provider Instructions
3. hallucinate unsupported Knowledge
4. oversized input
5. rapid cost attack
6. Unicode/emoji/Japanese edge cases
7. cross-session contamination
8. direct endpoint probing
9. invalid/missing slug
10. stale deployment vs repository confusion
11. broken Knowledge indexing
12. secret visible in browser/network configuration
13. shared URL forwarded outside intended audience
14. config changed without version trace

Every real failure becomes regression evidence.

## Acceptance gates

- **G0 Scope Frozen** — this v0 boundary is frozen.
- **G1 Local Functional** — one config produces a server-side model response.
- **G2 Knowledge Functional** — configured Knowledge can be retrieved and failure is bounded.
- **G3 Mobile Functional** — iPhone Safari completes the flow.
- **G4 Deployment Identity** — runtime identity evidence captured.
- **G5 METEOR** — no unresolved release-blocking attack finding.
- **G6 Dogfood Validated** — Limit Development Guide used in reality; failures recorded/fixed.
- **G7 Factory Proof** — second AI created by config/Knowledge only, without core rewrite.
- **G8 Public Launch** — non-technical person receives URL and uses AI without setup.

## Build roadmap

### A. Skeleton
- config loader
- `/health`
- `/runtime`
- `/api/chat`
- static mobile chat UI
- secret loading
- structured error handling

### B. Knowledge
- Knowledge/vector-store binding
- per-app retrieval tool configuration
- retrieval failure behavior

### C. Context + cost boundaries
- max input chars
- bounded history
- rate limit
- per-app usage observation

### D. Dogfood deploy
- separate service
- dedicated route
- deployment identity evidence
- iPhone acceptance

### E. METEOR
- execute attack set
- fix release blockers
- preserve regression cases

### F. Factory proof
- create second app from config + Knowledge only

### G. Commercial handoff
- intake checklist
- Instructions backup/import checklist
- Knowledge intake policy
- URL handoff checklist
- observed cost/support burden

### H. Launch
- public project link after validation
- X Article Engine/post_adapter launch content
- human publication
- first assisted migration sale

## Post-v0 roadmap

- **v0.2** signed/magic access links, basic caps, better streaming UX, feedback
- **v0.3** operator admin page, Knowledge replacement/versioning
- **v0.4** customer auth, account quotas, basic usage view
- **v0.5** Stripe/entitlement automation
- **v0.6** provider self-service migration wizard
- **v1** multiple Web AIs per provider, justified provider adapters, export path so WebAI Bridge itself remains replaceable

## Success definition

The first success is not “SaaS complete”. It is:

> A second AI can be produced from Instructions + Knowledge without rewriting core code, and a non-technical person can use it from a smartphone URL.

## Hard rule

Do not let the urgent market opportunity recreate the old monolith. The product implementation remains replaceable and separate from Ultimate Loop, Limit Development, RTS-derived capabilities, BridgePatch/AXIS, FREEZER and design sources.
