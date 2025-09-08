"""
Enhanced Narrative Service Tests
Tests for the improved Narrative service with story structures and analysis
"""

import pytest
from fastapi.testclient import TestClient
from services.narrative.main import app, SceneCard, OutlineReq, StoryBeat
from services.narrative.ledger import compute_promise_payoff, trope_budget_ok

client = TestClient(app)

class TestSceneCardValidation:
    """Test SceneCard validation"""
    
    def test_valid_scene_card(self):
        """Test creating a valid scene card"""
        card = SceneCard(
            slug="scene_1",
            where="Harbor of Lumen",
            who=["Elyra", "Captain Rios"],
            goal="Establish the setting and introduce characters",
            when={"time": "morning", "season": "spring"},
            conflict_or_twist="A mysterious fog rolls in",
            value_shift={"hope": -1, "mystery": +1},
            promises_made=["fog origin", "character backstory"],
            promises_paid=["setting established"],
            canon_refs=["p_harbor", "ch_elyra"]
        )
        assert card.slug == "scene_1"
        assert len(card.who) == 2
        assert card.goal == "Establish the setting and introduce characters"
    
    def test_scene_card_empty_who(self):
        """Test scene card with empty who list"""
        with pytest.raises(Exception):  # Pydantic validation error
            SceneCard(
                slug="scene_1",
                where="Harbor of Lumen",
                who=[],  # Empty list
                goal="Test scene"
            )
    
    def test_scene_card_slug_too_long(self):
        """Test scene card with slug too long"""
        with pytest.raises(ValueError):
            SceneCard(
                slug="a" * 101,  # Too long
                where="Harbor of Lumen",
                who=["Elyra"],
                goal="Test scene"
            )
    
    def test_scene_card_goal_too_long(self):
        """Test scene card with goal too long"""
        with pytest.raises(ValueError):
            SceneCard(
                slug="scene_1",
                where="Harbor of Lumen",
                who=["Elyra"],
                goal="a" * 501  # Too long
            )

class TestOutlineRequestValidation:
    """Test OutlineReq validation"""
    
    def test_valid_outline_request(self):
        """Test creating a valid outline request"""
        request = OutlineReq(
            world_id="w_eldershore",
            premise="A young mage discovers her powers in a world where magic is forbidden",
            mode="hero_journey",
            constraints=["no violence", "family-friendly"],
            draft_text="Once upon a time...",
            cards=[]
        )
        assert request.world_id == "w_eldershore"
        assert request.mode == "hero_journey"
        assert len(request.constraints) == 2
    
    def test_invalid_mode(self):
        """Test outline request with invalid mode"""
        with pytest.raises(ValueError, match="Invalid mode"):
            OutlineReq(
                world_id="w_eldershore",
                premise="Test premise",
                mode="invalid_mode"
            )
    
    def test_premise_too_short(self):
        """Test outline request with premise too short"""
        with pytest.raises(ValueError):
            OutlineReq(
                world_id="w_eldershore",
                premise="Short",  # Too short
                mode="hero_journey"
            )
    
    def test_premise_too_long(self):
        """Test outline request with premise too long"""
        with pytest.raises(ValueError):
            OutlineReq(
                world_id="w_eldershore",
                premise="a" * 1001,  # Too long
                mode="hero_journey"
            )

