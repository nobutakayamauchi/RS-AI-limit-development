from __future__ import annotations

import json
import os
import time
from collections import defaultdict, deque
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

BASE_DIR = Path(__file__).resolve().parent
CONFIG_DIR = Path(os.getenv("WEB_AI_CONFIG_DIR", BASE_DIR / "apps"))
STATIC_DIR = BASE_DIR / "static"


class HistoryMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1)


class ChatRequest(BaseModel):
    slug: str = Field(min_length=1, max_length=120, pattern=r"^[a-z0-9][a-z0-9-]*$")
    message: str = Field(min_length=1)
    history: list[HistoryMessage] = Field(default_factory=list)


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
            data["_instructions"] = instruction_path.read_text(encoding="utf-8")
            apps[slug] = data
        self.apps = apps

    def get(self, slug: str) -> dict:
        app = self.apps.get(slug)
        if not app:
            raise KeyError(slug)
        return app


registry = AppRegistry(CONFIG_DIR)
app = FastAPI(title="WebAI Bridge Prototype", version="0.0.1")

# Deliberately small single-process v0 limiter. Replace before multi-worker scale.
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
    return {
        "slug": app_config["slug"],
        "display_name": app_config.get("display_name", app_config["slug"]),
        "status": app_config.get("status", "unknown"),
        "welcome": app_config.get("ui", {}).get("welcome", "Ask me anything."),
    }


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "app_count": len(registry.apps)}


@app.get("/runtime")
def runtime_identity() -> dict:
    return {
        "service_unit": os.getenv("WEB_AI_SERVICE_UNIT", "UNSET"),
        "working_directory": os.getenv("WEB_AI_WORKING_DIRECTORY", str(BASE_DIR)),
        "entrypoint": "app:app",
        "route_surface": os.getenv("WEB_AI_ROUTE_SURFACE", "UNSET"),
        "deployed_revision": os.getenv("DEPLOYED_REVISION", "UNSET"),
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
def chat(payload: ChatRequest, request: Request) -> dict:
    enforce_rate_limit(request)
    try:
        app_config = registry.get(payload.slug)
    except KeyError:
        raise HTTPException(status_code=404, detail="Unknown app") from None

    usage = app_config.get("usage", {})
    max_input_chars = int(usage.get("max_input_chars", 12000))
    max_history_messages = int(usage.get("max_history_messages", 12))
    if len(payload.message) > max_input_chars:
        raise HTTPException(status_code=413, detail="Message too large")
    if len(payload.history) > max_history_messages:
        raise HTTPException(status_code=413, detail="Conversation history too large")

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=503, detail="AI service is not configured")

    model_env = app_config.get("model_env", "WEB_AI_MODEL")
    model = os.getenv(model_env)
    if not model:
        raise HTTPException(status_code=503, detail="AI model is not configured")

    input_messages = [m.model_dump() for m in payload.history]
    input_messages.append({"role": "user", "content": payload.message})

    kwargs: dict = {
        "model": model,
        "instructions": app_config["_instructions"],
        "input": input_messages,
        "store": False,
    }

    knowledge = app_config.get("knowledge", {})
    if knowledge.get("enabled"):
        vector_env = knowledge.get("vector_store_env")
        vector_store_id = os.getenv(vector_env or "") if vector_env else None
        if not vector_store_id:
            raise HTTPException(status_code=503, detail="Knowledge store is not configured")
        kwargs["tools"] = [
            {"type": "file_search", "vector_store_ids": [vector_store_id]}
        ]

    from openai import OpenAI

    client = OpenAI(api_key=api_key)
    try:
        response = client.responses.create(**kwargs)
    except Exception as exc:
        # Do not reflect provider error internals or secrets to the browser.
        raise HTTPException(status_code=502, detail="Upstream AI request failed") from exc

    text = (response.output_text or "").strip()
    if not text:
        raise HTTPException(status_code=502, detail="AI returned no text")
    return {"text": text}
