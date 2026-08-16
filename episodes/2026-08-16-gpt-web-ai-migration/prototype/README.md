# WebAI Bridge bounded prototype

State: `DOGFOOD / COST_CORE_ADDED / NOT_PRODUCTION`

This prototype now proves two coupled boundaries:

1. provider-controlled Instructions exposed through a smartphone-friendly Web AI URL;
2. payer/budget authorization before inference so the operator does not expose an unlimited platform-paid endpoint.

Optional Knowledge is attached by a server-side vector-store reference.

## Core invariant

```text
NO PAYER RESOLUTION
→ NO BUDGET AUTHORIZATION
→ NO MODEL EXECUTION
```

See `../COST_ROUTER.md`.

## Run

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
export WEB_AI_LEDGER_PATH='/persistent/runtime/webai-ledger.sqlite3'
uvicorn app:app --host 0.0.0.0 --port 8080
```

Open:

```text
/a/migration-fixture-ai
```

## Payer modes

### BYOK

The user enters their own provider API key in the page. The current UI keeps it in page memory and sends it to the backend in `X-Provider-API-Key`; it is not written to localStorage by the prototype and is not intentionally persisted by the backend.

Provider inference cost belongs to that API account. Do not log the header.

### PLATFORM_CREDIT

The operator supplies:

```text
OPENAI_API_KEY
MIGRATION_FIXTURE_BUDGET_ID
WEB_AI_LEDGER_PATH
```

The fixture has an explicit hard budget in app config. Before execution the backend computes a conservative reservation, atomically reserves that amount in SQLite, and refuses execution when the remaining budget cannot cover the reservation.

Provider failure releases the reservation without recording successful spend.

## Pricing registry

`pricing.json` is a versioned evidence snapshot, not an eternal constant.

The checked registry version is:

```text
openai-2026-07-30
```

If a model has no known price, platform-funded execution fails closed rather than treating cost as zero.

Tool/storage costs are separate mutable pricing. Platform-funded Knowledge requests are blocked unless an explicit Knowledge cost reserve policy is configured.

## Endpoints

- `GET /health` — process/config health and pricing-version visibility only.
- `GET /runtime` — deployment identity + pricing/ledger identity fields.
- `GET /apps/{slug}/public-config` — restricted UI config and allowed payer modes.
- `GET /a/{slug}` — mobile chat surface.
- `POST /api/chat` — payer-authorized server-side AI request.

## Runtime identity environment

```text
WEB_AI_SERVICE_UNIT
WEB_AI_WORKING_DIRECTORY
WEB_AI_ROUTE_SURFACE
DEPLOYED_REVISION
WEB_AI_LEDGER_PATH
```

The fixed entrypoint is reported as `app:app`.

## Knowledge

Set `knowledge.enabled=true` in an app config and point `vector_store_env` at an environment variable containing the server-side vector-store ID.

BYOK may use that provider path directly. PLATFORM_CREDIT additionally requires an explicit reserve for retrieval/tool costs before Knowledge execution is allowed.

## Privacy/storage default

The prototype sends `store=false` on Responses API calls. This is a conservative default, not a complete customer-data policy. Application/server logs, reverse proxies, provider-side behavior, and future persistent BYOK storage require separate review before commercial use.

## Current limits

- rate limiter is single-process only
- no authentication/access-link layer
- BYOK key is not persistently stored
- PLATFORM_CREDIT ledger is small v0 SQLite, not a full accounting system
- no purchased prepaid wallet yet
- no Stripe/monthly billing yet
- no creator/sponsor revenue split
- no persistent conversation storage
- no streaming
- no production deployment evidence
- no live OpenAI API test in the repository record yet
- no Knowledge/vector-store dogfood yet
- no iPhone acceptance result yet

These are explicit boundaries, not hidden completion claims.

## Local regression checks

A local copy matching the cost-core implementation compiled and passed:

```text
10 passed
```

Verified classes include:

- public config does not expose fixture Instructions/operator secrets;
- BYOK refuses execution without a user key;
- BYOK uses the user credential and does not debit platform credit;
- platform-funded inference requires a budget identity;
- platform-funded successful usage is metered/debited;
- exhausted budget blocks before provider execution;
- provider failure releases reservation without spend;
- unknown model price blocks platform-funded execution;
- Knowledge + platform funding blocks when no tool-cost reserve policy exists;
- existing input/history limits still apply before inference.

Provider calls were faked for these regression tests. Live-provider compatibility remains unobserved until Dogfood deployment.
