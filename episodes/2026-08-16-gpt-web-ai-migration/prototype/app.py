from __future__ import annotations

import json
import os
import sqlite3
import time
from collections import defaultdict, deque
from decimal import Decimal, ROUND_CEILING
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

BASE_DIR = Path(__file__).resolve().parent
CONFIG_DIR = Path(os.getenv("WEB_AI_CONFIG_DIR", BASE_DIR / "apps"))
STATIC_DIR = BASE_DIR / "static"
PRICING_FILE = Path(os.getenv("WEB_AI_PRICING_FILE", BASE_DIR / "pricing.json"))
LEDGER_PATH = Path(
    os.getenv("WEB_AI_LEDGER_PATH", BASE_DIR / ".runtime" / "webai-ledger.sqlite3")
)


class HistoryMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1)


class ChatRequest(BaseModel):
    slug: str = Field(min_length=1, max_length=120, pattern=r"^[a-z0-9][a-z0-9-]*$")
    message: str = Field(min_length=1)
    history: list[HistoryMessage] = Field(default_factory=list)
    payer_mode: Literal["BYOK", "PLATFORM_CREDIT"] | None = None


class AppRegistry:
    def __init__(self, config_dir: Path):
        self.config_dir = config_dir
        self.apps: dict[str, dict] = {}
        self.reload()

    def reload(self) -> None:
        apps: dict[str, dict] = {}
        if not self.config_dir.exists():
            self.apps = apps
            return
        for path in sorted(self.config_dir.glob("*.json")):
            data = json.loads(path.read_text(encoding="utf-8"))
            slug = data.get("slug")
            if not isinstance(slug, str) or not slug:
                raise ValueError(f"missing slug: {path}")
            if slug in apps:
                raise ValueError(f"duplicate slug: {slug}")
            instructions_file = data.get("instructions_file")
            if not instructions_file:
                raise ValueError(f"missing instructions_file: {slug}")
            instruction_path = BASE_DIR / instructions_file
            if not instruction_path.exists():
                raise ValueError(f"instructions file not found: {instruction_path}")

            billing = data.get("billing") or {}
            allowed_payers = billing.get("allowed_payer_modes") or []
            default_payer = billing.get("default_payer_mode")
            if not allowed_payers or default_payer not in allowed_payers:
                raise ValueError(f"invalid billing payer policy: {slug}")

            routing = data.get("routing") or {}
            default_model = routing.get("default_model")
            allowed_models = routing.get("allowed_models") or []
            if not default_model or default_model not in allowed_models:
                raise ValueError(f"invalid routing policy: {slug}")

            data["_instructions"] = instruction_path.read_text(encoding="utf-8")
            apps[slug] = data
        self.apps = apps

    def get(self, slug: str) -> dict:
        app_config = self.apps.get(slug)
        if not app_config:
            raise KeyError(slug)
        return app_config


class PricingRegistry:
    def __init__(self, path: Path):
        self.path = path
        self.version = "UNSET"
        self.source = "UNSET"
        self.models: dict[str, dict] = {}
        self.reload()

    def reload(self) -> None:
        if not self.path.exists():
            self.version = "UNSET"
            self.source = "UNSET"
            self.models = {}
            return
        data = json.loads(self.path.read_text(encoding="utf-8"))
        self.version = str(data.get("version") or "UNSET")
        self.source = str(data.get("source") or "UNSET")
        self.models = dict(data.get("models") or {})

    def get(self, model: str) -> dict:
        price = self.models.get(model)
        if not price:
            raise KeyError(model)
        return price


