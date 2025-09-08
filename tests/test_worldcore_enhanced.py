"""
Enhanced WorldCore Service Tests
Tests for the improved WorldCore service with validation, error handling, and guards
"""

import pytest
import json
from unittest.mock import Mock, patch
from services.worldcore.main import app, Entity, ApproveReq
from services.worldcore.dal import WorldCoreDAL
from services.guards.allen_lite import validate_entity_consistency
from fastapi.testclient import TestClient

client = TestClient(app)

class TestEntityValidation:
    """Test entity validation and constraints"""
    
    def test_valid_entity_creation(self):
        """Test creating a valid entity"""
        entity = Entity(
            id="test_character",
            type="Character",
            name="Test Character",
            status="DRAFT",
            traits={"age": 25, "description": "A test character"},
            world_id="test_world"
        )
        assert entity.id == "test_character"
        assert entity.type == "Character"
        assert entity.status == "DRAFT"
    
    def test_invalid_entity_type(self):
        """Test validation of invalid entity type"""
        with pytest.raises(ValueError, match="Invalid entity type"):
            Entity(
                id="test_entity",
                type="InvalidType",
                name="Test Entity",
                status="DRAFT",
                traits={}
            )
    
    def test_invalid_entity_status(self):
        """Test validation of invalid entity status"""
        with pytest.raises(ValueError, match="Invalid status"):
            Entity(
                id="test_entity",
                type="Character",
                name="Test Entity",
                status="INVALID",
                traits={}
            )
    
    def test_invalid_entity_id_format(self):
        """Test validation of invalid entity ID format"""
        with pytest.raises(ValueError, match="ID must start with letter"):
            Entity(
                id="123invalid",
                type="Character",
                name="Test Entity",
                status="DRAFT",
                traits={}
            )
    
    def test_entity_id_too_long(self):
        """Test validation of entity ID length"""
        with pytest.raises(ValueError):
            Entity(
                id="a" * 101,  # Too long
                type="Character",
                name="Test Entity",
                status="DRAFT",
                traits={}
            )
    
    def test_entity_name_too_long(self):
        """Test validation of entity name length"""
        with pytest.raises(ValueError):
            Entity(
                id="test_entity",
                type="Character",
                name="a" * 201,  # Too long
                status="DRAFT",
                traits={}
            )

class TestAllenLiteGuard:
    """Test Allen Lite guard validation"""
    
    def test_character_validation_with_age(self):
        """Test character validation with age trait"""
        entity = {
            "id": "test_char",
            "type": "Character",
            "name": "Test Character",
            "traits": {"age": 25}
        }
        issues = validate_entity_consistency(entity)
        assert len(issues) == 0
    
    def test_character_validation_without_age_or_description(self):
        """Test character validation without required traits"""
        entity = {
            "id": "test_char",
            "type": "Character",
            "name": "Test Character",
            "traits": {}
        }
        issues = validate_entity_consistency(entity)
        assert len(issues) > 0
        assert any("age or description" in issue for issue in issues)
    
    def test_place_validation_with_location(self):
        """Test place validation with location trait"""
        entity = {
            "id": "test_place",
            "type": "Place",
            "name": "Test Place",
            "traits": {"location": "Test City"}
        }
        issues = validate_entity_consistency(entity)
        assert len(issues) == 0
    
    def test_place_validation_without_location(self):
        """Test place validation without location trait"""
        entity = {
            "id": "test_place",
            "type": "Place",
            "name": "Test Place",
            "traits": {}
        }
        issues = validate_entity_consistency(entity)
        assert len(issues) > 0
        assert any("location or coordinates" in issue for issue in issues)
    
    def test_event_validation_with_date(self):
        """Test event validation with date trait"""
        entity = {
            "id": "test_event",
            "type": "Event",
            "name": "Test Event",
            "traits": {"date": "2024-01-01"}
        }
        issues = validate_entity_consistency(entity)
        assert len(issues) == 0
    
    def test_event_validation_without_date(self):
        """Test event validation without date trait"""
        entity = {
            "id": "test_event",
            "type": "Event",
            "name": "Test Event",
            "traits": {}
        }
        issues = validate_entity_consistency(entity)
        assert len(issues) > 0
        assert any("date or timeframe" in issue for issue in issues)
    
    def test_invalid_world_id_format(self):
        """Test validation of invalid world_id format"""
        entity = {
            "id": "test_entity",
            "type": "Character",
            "name": "Test Entity",
            "world_id": "123invalid"
        }
        issues = validate_entity_consistency(entity)
        assert len(issues) > 0
        assert any("Invalid world_id format" in issue for issue in issues)

