# narrative/providers/groq_client.py
import os, time
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from functools import lru_cache

# Make .env loading deterministic and shell-agnostic
try:
    from dotenv import load_dotenv  # pip install python-dotenv
    load_dotenv()
except Exception:
    pass

# Defensive import (don't crash at import time if Groq missing)
try:
    from groq import Groq
except Exception:  # pragma: no cover
    Groq = None  # type: ignore

DEFAULT_MODEL = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")
API_KEY_ENV   = "GROQ_API_KEY"

@dataclass
class GroqConfig:
    api_key: str
    model: str = DEFAULT_MODEL
    request_timeout: float = 20.0  # seconds (end-to-end per request)
    max_retries: int = 2
    retry_backoff_ms: int = 150

class GroqError(RuntimeError):
    pass

@lru_cache(maxsize=1)
def get_config() -> GroqConfig:
    key = os.environ.get(API_KEY_ENV, "").strip()
    if not key:
        raise GroqError(f"{API_KEY_ENV} is not set")
    return GroqConfig(api_key=key)

@lru_cache(maxsize=1)
def get_client() -> "Groq":
    if Groq is None:
        raise GroqError("groq SDK not installed. Try: pip install groq")
    cfg = get_config()
    return Groq(api_key=cfg.api_key)

def _sleep_ms(ms: int) -> None:
    time.sleep(ms / 1000.0)

def chat_complete(messages: List[Dict[str, str]], model: Optional[str] = None, **kwargs) -> str:
    """
    Deterministic, timeout-bounded wrapper around Groq chat.completions.create.
    Returns string content or raises GroqError with actionable details.
    """
    cfg = get_config()
    client = get_client()
    m = (model or cfg.model)

    # Map our single timeout to groq's args; also keep our own wall-clock guard
    request_timeout = float(kwargs.pop("request_timeout", cfg.request_timeout))
    max_retries     = int(kwargs.pop("max_retries", cfg.max_retries))
    backoff_ms      = int(kwargs.pop("retry_backoff_ms", cfg.retry_backoff_ms))

    start = time.perf_counter()
    attempt = 0
    last_err: Optional[Exception] = None

    while attempt <= max_retries:
        try:
            resp = client.chat.completions.create(
                model=m,
                messages=messages,
                temperature=kwargs.get("temperature", 0.8),
                max_tokens=kwargs.get("max_tokens", 900),
                top_p=kwargs.get("top_p", 0.95),
                timeout=request_timeout,  # groq SDK supports timeout
            )
            if not resp or not resp.choices:
                raise GroqError("Empty response from Groq")
            content = resp.choices[0].message.content or ""
            return content
        except Exception as e:  # noqa
            last_err = e
            # wall-clock guard
            if (time.perf_counter() - start) >= request_timeout:
                break
            if attempt >= max_retries:
                break
            _sleep_ms(backoff_ms * (attempt + 1))
            attempt += 1

    raise GroqError(f"Groq request failed: {str(last_err) if last_err else 'unknown'}")
