"""
Property-based tests for envelope gate invariants.
"""

import pytest
from hypothesis import given, strategies as st
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "packages"))
from pmagent.envelope_validator import validate_envelope, _env_ok, _env_err


class TestEnvelopeGateInvariants:
    """Test envelope gate invariants using property-based testing."""
    
    @given(st.dictionaries(
        keys=st.text(min_size=1, max_size=20).filter(lambda x: x not in ["status", "data", "error", "meta"]),
        values=st.one_of(
            st.text(),
            st.integers(),
            st.booleans(),
            st.none(),
            st.lists(st.text())
        ),
        min_size=1,
        max_size=10
    ))
    def test_additional_properties_rejected(self, data):
        """Any object with additional properties should be rejected."""
        # Create a valid envelope structure
        valid_envelope = _env_ok({"test": "data"})
        
        # Add additional properties
        invalid_envelope = {**valid_envelope, **data}
        
        is_valid, error_code, violations = validate_envelope(invalid_envelope)
        
        # Should be invalid due to additional properties
        assert not is_valid
        assert error_code == "ADDITIONAL_PROPERTIES"
        assert violations is not None
        assert len(violations) > 0
    
    @given(st.text())
    def test_non_dict_rejected(self, data):
        """Non-dict data should be rejected."""
        is_valid, error_code, violations = validate_envelope(data)
        
        assert not is_valid
        assert error_code == "INVALID_TYPE"
        assert violations is not None
        assert "Data must be a JSON object" in violations[0]
    
    def test_ok_status_requires_data(self):
        """OK status must have data field and error must be null."""
        # Missing data field
        invalid = {
            "status": "ok",
            "error": None,
            "meta": {"run_id": "test", "timestamp": "2025-01-01T00:00:00Z", "source": "test", "schema_version": "1.1.0-pr000"}
        }
        
        is_valid, error_code, violations = validate_envelope(invalid)
        assert not is_valid
        assert error_code == "MISSING_DATA"
        
        # Error field not null
        invalid2 = {
            "status": "ok",
            "data": {"test": "data"},
            "error": {"code": "test", "message": "test"},
            "meta": {"run_id": "test", "timestamp": "2025-01-01T00:00:00Z", "source": "test", "schema_version": "1.1.0-pr000"}
        }
        
        is_valid, error_code, violations = validate_envelope(invalid2)
        assert not is_valid
        assert error_code == "INVALID_ERROR_FIELD"
    
    def test_error_status_requires_error(self):
        """Error status must have error field and data must be null."""
        # Missing error field
        invalid = {
            "status": "error",
            "data": None,
            "meta": {"run_id": "test", "timestamp": "2025-01-01T00:00:00Z", "source": "test", "schema_version": "1.1.0-pr000"}
        }
        
        is_valid, error_code, violations = validate_envelope(invalid)
        assert not is_valid
        assert error_code == "MISSING_ERROR"
        
        # Data field not null
        invalid2 = {
            "status": "error",
            "data": {"test": "data"},
            "error": {"code": "test", "message": "test"},
            "meta": {"run_id": "test", "timestamp": "2025-01-01T00:00:00Z", "source": "test", "schema_version": "1.1.0-pr000"}
        }
        
        is_valid, error_code, violations = validate_envelope(invalid2)
        assert not is_valid
        assert error_code == "INVALID_DATA_FIELD"
    
    @given(st.text().filter(lambda x: x not in ["ok", "error"]))
    def test_invalid_status_rejected(self, status):
        """Only 'ok' and 'error' status values are allowed."""
        invalid = {
            "status": status,
            "data": {"test": "data"},
            "error": None,
            "meta": {"run_id": "test", "timestamp": "2025-01-01T00:00:00Z", "source": "test", "schema_version": "1.1.0-pr000"}
        }
        
        is_valid, error_code, violations = validate_envelope(invalid)
        assert not is_valid
        assert error_code == "INVALID_STATUS"
        assert f"Status must be 'ok' or 'error', got '{status}'" in violations[0]
    
    def test_valid_envelopes_pass(self):
        """Valid envelopes should pass validation."""
        # Valid OK envelope
        ok_envelope = _env_ok({"test": "data"})
        is_valid, error_code, violations = validate_envelope(ok_envelope)
        assert is_valid
        assert error_code is None
        assert violations is None
        
        # Valid error envelope
        error_envelope = _env_err("TEST_ERROR", "Test error message")
        is_valid, error_code, violations = validate_envelope(error_envelope)
        assert is_valid
        assert error_code is None
        assert violations is None
    
    def test_missing_required_fields(self):
        """Missing required fields should be rejected."""
        # Missing status
        invalid = {
            "data": {"test": "data"},
            "error": None,
            "meta": {"run_id": "test", "timestamp": "2025-01-01T00:00:00Z", "source": "test", "schema_version": "1.1.0-pr000"}
        }
        
        is_valid, error_code, violations = validate_envelope(invalid)
        assert not is_valid
        assert error_code == "MISSING_STATUS"
        
        # Missing meta
        invalid2 = {
            "status": "ok",
            "data": {"test": "data"},
            "error": None
        }
        
        is_valid, error_code, violations = validate_envelope(invalid2)
        assert not is_valid
        assert error_code == "MISSING_META"
