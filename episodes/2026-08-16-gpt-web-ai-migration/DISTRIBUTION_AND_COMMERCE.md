# Distribution / Access / Payment Policy — Core Specification

Date: 2026-08-16
Status: `CORE_SCHEMA / V0_UI_SHAPE`
Tracking: Issue #10
Companions: `SPEC.md`, `COST_ROUTER.md`

## Core insight

**Price to access the AI and price to run the model are different things.**

Do not couple them.

A creator may charge for the package while the user brings their own API key. A creator may distribute a package for free while funding the first N requests. A paid package may include platform credits, require BYOK, or allow either.

Therefore every package resolves at least three independent questions:

1. **ACCESS / LICENSE** — may this user use the AI, and what do they pay the creator/platform for access?
2. **INFERENCE PAYER** — whose provider balance pays for model/tool execution?
3. **DELIVERY MODE** — is the AI hosted by WebAI Bridge, portable to the user, or both?

These must remain orthogonal in the data model.

## Creator experience

The creator opens one package editor URL and configures:

```text
PACKAGE
├─ Name / description / icon
├─ Instructions
├─ Knowledge
├─ Model / capability policy
├─ Access & price
├─ Free allowance
├─ Inference payer options
├─ Delivery / portability
└─ Publish URL
```

The creator does not need to understand internal ledger mechanics to publish a simple package.

## 1. Access / license policy

Supported schema should permit:

```text
FREE
FREEMIUM
ONE_TIME_PURCHASE
SUBSCRIPTION
PAY_PER_USE_ACCESS
PRIVATE / INVITE_ONLY
```

### FREE

No package-access fee.

Inference may still be BYOK, user credit, creator-funded, sponsored, or hybrid.

### FREEMIUM

Creator defines a free entitlement boundary, for example:

- first N executions;
- first X platform credits;
- free until a date;
- free access to one model tier, paid access to higher capability;
- creator-funded allowance, then BYOK/user credit.

The free rule MUST be explicit and bounded.

### ONE_TIME_PURCHASE

User buys access/license once. Inference funding remains separately configured.

Example:

```text
Package price: ¥1,500 once
Inference: BYOK or USER_WALLET
```

This is valid. Paying for the package does not imply the creator must pay future API bills.

### SUBSCRIPTION

Recurring access entitlement. Included inference credits, if any, are a separate allowance attached to the subscription.

Never interpret subscription = unlimited inference.

### PAY_PER_USE_ACCESS

A commercial/service fee may be charged per invocation in addition to provider inference cost.

Example:

```text
Creator/service fee: ¥20 per run
Inference: BYOK
```

The user still pays provider tokens through their own key while the creator earns for the package/service.

## 2. Inference payer policy

Independent of access price:

```text
BYOK
USER_WALLET
CREATOR_PAYS
SPONSORED
HYBRID
```

### BYOK

User supplies provider credential. Provider inference is billed to the user directly.

The package may still be free or paid.

### USER_WALLET

User buys WebAI Bridge credits and inference/tool cost is deducted from their platform wallet.

### CREATOR_PAYS

Creator funds a bounded package budget.

Use cases:

- free demo;
- company product-support bot;
- lead magnet;
- customer benefit;
- creator-funded first N runs.

### SPONSORED

A third-party budget funds execution under a campaign/package policy.

### HYBRID

Policy resolves a sequence/fallback, for example:

```text
Creator pays first 20 requests
→ then user wallet
→ if wallet unavailable, offer BYOK
```

or:

```text
Free Luna allowance
→ user credit for Terra/Sol
```

The fallback sequence must be explicit and observable.

## 3. Delivery mode / portability

The creator chooses whether users receive only a hosted URL or may take the package with them.

```text
HOSTED_ONLY
PORTABLE_LICENSE
HOSTED_AND_PORTABLE
```

### HOSTED_ONLY

User accesses through WebAI Bridge URL. Instructions/Knowledge remain server-side to the extent technically possible.

Best for creators who want the simplest UX or do not want to distribute package source material.

### PORTABLE_LICENSE

Creator explicitly allows a user to obtain a portable package and run it with their own provider/runtime.

This is the “capable user can take it and run it themselves” path.

A portable package may include:

```text
manifest
instructions
knowledge references/files allowed by license
model/capability preferences
version metadata
license/terms
```

Do not pretend local portability can cryptographically hide Instructions/Knowledge from the recipient. If content must remain secret, use `HOSTED_ONLY`.

### HOSTED_AND_PORTABLE

The user may use the easy hosted link or take the package and self-run if capable.

This can become a strong distribution promise:

> Beginners can click the URL. Power users are not trapped in the platform.

## Hosted user payment UX

When the user opens a package URL, resolve access first, then show permitted inference-payment choices.

