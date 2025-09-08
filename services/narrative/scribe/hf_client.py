from __future__ import annotations
import os, json, time
from typing import Any, Dict
import requests
from services.narrative.ledger import compute_promise_payoff, trope_budget_ok

# NO-MOCKS GUARD: Hard-fail if Groq API key is missing
if not os.getenv("GROQ_API_KEY", "").strip():
    raise RuntimeError("NO-MOCKS: GROQ_API_KEY is required; mocking creative gen is forbidden.")

# ---- Load prompts from docs/prompts (preferred) or local fallback ----
PROMPT_FILES = [
    os.path.join("docs", "prompts", "scribe_prompts.json"),
    os.path.join(os.path.dirname(__file__), "scribe_prompts.json")
]
def _load_prompts() -> Dict[str, Dict[str, str]]:
    for p in PROMPT_FILES:
        if os.path.exists(p):
            with open(p, "r", encoding="utf-8") as f:
                return json.load(f)
    raise RuntimeError("scribe_prompts.json not found")
PROMPTS = _load_prompts()

def _fill(t: str, vars: Dict[str, Any]) -> str:
    try:
        return t.format(**vars)
    except KeyError:
        return t
def _render(task: str, vars: Dict[str, Any]) -> str:
    spec = PROMPTS.get(task, {})
    system = _fill(spec.get("system", ""), vars)
    user = _fill(spec.get("user", ""), vars)
    # Use OpenAI format for Groq API (not Llama format)
    return f"{system}\n\n{user}"


def _defaults_for(task: str) -> Dict[str, Any]:
    # No artificial limits - let creativity flow
    if task in ("scene", "rewrite"):
        return {"temperature": 1.05, "top_p": 0.9, "repetition_penalty": 1.12}
    if task in ("outline", "character_bible"):
        return {"temperature": 0.8, "top_p": 0.9, "repetition_penalty": 1.1}
    # logline / lineedit / misc - no limits
    return {"temperature": 0.7, "top_p": 0.9, "repetition_penalty": 1.05}

def _backoff(retry: int) -> float:
    return 0.5 * (2 ** retry)  # 0.5,1,2,4,8

def _groq_infer(model_id: str, token: str, prompt: str, controls: Dict[str, Any]) -> str:
    """
    Generate text using Groq's direct API for 70B models.
    """
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Split prompt into system and user parts
    parts = prompt.split("\n\n", 1)
    if len(parts) == 2:
        system_msg, user_msg = parts
        messages = [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg}
        ]
    else:
        messages = [{"role": "user", "content": prompt}]
    
    data = {
        "model": model_id,
        "messages": messages,
        "temperature": controls.get("temperature", 0.7),
        "top_p": controls.get("top_p", 0.9)
    }
    
    for i in range(6):
        try:
            response = requests.post(url, headers=headers, json=data, timeout=120)
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
            
        except Exception as e:
            if i == 5:  # Last attempt
                raise RuntimeError(f"Groq inference failed: {e}")
            time.sleep(_backoff(i))
            continue
    
    raise RuntimeError("Groq inference failed after retries")


def generate(task: str, inputs: Dict[str, Any], controls: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """Groq generator for Narrative with 70B model. Returns {draft, model, provider, controls, issues}."""
    token = os.environ.get("GROQ_API_KEY", "").strip()
    model = os.environ.get("GROQ_MODEL", "").strip()
    if not token:
        raise RuntimeError("GROQ_API_KEY is required")
    if not model:
        raise RuntimeError("GROQ_MODEL is required")
    
    # Merge caller controls over task defaults
    base = _defaults_for(task)
    controls = {**base, **(controls or {})}
    
    prompt = _render(task, inputs or {})
    text = _groq_infer(model, token, prompt, controls)
    out = {"draft": text, "model": model, "provider": "groq", "controls": controls}

    # Narrative QA
    banned = inputs.get("trope_bans", [
        "chosen one","ancient prophecy","dark lord","it was all a dream",
        "mysterious stranger","forbidden forest","destined to",
        "balance of light and dark","last of their kind","prophecy foretold","bloodline power"
    ])
    ok_trope, counts = trope_budget_ok(out["draft"], banned=banned, max_per_1k=2)
    issues = []
    if not ok_trope:
        issues.append({"type": "trope_budget", "counts": counts})
    cards = inputs.get("cards")
    if cards:
        ledger = compute_promise_payoff(cards)
        if ledger["orphans"]:
            issues.append({"type": "promise_orphans", "items": ledger["orphans"]})
        if ledger["extraneous"]:
            issues.append({"type": "promise_extraneous", "items": ledger["extraneous"]})
    out["issues"] = issues
    return out