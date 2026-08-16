# WebAI Bridge bounded prototype

State: `DOGFOOD / NOT_PRODUCTION`

This prototype proves the smallest useful boundary: provider-controlled Instructions exposed through a smartphone-friendly Web AI URL while the OpenAI API credential remains server-side. Optional Knowledge is attached by a server-side vector-store reference.

## Run

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
export OPENAI_API_KEY='...'
export WEB_AI_MODEL='...'
uvicorn app:app --host 0.0.0.0 --port 8080
```

Open:

```text
/a/migration-fixture-ai
```

Do not commit API keys, private vector-store IDs, or customer-private Knowledge.

## Endpoints

- `GET /health` — process/config health only; not a production-validity claim.
- `GET /runtime` — deployment identity fields. `UNSET` means identity is not established.
- `GET /apps/{slug}/public-config` — deliberately restricted public UI config.
- `GET /a/{slug}` — mobile chat surface.
- `POST /api/chat` — bounded server-side AI request.

## Runtime identity environment

```text
WEB_AI_SERVICE_UNIT
WEB_AI_WORKING_DIRECTORY
WEB_AI_ROUTE_SURFACE
DEPLOYED_REVISION
```

The fixed entrypoint is reported as `app:app`.

## Knowledge

Set `knowledge.enabled=true` in an app config and point `vector_store_env` at an environment variable containing the server-side vector-store ID. The backend then provides the Responses API `file_search` tool for that app.

## Privacy/storage default

The prototype sends `store=false` on Responses API calls. This is a deliberate conservative default, not a complete customer-data policy. Application/server logs and provider-side behavior still require explicit review before commercial use.

## Current limits

- in-memory rate limiter is single-process only
- no authentication/access-link layer
- no billing
- no persistent conversation storage
- no streaming
- no production deployment evidence
- no live API test in the repository record yet
- no Knowledge/vector-store dogfood yet
- no iPhone acceptance result yet

These are explicit v0 boundaries, not hidden completion claims.

## Local boundary checks performed before publication

A local copy of this prototype passed five non-network boundary tests:

1. health/public config works and does not expose fixture Instructions/code word;
2. unknown slug is explicit 404;
3. missing API key stops with bounded 503;
4. input and history limits are enforced;
5. duplicate slug is rejected during registry load.

The OpenAI SDK was intentionally imported only inside the live chat path so configuration/boundary tests do not require network/provider dependencies.
