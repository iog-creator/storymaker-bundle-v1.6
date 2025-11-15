import httpx

BASE = "http://127.0.0.1:8700"

def test_healthz_enveloped():
    with httpx.Client(base_url=BASE, timeout=5) as c:
        j = c.get("/agentpm/healthz").json()
        assert j["status"] == "ok"
        assert "schema_present" in j["data"]

def test_version_enveloped():
    with httpx.Client(base_url=BASE, timeout=5) as c:
        j = c.get("/agentpm/version").json()
        assert j["status"] == "ok"
        assert j["data"]["version"].endswith("pr001")

def test_proofs_enveloped():
    with httpx.Client(base_url=BASE, timeout=5) as c:
        j = c.get("/agentpm/proofs").json()
        assert j["status"] == "ok"
        assert "runs" in j["data"]