class BudgetLedger:
    """Small persistent v0 ledger.

    Reservations happen in a SQLite `BEGIN IMMEDIATE` transaction so two requests
    cannot both spend the same remaining platform-funded budget.
    """

    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self):
        conn = sqlite3.connect(self.path, timeout=10, isolation_level=None)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS budgets (
                    budget_id TEXT PRIMARY KEY,
                    hard_limit_micros INTEGER NOT NULL,
                    spent_micros INTEGER NOT NULL DEFAULT 0,
                    reserved_micros INTEGER NOT NULL DEFAULT 0
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS usage_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at INTEGER NOT NULL,
                    package_id TEXT NOT NULL,
                    payer_mode TEXT NOT NULL,
                    budget_id TEXT,
                    provider TEXT NOT NULL,
                    model TEXT NOT NULL,
                    pricing_version TEXT NOT NULL,
                    input_tokens INTEGER,
                    output_tokens INTEGER,
                    reserved_cost_micros INTEGER NOT NULL,
                    actual_cost_micros INTEGER,
                    charged_cost_micros INTEGER NOT NULL,
                    result TEXT NOT NULL
                )
                """
            )

    def reserve(self, budget_id: str, hard_limit_micros: int, amount_micros: int) -> bool:
        if amount_micros <= 0:
            raise ValueError("reservation must be positive")
        with self._connect() as conn:
            conn.execute("BEGIN IMMEDIATE")
            row = conn.execute(
                "SELECT hard_limit_micros, spent_micros, reserved_micros FROM budgets WHERE budget_id=?",
                (budget_id,),
            ).fetchone()
            if row is None:
                conn.execute(
                    "INSERT INTO budgets (budget_id, hard_limit_micros, spent_micros, reserved_micros) VALUES (?, ?, 0, 0)",
                    (budget_id, hard_limit_micros),
                )
                effective_limit = hard_limit_micros
                spent = 0
                reserved = 0
            else:
                # Config changes never silently increase an already persisted budget.
                effective_limit = min(int(row["hard_limit_micros"]), hard_limit_micros)
                spent = int(row["spent_micros"])
                reserved = int(row["reserved_micros"])

            if spent + reserved + amount_micros > effective_limit:
                conn.execute("ROLLBACK")
                return False

            conn.execute(
                "UPDATE budgets SET reserved_micros = reserved_micros + ?, hard_limit_micros=? WHERE budget_id=?",
                (amount_micros, effective_limit, budget_id),
            )
            conn.execute("COMMIT")
            return True

    def settle(
        self,
        *,
        budget_id: str,
        reserved_micros: int,
        charged_micros: int,
        package_id: str,
        payer_mode: str,
        provider: str,
        model: str,
        pricing_version: str,
        input_tokens: int | None,
        output_tokens: int | None,
        actual_cost_micros: int | None,
        result: str,
    ) -> None:
        if charged_micros < 0 or charged_micros > reserved_micros:
            raise ValueError("charged cost must fit reservation")
        with self._connect() as conn:
            conn.execute("BEGIN IMMEDIATE")
            row = conn.execute(
                "SELECT reserved_micros FROM budgets WHERE budget_id=?", (budget_id,)
            ).fetchone()
            if row is None or int(row["reserved_micros"]) < reserved_micros:
                conn.execute("ROLLBACK")
                raise RuntimeError("budget reservation missing")
            conn.execute(
                "UPDATE budgets SET reserved_micros = reserved_micros - ?, spent_micros = spent_micros + ? WHERE budget_id=?",
                (reserved_micros, charged_micros, budget_id),
            )
            conn.execute(
                """INSERT INTO usage_events
                   (created_at, package_id, payer_mode, budget_id, provider, model, pricing_version,
                    input_tokens, output_tokens, reserved_cost_micros, actual_cost_micros,
                    charged_cost_micros, result)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    int(time.time()),
                    package_id,
                    payer_mode,
                    budget_id,
                    provider,
                    model,
                    pricing_version,
                    input_tokens,
                    output_tokens,
                    reserved_micros,
                    actual_cost_micros,
                    charged_micros,
                    result,
                ),
            )
            conn.execute("COMMIT")

    def release_failed(
        self,
        *,
        budget_id: str,
        reserved_micros: int,
        package_id: str,
        provider: str,
        model: str,
        pricing_version: str,
        result: str,
    ) -> None:
        with self._connect() as conn:
            conn.execute("BEGIN IMMEDIATE")
            conn.execute(
                "UPDATE budgets SET reserved_micros = MAX(0, reserved_micros - ?) WHERE budget_id=?",
                (reserved_micros, budget_id),
            )
            conn.execute(
                """INSERT INTO usage_events
                   (created_at, package_id, payer_mode, budget_id, provider, model, pricing_version,
                    input_tokens, output_tokens, reserved_cost_micros, actual_cost_micros,
                    charged_cost_micros, result)
                   VALUES (?, ?, 'PLATFORM_CREDIT', ?, ?, ?, ?, NULL, NULL, ?, NULL, 0, ?)""",
                (
                    int(time.time()),
                    package_id,
                    budget_id,
                    provider,
                    model,
                    pricing_version,
                    reserved_micros,
                    result,
                ),
            )
            conn.execute("COMMIT")


