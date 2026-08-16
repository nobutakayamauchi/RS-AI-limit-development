# GPT → Web AI Migration Kit — Initial Specification

Status: `SPEC_REVISED / COST_CORE_FROZEN_FOR_DOGFOOD`
Date: 2026-08-16
Working name: **WebAI Bridge / GPT Migration Kit**
Tracking: Issue #10
Core companion: `COST_ROUTER.md`

## Protected outcome

A non-technical user can tap one URL on a smartphone, type a request, and use a provider-configured AI without installing a Skill, copying prompts, placing Knowledge files, or accidentally exposing the service operator to unbounded inference cost.

## Business-core outcome

The system must answer **who pays for inference before inference occurs**.

```text
NO PAYER RESOLUTION
→ NO BUDGET AUTHORIZATION
→ NO MODEL EXECUTION
```

The product is therefore two coupled surfaces:

1. **AI Package Runtime** — Instructions + Knowledge + chat URL.
2. **Token Wallet / Cost Router** — payer, budget, model-tier and usage authority.

Neither is considered complete without the other.

## First commercial offer

> Give us the GPT Instructions + Knowledge files. We return a smartphone-usable dedicated Web AI URL. You can use your own provider key, or use an explicitly bounded platform-funded allowance where offered.

The first commercial version is service-assisted. Full self-service billing is intentionally deferred.

## v0 required capabilities

### AI Package Runtime

- app name and slug
- provider-controlled Instructions
- optional Knowledge binding
- mobile-first chat UI
- dedicated URL
- bounded multi-turn context
- explicit error state
- request/rate boundary
- runtime/deployment identity endpoint

### Token Wallet / Cost Router

- payer resolution before provider call
- `BYOK` payer mode
- `PLATFORM_CREDIT` bounded payer mode
- credential resolution separate from public app config
- budget authorization before provider call
- hard budget/cap stop
- server-controlled allowed model tiers
- simple cost-aware model routing policy
- versioned pricing registry
- usage/meter event after execution
- explicit `COST_UNKNOWN`/failure behavior rather than assuming zero

## v0 non-goals

Do not block first Dogfood/assisted sale on:

- automated Stripe billing
- purchased prepaid wallet
- monthly subscription plans
- creator revenue sharing
- creator/sponsor multi-party settlement
- persistent BYOK key storage
- customer dashboard
- Google login
- multi-admin
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
        │    ├─ Knowledge/vector-store reference
        │    ├─ public UI config
        │    ├─ allowed payer modes
        │    └─ routing/budget policy
        ├─ Session Context Boundary
        ├─ Rate / Abuse Gate
        ├─ Payer Resolution
        ├─ Credential Resolution
        ├─ Budget Authorization
        ├─ Cost-aware Model Router
        ├─ Max-cost Guard
        ├─ Deployment Identity
        └─ Provider / OpenAI Responses API
                  └─ file_search / vector store when configured
                          ↓
                    Usage Observation
                          ↓
                    Cost Calculation
                          ↓
                    Meter / Ledger Event
```

Prototype preference:

- Python
- FastAPI or equivalent small HTTP layer
- HTML/CSS/vanilla JS
- JSON app config
- environment/server-secret state
- fixed-point integer currency units for internal ledger values
- minimal persistence only where required

## Payer modes

### BYOK

The end user supplies a provider credential and the provider charges that user/account.

V0 boundary:

- no key in Git or public static assets;
- no ordinary logging of the key;
- session-scoped/non-persistent use preferred;
- persistent storage requires later authentication + encrypted secret design;
- provider inference cost does not debit platform credit.

### PLATFORM_CREDIT

The operator/creator intentionally funds a bounded amount of inference.

V0 boundary:

- explicit hard cap or request allowance;
- no unauthenticated unlimited platform-paid mode;
- stop before provider execution when authorization fails;
- operator-granted Dogfood/promotional allowance is allowed;
- public sale of stored prepaid value is deferred until payment/legal design is separately reviewed.

Future schema may add `USER_WALLET`, `CREATOR_PAYS`, `SPONSORED`, and `HYBRID` without rewriting the inference path.

## Pricing and model routing

Pricing is mutable external state. Model IDs must not imply eternal prices.

Hard rules:

```text
MODEL NAME != PRICE
MISSING PRICE != FREE
CURRENT PRICE != HISTORICAL PRICE
```

The pricing registry records provider, model ID, effective date, input/cached/output prices, special rules, evidence source and review timestamp.

A cost-aware router may begin cheap and escalate only when justified:

```text
Luna
 ↓ complexity / confidence gate
