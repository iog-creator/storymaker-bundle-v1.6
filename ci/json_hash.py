#!/usr/bin/env python3
import sys, json, hashlib
"""
Reads an envelope on stdin, removes `.proof`, dumps with sort_keys=True and
separators=(',', ':'), and prints the sha256 hex digest.
"""
doc = json.load(sys.stdin)
if isinstance(doc, dict) and "proof" in doc:
    del doc["proof"]
canon = json.dumps(doc, sort_keys=True, separators=(",", ":"))
print(hashlib.sha256(canon.encode("utf-8")).hexdigest())