registry = AppRegistry(CONFIG_DIR)
pricing = PricingRegistry(PRICING_FILE)
ledger = BudgetLedger(LEDGER_PATH)
app = FastAPI(title="WebAI Bridge Prototype", version="0.0.2")

# Separate from the financial ledger: this is only a basic abuse-rate gate.
_request_times: dict[str, deque[float]] = defaultdict(deque)


def enforce_rate_limit(request: Request) -> None:
    limit = int(os.getenv("WEB_AI_REQUESTS_PER_MINUTE", "20"))
    now = time.monotonic()
    key = request.client.host if request.client else "unknown"
    q = _request_times[key]
    while q and now - q[0] > 60:
        q.popleft()
    if len(q) >= limit:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    q.append(now)


def public_config(app_config: dict) -> dict:
    billing = app_config["billing"]
    return {
        "slug": app_config["slug"],
        "display_name": app_config.get("display_name", app_config["slug"]),
        "status": app_config.get("status", "unknown"),
        "welcome": app_config.get("ui", {}).get("welcome", "Ask me anything."),
        "allowed_payer_modes": billing["allowed_payer_modes"],
        "default_payer_mode": billing["default_payer_mode"],
    }


def resolve_payer_mode(payload: ChatRequest, app_config: dict) -> str:
    billing = app_config["billing"]
    payer_mode = payload.payer_mode or billing["default_payer_mode"]
    if payer_mode not in billing["allowed_payer_modes"]:
        raise HTTPException(status_code=403, detail="Payer mode is not allowed")
    return payer_mode


def resolve_model(app_config: dict) -> str:
    routing = app_config["routing"]
    model = routing["default_model"]
    if model not in routing["allowed_models"]:
        raise HTTPException(status_code=503, detail="Model routing policy is invalid")
    return model


def token_upper_bound(text: str) -> int:
    # Deliberately conservative byte-bound approximation used only to reserve
    # platform-funded budget before execution.
    return len(text.encode("utf-8")) + 8


def request_input_token_upper_bound(
    payload: ChatRequest, instructions: str, knowledge_reserve_tokens: int
) -> int:
    total = token_upper_bound(instructions) + token_upper_bound(payload.message)
    for item in payload.history:
        total += token_upper_bound(item.content) + 8
    return total + max(0, knowledge_reserve_tokens)


def cost_micros(*, input_tokens: int, output_tokens: int, price: dict) -> int:
    # Because rates are USD / 1M tokens and 1 USD = 1M microdollars,
    # tokens * rate directly yields microdollars.
    input_rate = Decimal(str(price["input_usd_per_1m"]))
    output_rate = Decimal(str(price["output_usd_per_1m"]))
    value = (Decimal(input_tokens) * input_rate) + (
        Decimal(output_tokens) * output_rate
    )
    return int(value.to_integral_value(rounding=ROUND_CEILING))


def extract_usage(response) -> tuple[int | None, int | None]:
    usage = getattr(response, "usage", None)
    if usage is None:
        return None, None
    input_tokens = getattr(usage, "input_tokens", None)
    output_tokens = getattr(usage, "output_tokens", None)
    if not isinstance(input_tokens, int) or not isinstance(output_tokens, int):
        return None, None
    return input_tokens, output_tokens


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "app_count": len(registry.apps),
        "pricing_version": pricing.version,
    }


