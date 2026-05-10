from __future__ import annotations

import json
from urllib import request
from urllib.error import HTTPError

from .storage import ProviderRecord


class ProviderError(Exception):
    pass


def _post_json(url: str, payload: dict, api_key: str, timeout: int = 60) -> dict:
    body = json.dumps(payload).encode("utf-8")
    req = request.Request(url=url, data=body, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("Authorization", f"Bearer {api_key}")
    try:
        with request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw)
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="ignore")
        raise ProviderError(f"provider HTTP {exc.code}: {detail[:300]}") from exc


def chat(provider: ProviderRecord, message: str) -> str:
    if provider.provider_type == "openai":
        return _chat_openai(provider, message)
    if provider.provider_type == "anthropic":
        return _chat_anthropic(provider, message)
    if provider.provider_type == "openai_compatible":
        return _chat_openai_compatible(provider, message)
    raise ProviderError(f"unsupported provider_type: {provider.provider_type}")


def _chat_openai(provider: ProviderRecord, message: str) -> str:
    url = provider.base_url.rstrip("/") + "/chat/completions"
    payload = {
        "model": provider.model,
        "messages": [{"role": "user", "content": message}],
        "temperature": 0.2,
    }
    res = _post_json(url, payload, provider.api_key)
    try:
        return res["choices"][0]["message"]["content"].strip()
    except Exception as exc:  # noqa: BLE001
        raise ProviderError(f"invalid OpenAI response shape: {res}") from exc


def _chat_openai_compatible(provider: ProviderRecord, message: str) -> str:
    return _chat_openai(provider, message)


def _chat_anthropic(provider: ProviderRecord, message: str) -> str:
    url = provider.base_url.rstrip("/") + "/messages"
    body = json.dumps(
        {
            "model": provider.model,
            "max_tokens": 1000,
            "messages": [{"role": "user", "content": message}],
        }
    ).encode("utf-8")
    req = request.Request(url=url, data=body, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("x-api-key", provider.api_key)
    req.add_header("anthropic-version", "2023-06-01")
    try:
        with request.urlopen(req, timeout=60) as resp:
            raw = resp.read().decode("utf-8")
            res = json.loads(raw)
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="ignore")
        raise ProviderError(f"provider HTTP {exc.code}: {detail[:300]}") from exc

    try:
        blocks = res["content"]
        text_parts = [b.get("text", "") for b in blocks if isinstance(b, dict)]
        return "\n".join([p for p in text_parts if p]).strip()
    except Exception as exc:  # noqa: BLE001
        raise ProviderError(f"invalid Anthropic response shape: {res}") from exc