Example:

```text
[ X投稿AI ]

Access: Purchased ✓

How do you want to pay for AI usage?

○ Use WebAI credits
   Balance: ¥840 equivalent
   [ Add credit ]

○ Use my own API key
   [ OpenAI API key __________ ]

○ Use included creator allowance
   8 free runs remaining

[ Start ]
```

If no valid payer path exists, model execution is blocked.

## Creator package editor UX

Minimum conceptual form:

```text
1. BASIC
   Name
   Description
   Public URL slug

2. AI
   Instructions
   Knowledge
   Capability/model ceiling

3. ACCESS PRICE
   ○ Free
   ○ Freemium
   ○ One-time purchase
   ○ Subscription
   ○ Pay-per-use access

4. FREE / INCLUDED ALLOWANCE
   Amount / runs / expiry / model tier

5. WHO PAYS INFERENCE?
   [ ] User WebAI credits
   [ ] BYOK
   [ ] Creator budget
   [ ] Sponsor budget

   Fallback order:
   Creator allowance → User credit → BYOK

6. DELIVERY
   ○ Hosted only
   ○ Portable license
   ○ Both

7. PUBLISH
   Preview
   Cost exposure warning
   Publish URL
```

## Package schema

Illustrative shape:

```json
{
  "package_id": "x-post-ai",
  "access": {
    "mode": "ONE_TIME_PURCHASE",
    "price": {"currency": "JPY", "minor_units": 1500},
    "entitlement": "PERPETUAL"
  },
  "included_allowance": {
    "enabled": true,
    "payer": "CREATOR_PAYS",
    "limit_type": "REQUESTS",
    "limit": 10,
    "max_model_tier": "LUNA"
  },
  "inference": {
    "allowed_payer_modes": ["USER_WALLET", "BYOK"],
    "fallback_order": ["USER_WALLET", "BYOK"]
  },
  "delivery": {
    "mode": "HOSTED_AND_PORTABLE",
    "portable_license_id": "creator-standard-v1"
  }
}
```

This means:

- user pays ¥1,500 for the AI package;
- first 10 Luna-tier requests are creator-funded;
- after that, user may use WebAI credit or BYOK;
- capable users may take an explicitly licensed portable package;
- the creator is not exposed to unlimited inference spend.

## Entitlement and inference are separate gates

Execution becomes:

```text
REQUEST
↓
PACKAGE EXISTS
↓
ACCESS ENTITLEMENT VALID?
↓
PAYER RESOLUTION
↓
BUDGET / CREDENTIAL AUTHORIZATION
↓
MODEL ROUTING
↓
EXECUTE
↓
USAGE / COST LEDGER
↓
CREATOR / PLATFORM COMMERCIAL LEDGER (where applicable)
↓
RESPONSE
```

Hard invariants:

```text
PAID ACCESS != PLATFORM PAYS INFERENCE
FREE ACCESS != FREE INFERENCE
BYOK != FREE PACKAGE
SUBSCRIPTION != UNLIMITED TOKENS
PORTABLE != SECRET INSTRUCTIONS
```

## Platform wallet / card top-up

Future commercial UX:

```text
User
↓
Add WebAI credit
↓
Card / supported payment method
↓
Wallet credit
↓
Inference requests debit wallet under cost + margin policy
```

The wallet balance is not the same record as raw provider spend. Preserve at least:

- customer credit/entitlement ledger;
- provider-cost ledger;
- platform fee/margin ledger;
- creator revenue ledger when revenue share exists.

Do not collapse these into one mutable balance field.

## Creator economics

Later, each execution can decompose into:

```text
USER CHARGE
├─ provider/tool cost
├─ payment/processing cost
├─ platform margin
└─ creator revenue
```

The formula is package/version specific and must not be inferred retroactively from current pricing.

## v0 boundary

For v0 Dogfood, implement/validate the schema boundary without building the entire marketplace.

Required now:

- access policy object exists;
- inference payer remains independent;
- `FREE` and a paid-access placeholder can coexist with BYOK;
- creator allowance can be bounded;
- hosted vs portable mode is represented;
- execution gate does not assume paid package means platform-funded inference.

Still deferred:

- live card top-up;
- refunds;
- subscription lifecycle;
- tax handling;
- creator payout/KYC;
- revenue-share settlement;
- persistent encrypted BYOK vault;
- public package marketplace.

## Product thesis

The simplest user gets:

> **Tap a URL and use the AI.**

The user who does not want API setup gets:

> **Add credit and use it.**

The power user gets:

> **Bring your own key, or take a portable package when the creator permits it.**

The creator gets:

> **Choose what the AI costs, who pays inference, how much you subsidize, and whether users can take the package with them.**

That combination is the distribution product, not merely the chat page.