@app.get("/runtime")
def runtime_identity() -> dict:
    return {
        "service_unit": os.getenv("WEB_AI_SERVICE_UNIT", "UNSET"),
        "working_directory": os.getenv("WEB_AI_WORKING_DIRECTORY", str(BASE_DIR)),
        "entrypoint": "app:app",
        "route_surface": os.getenv("WEB_AI_ROUTE_SURFACE", "UNSET"),
        "deployed_revision": os.getenv("DEPLOYED_REVISION", "UNSET"),
        "pricing_version": pricing.version,
        "ledger_path": str(LEDGER_PATH),
    }


@app.get("/apps/{slug}/public-config")
def get_public_config(slug: str) -> dict:
    try:
        return public_config(registry.get(slug))
    except KeyError:
        raise HTTPException(status_code=404, detail="Unknown app") from None


@app.get("/a/{slug}")
def app_page(slug: str):
    try:
        registry.get(slug)
    except KeyError:
        raise HTTPException(status_code=404, detail="Unknown app") from None
    return FileResponse(STATIC_DIR / "index.html")


@app.post("/api/chat")
def chat(
    payload: ChatRequest,
    request: Request,
    byok_api_key: str | None = Header(default=None, alias="X-Provider-API-Key"),
) -> dict:
    enforce_rate_limit(request)
    try:
        app_config = registry.get(payload.slug)
    except KeyError:
        raise HTTPException(status_code=404, detail="Unknown app") from None

    usage_policy = app_config.get("usage", {})
    max_input_chars = int(usage_policy.get("max_input_chars", 12000))
    max_history_messages = int(usage_policy.get("max_history_messages", 12))
    max_output_tokens = int(usage_policy.get("max_output_tokens", 2048))
    if len(payload.message) > max_input_chars:
        raise HTTPException(status_code=413, detail="Message too large")
    if len(payload.history) > max_history_messages:
        raise HTTPException(status_code=413, detail="Conversation history too large")

    # Economic authorization happens before any provider execution.
    payer_mode = resolve_payer_mode(payload, app_config)
    model = resolve_model(app_config)

    knowledge = app_config.get("knowledge", {})
    knowledge_enabled = bool(knowledge.get("enabled"))
    tool_reserve_micros = 0
    knowledge_reserve_tokens = 0

    if knowledge_enabled:
        vector_env = knowledge.get("vector_store_env")
        vector_store_id = os.getenv(vector_env or "") if vector_env else None
        if not vector_store_id:
            raise HTTPException(status_code=503, detail="Knowledge store is not configured")
        if payer_mode == "PLATFORM_CREDIT":
            # File/tool costs are external mutable pricing. A platform-funded
            # Knowledge request is blocked unless an explicit reserve policy exists.
            pc_policy = knowledge.get("platform_credit") or {}
            if not pc_policy.get("enabled"):
                raise HTTPException(
                    status_code=503,
                    detail="Platform-funded Knowledge cost policy is not configured",
                )
            knowledge_reserve_tokens = int(pc_policy.get("reserve_input_tokens", 0))
            tool_reserve_micros = int(pc_policy.get("tool_reserve_usd_micros", 0))
            if knowledge_reserve_tokens <= 0 or tool_reserve_micros < 0:
                raise HTTPException(
                    status_code=503,
                    detail="Platform-funded Knowledge reserve is invalid",
                )
    else:
        vector_store_id = None

    reservation_micros = 0
    budget_id = None
    price = None

    if payer_mode == "BYOK":
        # Session/request-scoped BYOK: never persisted by this prototype.
        api_key = (byok_api_key or "").strip()
        if not api_key:
            raise HTTPException(status_code=402, detail="BYOK provider API key is required")
    else:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise HTTPException(status_code=503, detail="Platform AI service is not configured")
        try:
            price = pricing.get(model)
        except KeyError:
            raise HTTPException(status_code=503, detail="Model price is not configured") from None

        billing = app_config["billing"]["platform_credit"]
        if not billing.get("enabled"):
            raise HTTPException(status_code=403, detail="Platform credit is disabled")
        budget_env = billing.get("budget_id_env")
        budget_id = os.getenv(budget_env or "") if budget_env else None
        if not budget_id:
            raise HTTPException(status_code=503, detail="Platform budget is not configured")
        hard_limit_micros = int(billing.get("hard_limit_usd_micros", 0))
        if hard_limit_micros <= 0:
            raise HTTPException(status_code=503, detail="Platform budget limit is invalid")

        input_upper = request_input_token_upper_bound(
            payload, app_config["_instructions"], knowledge_reserve_tokens
        )
        reservation_micros = cost_micros(
            input_tokens=input_upper,
            output_tokens=max_output_tokens,
            price=price,
        ) + tool_reserve_micros
        if not ledger.reserve(budget_id, hard_limit_micros, reservation_micros):
            raise HTTPException(status_code=402, detail="Platform inference budget exhausted")

    input_messages = [m.model_dump() for m in payload.history]
    input_messages.append({"role": "user", "content": payload.message})
    kwargs: dict = {
        "model": model,
        "instructions": app_config["_instructions"],
        "input": input_messages,
        "store": False,
        "max_output_tokens": max_output_tokens,
    }
    if knowledge_enabled:
        kwargs["tools"] = [
            {"type": "file_search", "vector_store_ids": [vector_store_id]}
        ]

    from openai import OpenAI

    client = OpenAI(api_key=api_key)
    try:
        response = client.responses.create(**kwargs)
    except Exception as exc:
        if payer_mode == "PLATFORM_CREDIT" and budget_id:
            ledger.release_failed(
                budget_id=budget_id,
                reserved_micros=reservation_micros,
                package_id=payload.slug,
                provider="openai",
                model=model,
                pricing_version=pricing.version,
                result="PROVIDER_ERROR",
            )
        raise HTTPException(status_code=502, detail="Upstream AI request failed") from exc

    text = (response.output_text or "").strip()
    if not text:
        if payer_mode == "PLATFORM_CREDIT" and budget_id:
            ledger.release_failed(
                budget_id=budget_id,
                reserved_micros=reservation_micros,
                package_id=payload.slug,
                provider="openai",
                model=model,
                pricing_version=pricing.version,
                result="EMPTY_RESPONSE",
            )
        raise HTTPException(status_code=502, detail="AI returned no text")

    input_tokens, output_tokens = extract_usage(response)
    actual_cost_micros = None
    charged_micros = 0
    cost_state = "NOT_PLATFORM_BILLED"

    if payer_mode == "PLATFORM_CREDIT" and budget_id and price:
        if input_tokens is None or output_tokens is None:
            # Economically fail safe: if usage proof is missing after a successful
            # provider call, charge the already-authorized reservation rather than
            # silently treating real provider spend as zero.
            charged_micros = reservation_micros
            cost_state = "COST_UNKNOWN_CHARGED_RESERVATION"
        else:
            actual_cost_micros = cost_micros(
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                price=price,
            ) + tool_reserve_micros
            charged_micros = min(actual_cost_micros, reservation_micros)
            cost_state = (
                "ACTUAL"
                if actual_cost_micros <= reservation_micros
                else "UNDER_RESERVED_CHARGED_CAP"
            )
        ledger.settle(
            budget_id=budget_id,
            reserved_micros=reservation_micros,
            charged_micros=charged_micros,
            package_id=payload.slug,
            payer_mode=payer_mode,
            provider="openai",
            model=model,
            pricing_version=pricing.version,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            actual_cost_micros=actual_cost_micros,
            result="SUCCESS",
        )

    return {
        "text": text,
        "meter": {
            "payer_mode": payer_mode,
            "model": model,
            "pricing_version": pricing.version
            if payer_mode == "PLATFORM_CREDIT"
            else None,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "charged_cost_usd_micros": charged_micros
            if payer_mode == "PLATFORM_CREDIT"
            else None,
            "cost_state": cost_state,
        },
    }
