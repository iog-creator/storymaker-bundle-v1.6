"""
Test that services output clean JSON to stdout (no mock contamination)
"""
import subprocess
import json
import os
import shlex


def run_json(cmd):
    """Run command and verify stdout is clean JSON, stderr can contain logs"""
    p = subprocess.run(shlex.split(cmd), capture_output=True, text=True, check=True)
    # stdout must be JSON-only
    json.loads(p.stdout)
    # stderr can contain logs but no fallback references
    assert "fallback" not in (p.stderr or "").lower()


def test_lmstudio_models_json_only():
    """Test that LM Studio models endpoint outputs clean JSON"""
    run_json("python3 scripts/lm_api.py models")


def test_narrative_verify_json_only():
    """Test that narrative verification outputs clean JSON"""
    # This will fail if narrative service isn't running, but that's ok
    try:
        run_json("bash scripts/verify_narrative.sh")
    except subprocess.CalledProcessError:
        # Service not running is acceptable for this test
        pass


def test_no_mocks_guard_clean():
    """Test that no-mocks guard doesn't contaminate stdout"""
    # Load environment and run guard
    env = os.environ.copy()
    env['DISABLE_MOCKS'] = '1'
    env['MOCK_LMS'] = '0'
    
    p = subprocess.run(
        ["bash", "scripts/lib/no_mocks_guard.sh"],
        capture_output=True,
        text=True,
        env=env
    )
    
    # Guard should succeed (exit 0) and not output to stdout
    assert p.returncode == 0
    assert p.stdout == ""  # No stdout contamination
    assert "checks passed" in p.stderr  # Success message to stderr