class TestWorldCoreAPI:
    """Test WorldCore API endpoints"""
    
    @patch('services.worldcore.main.dal')
    def test_health_endpoint_success(self, mock_dal):
        """Test health endpoint when DB is available"""
        mock_dal.graph.return_value = {"nodes": [], "edges": []}
        
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "ok"
        assert data["data"]["ok"] is True
    
    @patch('services.worldcore.main.dal')
    def test_health_endpoint_db_unavailable(self, mock_dal):
        """Test health endpoint when DB is unavailable"""
        mock_dal.graph.side_effect = Exception("Connection failed")
        
        response = client.get("/health")
        assert response.status_code == 200  # Still returns 200 with error envelope
        
        data = response.json()
        assert data["status"] == "error"
        assert data["error"]["code"] == "DB_UNAVAILABLE"
    
    @patch('services.worldcore.main.dal')
    def test_propose_endpoint_success(self, mock_dal):
        """Test successful proposal creation"""
        mock_dal.propose.return_value = "b3:12345678...123456"
        
        entity_data = {
            "id": "test_character",
            "type": "Character",
            "name": "Test Character",
            "status": "DRAFT",
            "traits": {"age": 25},
            "world_id": "test_world"
        }
        
        response = client.post("/propose", json=entity_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "ok"
        assert "cid" in data["data"]
        assert data["data"]["id"] == "test_character"
    
    @patch('services.worldcore.main.dal')
    def test_propose_endpoint_validation_failure(self, mock_dal):
        """Test proposal with validation failure"""
        entity_data = {
            "id": "test_character",
            "type": "Character",
            "name": "Test Character",
            "status": "DRAFT",
            "traits": {},  # Missing required traits for Character
            "world_id": "test_world"
        }
        
        response = client.post("/propose", json=entity_data)
        assert response.status_code == 200  # Returns 200 with error envelope
        
        data = response.json()
        assert data["status"] == "error"
        assert data["error"]["code"] == "VALIDATION_FAILED"
    
    @patch('services.worldcore.main.dal')
    def test_approve_endpoint_success(self, mock_dal):
        """Test successful approval"""
        mock_dal.approve.return_value = {"id": "test_character", "version": 1}
        
        approve_data = {"cid": "b3:12345678...123456"}
        
        response = client.post("/approve", json=approve_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "ok"
        assert data["data"]["canon_pointer"]["id"] == "test_character"
    
    @patch('services.worldcore.main.dal')
    def test_approve_endpoint_nothing_to_approve(self, mock_dal):
        """Test approval when nothing to approve"""
        mock_dal.approve.return_value = {"id": None, "version": 0}
        
        approve_data = {"cid": "invalid_cid"}
        
        response = client.post("/approve", json=approve_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "error"
        assert data["error"]["code"] == "NOTHING_TO_APPROVE"
    
    @patch('services.worldcore.main.dal')
    def test_get_canon_success(self, mock_dal):
        """Test successful canon retrieval"""
        mock_entity = {
            "entity": {
                "id": "test_character",
                "type": "Character",
                "name": "Test Character",
                "status": "CANON",
                "traits": {"age": 25},
                "world_id": "test_world"
            },
            "canon_version": 1
        }
        mock_dal.get_canon.return_value = mock_entity
        
        response = client.get("/canon/entity/test_character")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "ok"
        assert data["data"]["entity"]["id"] == "test_character"
    
    def test_get_canon_invalid_id_format(self):
        """Test canon retrieval with invalid ID format"""
        response = client.get("/canon/entity/123invalid")
        assert response.status_code == 400
    
    @patch('services.worldcore.main.dal')
    def test_get_canon_not_found(self, mock_dal):
        """Test canon retrieval when entity not found"""
        mock_dal.get_canon.return_value = None
        
        response = client.get("/canon/entity/nonexistent")
        assert response.status_code == 404
    
    @patch('services.worldcore.main.dal')
    def test_graph_endpoint_success(self, mock_dal):
        """Test successful graph retrieval"""
        mock_graph = {
            "nodes": [
                {"id": "test_character", "type": "Character", "label": "Test Character", "status": "CANON"}
            ],
            "edges": [],
            "total_nodes": 1,
            "total_edges": 0
        }
        mock_dal.graph.return_value = mock_graph
        
        response = client.get("/graph")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "ok"
        assert len(data["data"]["nodes"]) == 1
    
    @patch('services.worldcore.main.dal')
    def test_graph_endpoint_with_filters(self, mock_dal):
        """Test graph retrieval with filters"""
        mock_graph = {"nodes": [], "edges": [], "total_nodes": 0, "total_edges": 0}
        mock_dal.graph.return_value = mock_graph
        
        response = client.get("/graph?world_id=test_world&q=character")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "ok"
    
    @patch('services.worldcore.main.dal')
    def test_proposals_endpoint_success(self, mock_dal):
        """Test successful proposals retrieval"""
        mock_proposals = [
            {
                "cid": "b3:12345678...123456",
                "entity": {"id": "test_character", "type": "Character"},
                "created_at": "2024-01-01T00:00:00Z"
            }
        ]
        mock_dal.get_proposals.return_value = mock_proposals
        
        response = client.get("/proposals")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "ok"
        assert len(data["data"]["proposals"]) == 1
    
    def test_proposals_endpoint_limit_cap(self):
        """Test proposals endpoint with limit cap"""
        response = client.get("/proposals?limit=2000")  # Over the 1000 cap
        assert response.status_code == 200
        
        # The limit should be capped to 1000 internally

class TestWorldCoreDAL:
    """Test WorldCore Data Access Layer"""
    
    def test_dal_initialization_with_dsn(self):
        """Test DAL initialization with DSN"""
        dal = WorldCoreDAL("postgresql://test:test@localhost:5432/test")
        assert dal.dsn == "postgresql://test:test@localhost:5432/test"
    
    def test_dal_initialization_without_dsn(self):
        """Test DAL initialization without DSN"""
        with patch.dict('os.environ', {'POSTGRES_DSN': 'postgresql://env:env@localhost:5432/env'}):
            dal = WorldCoreDAL()
            assert dal.dsn == "postgresql://env:env@localhost:5432/env"
    
    def test_dal_initialization_no_dsn_available(self):
        """Test DAL initialization when no DSN is available"""
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(RuntimeError, match="POSTGRES_DSN is required"):
                WorldCoreDAL()
    
    @patch('psycopg.connect')
    def test_propose_success(self, mock_connect):
        """Test successful proposal creation"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connect.return_value.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None  # No existing proposal
        
        dal = WorldCoreDAL("postgresql://test:test@localhost:5432/test")
        entity = {"id": "test_character", "type": "Character", "name": "Test Character"}
        
        result = dal.propose(entity, "test_cid")
        
        assert result == "test_cid"
        mock_cursor.execute.assert_called()
        mock_conn.commit.assert_called()
    
    @patch('psycopg.connect')
    def test_propose_existing_proposal(self, mock_connect):
        """Test proposal creation when proposal already exists"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connect.return_value.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.fetchone.return_value = ("test_cid",)  # Existing proposal
        
        dal = WorldCoreDAL("postgresql://test:test@localhost:5432/test")
        entity = {"id": "test_character", "type": "Character", "name": "Test Character"}
        
        result = dal.propose(entity, "test_cid")
        
        assert result == "test_cid"
        # Should not insert again
    
    @patch('psycopg.connect')
    def test_approve_success(self, mock_connect):
        """Test successful approval"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connect.return_value.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        
        # Mock proposal exists
        mock_cursor.fetchone.side_effect = [
            ({"id": "test_character", "type": "Character", "name": "Test Character"},),  # Proposal
            (1,)  # Version
        ]
        
        dal = WorldCoreDAL("postgresql://test:test@localhost:5432/test")
        
        result = dal.approve("test_cid")
        
        assert result["id"] == "test_character"
        assert result["version"] == 1
        mock_conn.commit.assert_called()
    
    @patch('psycopg.connect')
    def test_approve_already_approved(self, mock_connect):
        """Test approval when already approved"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connect.return_value.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        
        # Mock no proposal, but entity exists
        mock_cursor.fetchone.side_effect = [
            None,  # No proposal
            ("test_character", 2)  # Already approved entity
        ]
        
        dal = WorldCoreDAL("postgresql://test:test@localhost:5432/test")
        
        result = dal.approve("test_cid")
        
        assert result["id"] == "test_character"
        assert result["version"] == 2
    
    @patch('psycopg.connect')
    def test_get_canon_success(self, mock_connect):
        """Test successful canon retrieval"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connect.return_value.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        
        mock_cursor.fetchone.return_value = (
            "test_character", "test_cid", "Character", "Test Character", 
            "CANON", {"age": 25}, "test_world", 1, "2024-01-01T00:00:00Z", "2024-01-01T00:00:00Z"
        )
        
        dal = WorldCoreDAL("postgresql://test:test@localhost:5432/test")
        
        result = dal.get_canon("test_character")
        
        assert result is not None
        assert result["entity"]["id"] == "test_character"
        assert result["canon_version"] == 1
    
    @patch('psycopg.connect')
    def test_get_canon_not_found(self, mock_connect):
        """Test canon retrieval when entity not found"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connect.return_value.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        
        mock_cursor.fetchone.return_value = None
        
        dal = WorldCoreDAL("postgresql://test:test@localhost:5432/test")
        
        result = dal.get_canon("nonexistent")
        
        assert result is None
    
    @patch('psycopg.connect')
    def test_graph_success(self, mock_connect):
        """Test successful graph retrieval"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connect.return_value.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        
        mock_cursor.fetchall.return_value = [
            ("test_character", "Character", "Test Character", "CANON", "test_world")
        ]
        
        dal = WorldCoreDAL("postgresql://test:test@localhost:5432/test")
        
        result = dal.graph()
        
        assert "nodes" in result
        assert "edges" in result
        assert len(result["nodes"]) == 1
        assert result["nodes"][0]["id"] == "test_character"
    
    @patch('psycopg.connect')
    def test_get_proposals_success(self, mock_connect):
        """Test successful proposals retrieval"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connect.return_value.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        
        mock_cursor.fetchall.return_value = [
            ("test_cid", {"id": "test_character", "type": "Character"}, "2024-01-01T00:00:00Z")
        ]
        
        dal = WorldCoreDAL("postgresql://test:test@localhost:5432/test")
        
        result = dal.get_proposals()
        
        assert len(result) == 1
        assert result[0]["cid"] == "test_cid"
        assert result[0]["entity"]["id"] == "test_character"