Terra
 ↓ material difficulty / consequence gate
Sol
 ↓ only where justified
additional DA / WITNESS-like / METEOR validation
```

The exact routing policy is replaceable. The protected outcome is acceptable task quality inside an explicitly authorized cost/risk envelope.

## Trust boundaries

1. Operator/provider API secrets MUST NOT appear in browser code.
2. BYOK credentials MUST NOT be committed or normally logged.
3. End-user input MUST NOT overwrite provider Instructions/config/billing policy.
4. Public UI config and private runtime config MUST be separable.
5. Customer-private Knowledge MUST NOT enter public GitHub.
6. Raw provider Instructions are server-side material.
7. Every provider call MUST resolve a payer first.
8. Every platform-funded call MUST pass a budget authorization gate first.
9. A user MUST NOT directly escalate to a disallowed expensive model.
10. Missing usage/price proof MUST NOT become zero cost.
11. Usage must be bounded to avoid accidental cost explosion.
12. Deployment Identity MUST be established before runtime claims.
13. `Code existence != runtime evidence`.
14. Failed/missing Knowledge retrieval must not be presented as verified knowledge.
15. Conversation retention must be explicit; do not silently promise privacy properties not implemented.

## App config contract

```json
{
  "id": "limit-development-guide",
  "slug": "limit-development-guide",
  "display_name": "限界開発 Guide",
  "status": "dogfood",
  "instructions_file": "apps/limit-development-guide/instructions.md",
  "knowledge": {
    "enabled": false,
    "vector_store_env": "LIMIT_DEV_VECTOR_STORE_ID"
  },
  "billing": {
    "allowed_payer_modes": ["BYOK", "PLATFORM_CREDIT"],
    "default_payer_mode": "BYOK",
    "platform_credit": {
      "enabled": true,
      "budget_id_env": "LIMIT_DEV_BUDGET_ID",
      "hard_limit_usd_micros": 500000
    }
  },
  "routing": {
    "policy": "cost_aware_v0",
    "default_tier": "LUNA",
    "allowed_tiers": ["LUNA", "TERRA", "SOL"],
    "max_tier": "SOL"
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

Secret values are referenced outside public config rather than committed directly.

## Existing ecosystem integration

### Ultimate Loop

Development protocol only. Use discovery, Raison d'être Destroy, METEOR, Deployment Identity, post-deploy reality gate, and later DARWIN. The Cost Router is tested/evolved by Ultimate Loop; it is not embedded into Ultimate Loop itself.

Model-routing policies are challengers subject to replacement when a cheaper/stronger provider or model proves better quality-per-cost.

### RS-AI-limit-development

This Episode is the Dogfood/evidence home. It records SPEC, Cost Router design, STATUS, tests, failures and handoff. It is not the permanent production repository.

### Standalone product repository

Promotion target after Dogfood validation. Rule:

`DOGFOOD_VALIDATED + FACTORY_PROOF + COST_GATE_VALIDATED -> promote/extract runtime to standalone product repo`

### limit-development

Public front door only. Add a project/demo link only after deployment and cost-gate validation.

### RTS / X Article Engine / post_adapter

Use build/dogfood/cost evidence as source material for launch content. Publication remains `/human` and user-controlled. No X autoposting.

### BridgePatch

Use as immediate assisted-commercial wrapper when migration includes bespoke setup or integration. Requests that expand into custom workflow/business-system automation are routed to BridgePatch instead of bloating WebAI Bridge core.

### AXIS

Optional upstream prioritization when a buyer has many GPTs/AI assets and must choose migration order. It may later also help prioritize which workloads justify expensive model tiers, but it is not required for one straightforward migration.

### Obsidian / FREEZER

Freeze customer-independent migration recipes, architecture decisions, failure classes, pricing evidence snapshots, routing experiments, cost lessons and reusable knowledge. Never place API keys or customer-private payloads in shared/public knowledge.

### Figma

Design reference only. Must not block v0 functional/cost-safe URL.

### GitHub Pages

Marketing/docs/demo shell only. No browser-side operator API-secret runtime.

### Existing Oracle/Ubuntu

Candidate runtime only. Before claiming deployment capture service/unit, working directory, entrypoint, route surface and deployed revision.

## Dogfood sequence

### Dogfood 0 — deterministic fixture + cost gate

No Knowledge. Fixed Instructions.

Must prove:

- Instructions govern behavior;
- no operator secret leakage;
- payer mode is resolved before provider call;
- a missing payer/credential/budget fails closed;
- platform-funded path cannot exceed hard cap;
- BYOK does not consume platform-funded budget;
- explicit unknown/error behavior;
- iPhone usability later at G3.

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
- budget exhaustion
- model escalation request by user
- routing reason trace
- reload/reconnect
- iPhone Safari portrait

### Dogfood 2 — real internal assistant

Wrap a genuine internal use case (candidate: X Article Engine guidance surface) and observe actual quality/cost by model tier. This is the first useful evidence for later pricing and automatic routing.

## METEOR attack set

1. reveal provider Instructions
2. override provider Instructions
3. hallucinate unsupported Knowledge
4. oversized input
5. rapid cost attack
6. bypass payer resolution
7. spend after platform budget exhaustion
8. force Sol/expensive tier through user input
9. race/concurrent requests against the same remaining budget
10. forge usage/credit state
11. BYOK credential leakage into logs/client config
12. Unicode/emoji/Japanese edge cases
13. cross-session contamination
14. direct endpoint probing
15. invalid/missing slug
16. stale deployment vs repository confusion
17. broken Knowledge indexing
18. operator secret visible in browser/network configuration
19. shared URL forwarded outside intended audience
20. config/pricing revision changed without runtime trace
21. missing pricing data being interpreted as zero/free

Every real failure becomes regression evidence.

## Acceptance gates

- **G0 Scope + Cost Core Frozen** — runtime and payer/cost boundary frozen.
- **G1 Local Functional** — one config produces a server-side model request/response path.
- **G2 Cost Authorization Functional** — every provider call resolves payer + budget; BYOK and bounded platform-credit behavior proven.
- **G3 Knowledge Functional** — configured Knowledge can be retrieved and failure is bounded.
- **G4 Mobile Functional** — iPhone Safari completes the flow.
- **G5 Deployment Identity** — runtime identity evidence captured.
- **G6 METEOR** — no unresolved release-blocking attack/cost finding.
- **G7 Dogfood Validated** — Limit Development Guide used in reality; failures and actual cost observed.
- **G8 Factory Proof** — second AI created by config/Knowledge/billing policy only, without core rewrite.
- **G9 Public Launch** — non-technical person receives URL and uses AI without exposing an unlimited operator-paid path.

## Build roadmap

### A. Skeleton
- config loader
- `/health`
- `/runtime`
- `/api/chat`
- static mobile chat UI
- secret loading
- structured error handling

### B. Cost Core — BEFORE public provider execution
- payer-mode schema
- payer resolution
- BYOK session credential path
- platform-credit budget object
- pre-execution authorization
- model-tier allowlist/router
- versioned price registry
- usage/meter event
- hard stop

### C. Knowledge
- Knowledge/vector-store binding
- per-app retrieval tool configuration
- retrieval failure behavior

### D. Context + abuse boundaries
- max input chars
- bounded history
- rate limit
- concurrency/overspend protection

### E. Dogfood deploy
- separate service
- dedicated route
- deployment identity evidence
- iPhone acceptance

### F. METEOR
- execute attack set including economic attacks
- fix release blockers
- preserve regression cases

### G. Factory proof
- create second app from config + Instructions + Knowledge + billing policy only

### H. Commercial handoff
- intake checklist
- Instructions backup/import checklist
- Knowledge intake policy
- payer-mode choice
- BYOK handoff path or explicit funded allowance
- URL handoff checklist
- observed quality/cost/support burden

### I. Launch
- public project link after validation
- X Article Engine/post_adapter launch content
- human publication
- first assisted migration sale

## Post-v0 roadmap

- **v1** purchased prepaid wallet, user-visible meter, package-level limits, stronger automatic routing, transactional/idempotent ledger
- **v2** monthly plans, `CREATOR_PAYS`, `USER_WALLET`, `SPONSORED`, `HYBRID`, creator revenue share
- later: provider competition/routing and export path so WebAI Bridge itself remains replaceable

## Success definition

The first success is not “SaaS complete”. It is:

> A second AI can be produced from Instructions + Knowledge + billing/routing policy without rewriting core code; every inference has an authorized payer; and a non-technical person can use it from a smartphone URL without creating an unbounded platform-cost liability.

## Hard rule

Do not let the urgent market opportunity recreate either the old monolith **or an unlimited inference subsidy**. The product implementation remains replaceable and separate from Ultimate Loop, Limit Development, RTS-derived capabilities, BridgePatch/AXIS, FREEZER and design sources.
