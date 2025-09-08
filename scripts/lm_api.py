#!/usr/bin/env python3
"""
lm_api.py — stdlib-only Python client for LM Studio's OpenAI-compatible API.
Emits EXACTLY ONE Envelope v1.1 JSON to stdout.

Usage:
  python scripts/lm_api.py models
  python scripts/lm_api.py chat --prompt "ping" [--system "Reply with a single word: pong"] [--model ID] [--max-tokens 16] [--temperature 0]

Env:
  OPENAI_API_BASE (default: http://127.0.0.1:1234/v1)
  OPENAI_API_KEY  (default: lm-studio)
  MOCK_LMS=1      (simulate success without hitting network)

Exit codes:
"""

# Self-healing bootstrap: re-invoke through run.sh if not already loaded
import os, sys, subprocess, pathlib
if os.environ.get("RUN_SH") != "1":
    run_sh = pathlib.Path(__file__).parent / "run.sh"
    os.execv("/bin/bash", ["bash", str(run_sh), sys.executable, __file__, *sys.argv[1:]])
import argparse, json, os, sys, urllib.request, urllib.error

def _env(name, default=None):
    v = os.environ.get(name)
    return v if v is not None else default

def emit_envelope(status, smoke, reasons, data=None, checks=None, proofs=None, error_message=""):
    env = {
        "status": status,
        "data": data or {},
        "error": {"message": error_message if status != "success" else "", "details": {}},
        "meta": {
            "smoke_score": float(smoke),
            "reasons": reasons if reasons else (["ok"] if status == "success" else ["unspecified"]),
            "scope": ["scripts/lm_api.py"],
            "checks": checks or [],
            "proofs": proofs or []
        }
    }
    print(json.dumps(env, ensure_ascii=False))
    # single envelope only: stdout contains exactly one JSON object

def http_get_json(url, headers=None, timeout=4):
    req = urllib.request.Request(url, headers=headers or {})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))

def http_post_json(url, payload, headers=None, timeout=8):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json", **(headers or {})})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))

def cmd_models(base, mock):
    reasons, checks, proofs = [], [], []
    if mock:
        models = {"data": [{"id": "mock-model", "object": "model"}]}
    else:
        try:
            models = http_get_json(base.rstrip("/") + "/models", timeout=4)
        except Exception as e:
            emit_envelope("error", 1.0, ["models_fetch_failed"], data={"base": base}, error_message=str(e))
            return
    arr = models.get("data") or []
    count = len(arr)
    if count < 1:
        emit_envelope("error", 1.0, ["no_models_loaded"], data={"base": base, "count": count})
        return
    first = (arr[0] or {}).get("id", "")
    checks.append({"name": "models_count_ge_1", "pass": True})
    proofs.append(f"first_model={first}")
    emit_envelope("success", 0.0, ["lm_models_ok"], data={"base": base, "count": count, "models": arr[:3]}, checks=checks, proofs=proofs)

def cmd_chat(base, api_key, model, prompt, system_msg, max_tokens, temperature, mock):
    reasons, checks, proofs = [], [], []
    content = ""
    if mock:
        content = "pong"
    else:
        # discover default model if not provided
        if not model:
            try:
                models = http_get_json(base.rstrip("/") + "/models", timeout=4)
                # Filter out embedding models for chat
                chat_models = [m for m in (models.get("data") or []) if not ("embedding" in m.get("id", "").lower())]
                model = (chat_models[0] if chat_models else {}).get("id", "")
            except Exception as e:
                emit_envelope("error", 1.0, ["models_fetch_failed"], data={"base": base}, error_message=str(e))
                return
        if not model:
            emit_envelope("error", 1.0, ["no_model_for_chat"], data={"base": base})
            return
        payload = {
            "model": model,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "messages": [
                {"role": "system", "content": system_msg},
                {"role": "user", "content": prompt}
            ]
        }
        headers = {"Authorization": f"Bearer {api_key}"}
        try:
            resp = http_post_json(base.rstrip("/") + "/chat/completions", payload, headers=headers, timeout=8)
            content = (((resp.get("choices") or [{}])[0]).get("message") or {}).get("content", "") or ""
        except Exception as e:
            emit_envelope("error", 1.0, ["chat_request_failed"], data={"base": base, "model": model}, error_message=str(e))
            return

    if not content:
        emit_envelope("error", 1.0, ["chat_no_content"], data={"base": base, "model": model})
        return
    preview = (content[:32] + "...") if len(content) > 32 else content
    checks.append({"name": "chat_reply_nonempty", "pass": True})
    proofs.append(f"len={len(content)}")
    emit_envelope("success", 0.0, ["chat_ok"], data={"base": base, "model": model, "preview": preview}, checks=checks, proofs=proofs)

def main():
    base = _env("OPENAI_API_BASE", "http://127.0.0.1:1234/v1")
    api_key = _env("OPENAI_API_KEY", "lm-studio")
    mock = _env("MOCK_LMS", "0") == "1"

    p = argparse.ArgumentParser(description="LM Studio Envelope CLI (stdlib only)")
    sub = p.add_subparsers(dest="cmd", required=True)

    sp_models = sub.add_parser("models", help="List models (envelope)")
    sp_models.set_defaults(func=lambda _: cmd_models(base, mock))

    sp_chat = sub.add_parser("chat", help="Chat smoke (envelope)")
    sp_chat.add_argument("--prompt", required=True)
    sp_chat.add_argument("--system", dest="system_msg", default="Reply with a single word: pong")
    sp_chat.add_argument("--model", default="")
    sp_chat.add_argument("--max-tokens", type=int, default=16)
    sp_chat.add_argument("--temperature", type=float, default=0.0)
    sp_chat.set_defaults(func=lambda args: cmd_chat(
        base, api_key, args.model, args.prompt, args.system_msg, args.max_tokens, args.temperature, mock
    ))

    args = p.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
