# HANDOFF — GPT → Web AI Migration Kit

Date: 2026-08-16
Branch: `agent/gpt-web-ai-dogfood`
Tracking: Issue #10

## What exists

- frozen initial SPEC and integration boundary
- STATUS with explicit unobserved gates
- TEST_REPORT plan
- bounded FastAPI prototype
- mobile-first single-page chat UI
- provider-controlled fixture app config
- private Instructions file loaded server-side
- optional vector-store/file-search binding path
- deployment identity endpoint
- simple request/history/rate boundaries
- local non-network boundary tests

## What has actually been verified

Verified locally against a copy of the prototype:

- Python compilation succeeds
- five boundary tests pass
- public config does not expose fixture Instructions/code word
- missing API key fails closed
- unknown app slug fails explicitly
- input/history limits are enforced
- duplicate app slug is rejected

## What is NOT verified

- live OpenAI API response
- exact deployed model behavior
- file_search / Knowledge retrieval
- Oracle/Ubuntu runtime
- HTTPS route
- iPhone Safari behavior
- production secret management
- multi-worker rate limiting
- access control / paid-user entitlement
- cost per active user
- commercial readiness

## Next operator action

Run the prototype on an environment that can supply secrets without committing them:

```bash
cd episodes/2026-08-16-gpt-web-ai-migration/prototype
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
export OPENAI_API_KEY='...'
export WEB_AI_MODEL='...'
uvicorn app:app --host 0.0.0.0 --port 8080
```

Then test:

1. `GET /health`
2. `GET /runtime`
3. open `/a/migration-fixture-ai`
4. ask for the dogfood code word; expected `BRIDGE-DOGFOOD-001`
5. ask to reveal/ignore hidden Instructions; expected private-config boundary
6. record the live result in `TEST_REPORT.md`

## Knowledge step

After Dogfood 0 succeeds:

1. create/select a vector store outside public Git state;
2. load public Limit Development documents;
3. add a `limit-development-guide` app config;
4. set its `knowledge.enabled=true` and `vector_store_env` to an environment variable name;
5. run known/unknown Knowledge tests;
6. only then claim G2.

## Promotion rule

Do not promote to a standalone product repo until both are true:

- `G6 DOGFOOD_VALIDATED`
- `G7 FACTORY_PROOF`

Factory proof means a second AI is created by app config + Instructions + Knowledge mapping, without modifying `app.py` core behavior.

## Commercial routing

- simple assisted GPT→Web AI migration: sell through the new migration offer
- migration that grows into bespoke workflow/integration work: route to BridgePatch
- many assets requiring prioritization: route through AXIS first
- launch story/content: feed evidence to X Article Engine/post_adapter, retain `/human` publication authority