class TestNarrativeAPI:
    """Test Narrative API endpoints"""
    
    def test_health_endpoint(self):
        """Test health endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "ok"
        assert data["data"]["ok"] is True
    
    def test_outline_endpoint_hero_journey(self):
        """Test outline generation with hero journey structure"""
        request_data = {
            "world_id": "w_eldershore",
            "premise": "A young mage discovers her powers in a world where magic is forbidden",
            "mode": "hero_journey",
            "cards": [
                {
                    "slug": "scene_1",
                    "where": "Harbor of Lumen",
                    "who": ["Elyra"],
                    "goal": "Establish the ordinary world",
                    "promises_made": ["fog origin"],
                    "promises_paid": []
                }
            ]
        }
        
        response = client.post("/narrative/outline", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "ok"
        assert "beats" in data["data"]
        assert "issues" in data["data"]
        assert "ledger" in data["data"]
        assert "analysis" in data["data"]
        
        # Check that we have the expected number of beats for hero journey
        assert len(data["data"]["beats"]) == 8
        assert data["data"]["beats"][0]["id"] == "YOU"
        assert data["data"]["beats"][-1]["id"] == "CHANGE"
    
    def test_outline_endpoint_harmon_8(self):
        """Test outline generation with Harmon 8 structure"""
        request_data = {
            "world_id": "w_eldershore",
            "premise": "A detective investigates a series of mysterious disappearances",
            "mode": "harmon_8"
        }
        
        response = client.post("/narrative/outline", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "ok"
        assert len(data["data"]["beats"]) == 8
        assert data["data"]["beats"][0]["id"] == "HOOK"
        assert data["data"]["beats"][-1]["id"] == "RESOLUTION"
    
    def test_outline_endpoint_kishotenketsu(self):
        """Test outline generation with Kishōtenketsu structure"""
        request_data = {
            "world_id": "w_eldershore",
            "premise": "A slice-of-life story about friendship and growth",
            "mode": "kishotenketsu"
        }
        
        response = client.post("/narrative/outline", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "ok"
        assert len(data["data"]["beats"]) == 4
        assert data["data"]["beats"][0]["id"] == "KI"
        assert data["data"]["beats"][-1]["id"] == "KETSU"
    
    def test_outline_endpoint_with_trope_issues(self):
        """Test outline generation with trope budget issues"""
        request_data = {
            "world_id": "w_eldershore",
            "premise": "A young mage discovers her powers",
            "mode": "hero_journey",
            "draft_text": "chosen one " * 20 + "ancient prophecy " * 15  # Over trope limit
        }
        
        response = client.post("/narrative/outline", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "ok"
        
        # Should have trope budget issues
        trope_issues = [issue for issue in data["data"]["issues"] if issue["type"] == "trope_budget"]
        assert len(trope_issues) > 0
        assert trope_issues[0]["severity"] == "error"
    
    def test_outline_endpoint_with_promise_issues(self):
        """Test outline generation with promise/payoff issues"""
        request_data = {
            "world_id": "w_eldershore",
            "premise": "A young mage discovers her powers",
            "mode": "hero_journey",
            "cards": [
                {
                    "slug": "scene_1",
                    "where": "Harbor of Lumen",
                    "who": ["Elyra"],
                    "goal": "Establish the ordinary world",
                    "promises_made": ["fog origin", "character backstory"],
                    "promises_paid": []  # No promises paid
                }
            ]
        }
        
        response = client.post("/narrative/outline", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "ok"
        
        # Should have promise orphan issues
        promise_issues = [issue for issue in data["data"]["issues"] if issue["type"] == "promise_orphans"]
        assert len(promise_issues) > 0
        assert promise_issues[0]["severity"] == "warning"
        assert "fog origin" in promise_issues[0]["items"]
        assert "character backstory" in promise_issues[0]["items"]
    
    def test_get_structures_endpoint(self):
        """Test getting available story structures"""
        response = client.get("/narrative/structures")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "ok"
        assert "structures" in data["data"]
        
        structures = data["data"]["structures"]
        assert "hero_journey" in structures
        assert "harmon_8" in structures
        assert "kishotenketsu" in structures
        
        # Check hero journey structure
        hero_journey = structures["hero_journey"]
        assert len(hero_journey) == 8
        assert hero_journey[0]["id"] == "YOU"
        assert hero_journey[-1]["id"] == "CHANGE"
    
    def test_analyze_story_endpoint(self):
        """Test story analysis endpoint"""
        request_data = {
            "world_id": "w_eldershore",
            "premise": "A young mage discovers her powers",
            "mode": "hero_journey",
            "cards": [
                {
                    "slug": "scene_1",
                    "where": "Harbor of Lumen",
                    "who": ["Elyra"],
                    "goal": "Establish the ordinary world",
                    "promises_made": ["fog origin"],
                    "promises_paid": []
                },
                {
                    "slug": "scene_2",
                    "where": "Forest Path",
                    "who": ["Elyra", "Mentor"],
                    "goal": "Learn about magic",
                    "promises_made": [],
                    "promises_paid": ["fog origin"]
                }
            ]
        }
        
        response = client.post("/narrative/analyze", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "ok"
        assert "analysis" in data["data"]
        assert "recommendations" in data["data"]
        assert "ledger" in data["data"]
        
        analysis = data["data"]["analysis"]
        assert analysis["character_count"] == 2  # Elyra and Mentor
        assert analysis["location_count"] == 2  # Harbor and Forest
        assert analysis["scene_count"] == 2
        assert analysis["promise_balance"] is True  # All promises paid
    
    def test_analyze_story_with_issues(self):
        """Test story analysis with various issues"""
        request_data = {
            "world_id": "w_eldershore",
            "premise": "A young mage discovers her powers",
            "mode": "hero_journey",
            "draft_text": "chosen one " * 20,  # Over trope limit
            "cards": [
                {
                    "slug": "scene_1",
                    "where": "Harbor of Lumen",
                    "who": ["Elyra"],  # Only one character
                    "goal": "Establish the ordinary world",
                    "promises_made": ["fog origin", "character backstory"],
                    "promises_paid": []
                }
            ]
        }
        
        response = client.post("/narrative/analyze", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "ok"
        
        recommendations = data["data"]["recommendations"]
        assert len(recommendations) > 0
        
        # Should have recommendations for promise resolution, trope reduction, and character development
        rec_types = [rec["type"] for rec in recommendations]
        assert "promise_resolution" in rec_types
        assert "trope_reduction" in rec_types
        assert "character_development" in rec_types

class TestStoryStructures:
    """Test story structure functionality"""
    
    def test_hero_journey_structure(self):
        """Test hero journey structure"""
        from services.narrative.main import STORY_STRUCTURES
        
        hero_journey = STORY_STRUCTURES["hero_journey"]
        assert len(hero_journey) == 8
        
        expected_beats = ["YOU", "NEED", "GO", "SEARCH", "FIND", "TAKE", "RETURN", "CHANGE"]
        actual_beats = [beat[0] for beat in hero_journey]
        assert actual_beats == expected_beats
    
    def test_harmon_8_structure(self):
        """Test Harmon 8 structure"""
        from services.narrative.main import STORY_STRUCTURES
        
        harmon_8 = STORY_STRUCTURES["harmon_8"]
        assert len(harmon_8) == 8
        
        expected_beats = ["HOOK", "STAKES", "PLOT_TURN_1", "PINCH_1", "MIDPOINT", "PINCH_2", "PLOT_TURN_2", "RESOLUTION"]
        actual_beats = [beat[0] for beat in harmon_8]
        assert actual_beats == expected_beats
    
    def test_kishotenketsu_structure(self):
        """Test Kishōtenketsu structure"""
        from services.narrative.main import STORY_STRUCTURES
        
        kishotenketsu = STORY_STRUCTURES["kishotenketsu"]
        assert len(kishotenketsu) == 4
        
        expected_beats = ["KI", "SHO", "TEN", "KETSU"]
        actual_beats = [beat[0] for beat in kishotenketsu]
        assert actual_beats == expected_beats

class TestLedgerFunctions:
    """Test ledger computation functions"""
    
    def test_compute_promise_payoff_balanced(self):
        """Test promise/payoff computation with balanced promises"""
        cards = [
            {
                "promises_made": ["fog origin", "character backstory"],
                "promises_paid": ["fog origin", "character backstory"]
            }
        ]
        
        result = compute_promise_payoff(cards)
        assert result["orphans"] == []
        assert result["extraneous"] == []
    
    def test_compute_promise_payoff_orphans(self):
        """Test promise/payoff computation with orphaned promises"""
        cards = [
            {
                "promises_made": ["fog origin", "character backstory"],
                "promises_paid": ["fog origin"]
            }
        ]
        
        result = compute_promise_payoff(cards)
        assert "character backstory" in result["orphans"]
        assert "fog origin" not in result["orphans"]
    
    def test_compute_promise_payoff_extraneous(self):
        """Test promise/payoff computation with extraneous payoffs"""
        cards = [
            {
                "promises_made": ["fog origin"],
                "promises_paid": ["fog origin", "character backstory"]
            }
        ]
        
        result = compute_promise_payoff(cards)
        assert "character backstory" in result["extraneous"]
        assert "fog origin" not in result["extraneous"]
    
    def test_trope_budget_ok_within_limit(self):
        """Test trope budget check within limit"""
        text = "chosen one " * 5  # 5 instances in short text
        ok, counts = trope_budget_ok(text, ["chosen one"], max_per_1k=10)
        assert ok is True
        assert "chosen one" in counts
        assert counts["chosen one"] == 5
    
    def test_trope_budget_ok_over_limit(self):
        """Test trope budget check over limit"""
        text = "chosen one " * 20  # 20 instances in short text
        ok, counts = trope_budget_ok(text, ["chosen one"], max_per_1k=2)
        assert ok is False
        assert "chosen one" in counts
        assert counts["chosen one"] == 20
    
    def test_trope_budget_ok_multiple_tropes(self):
        """Test trope budget check with multiple tropes"""
        text = "chosen one " * 5 + "ancient prophecy " * 3
        ok, counts = trope_budget_ok(text, ["chosen one", "ancient prophecy"], max_per_1k=10)
        assert ok is True
        assert counts["chosen one"] == 5
        assert counts["ancient prophecy"] == 3
    
    def test_trope_budget_ok_case_insensitive(self):
        """Test trope budget check is case insensitive"""
        text = "CHOSEN ONE " * 5 + "chosen one " * 3
        ok, counts = trope_budget_ok(text, ["chosen one"], max_per_1k=10)
        assert ok is True
        assert counts["chosen one"] == 8  # Both cases counted
