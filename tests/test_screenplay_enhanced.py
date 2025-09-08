"""
Enhanced Screenplay Service Tests
Tests for the improved Screenplay service with formatting and export capabilities
"""

import pytest
from fastapi.testclient import TestClient
from services.screenplay.main import (
    app, SceneCard, ExportReq, Scene, 
    generate_fountain_content, generate_fdx_content, 
    generate_html_content, generate_plain_text_content,
    estimate_page_count
)

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
            dialogue=[
                {"character": "Elyra", "text": "What is this fog?"},
                {"character": "Captain Rios", "text": "I've never seen anything like it."}
            ],
            action="Elyra stands at the harbor, watching the mysterious fog approach."
        )
        assert card.slug == "scene_1"
        assert len(card.who) == 2
        assert len(card.dialogue) == 2
    
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

class TestExportRequestValidation:
    """Test ExportReq validation"""
    
    def test_valid_export_request(self):
        """Test creating a valid export request"""
        cards = [
            SceneCard(
                slug="scene_1",
                where="Harbor of Lumen",
                who=["Elyra"],
                goal="Establish the setting"
            )
        ]
        
        request = ExportReq(
            cards=cards,
            format="fountain",
            title="The Harbor Mystery",
            author="Test Author",
            version="1.0"
        )
        assert request.format == "fountain"
        assert request.title == "The Harbor Mystery"
        assert len(request.cards) == 1
    
    def test_invalid_format(self):
        """Test export request with invalid format"""
        cards = [
            SceneCard(
                slug="scene_1",
                where="Harbor of Lumen",
                who=["Elyra"],
                goal="Test scene"
            )
        ]
        
        with pytest.raises(ValueError, match="Invalid format"):
            ExportReq(
                cards=cards,
                format="invalid_format"
            )
    
    def test_empty_cards_list(self):
        """Test export request with empty cards list"""
        with pytest.raises(ValueError):
            ExportReq(
                cards=[],  # Empty list
                format="fountain"
            )
    
    def test_title_too_long(self):
        """Test export request with title too long"""
        cards = [
            SceneCard(
                slug="scene_1",
                where="Harbor of Lumen",
                who=["Elyra"],
                goal="Test scene"
            )
        ]
        
        with pytest.raises(ValueError):
            ExportReq(
                cards=cards,
                format="fountain",
                title="a" * 201  # Too long
            )

class TestScreenplayAPI:
    """Test Screenplay API endpoints"""
    
    def test_health_endpoint(self):
        """Test health endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "ok"
        assert data["data"]["ok"] is True
    
    def test_export_endpoint_fountain(self):
        """Test export endpoint with Fountain format"""
        request_data = {
            "cards": [
                {
                    "slug": "scene_1",
                    "where": "Harbor of Lumen",
                    "who": ["Elyra"],
                    "goal": "Establish the setting",
                    "dialogue": [
                        {"character": "Elyra", "text": "What is this fog?"}
                    ],
                    "action": "Elyra stands at the harbor."
                }
            ],
            "format": "fountain",
            "title": "The Harbor Mystery",
            "author": "Test Author"
        }
        
        response = client.post("/screenplay/export", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "ok"
        assert "artifact" in data["data"]
        
        artifact = data["data"]["artifact"]
        assert artifact["type"] == "fountain"
        assert artifact["title"] == "The Harbor Mystery"
        assert artifact["author"] == "Test Author"
        assert artifact["scene_count"] == 1
    
    def test_export_endpoint_fdx(self):
        """Test export endpoint with FDX format"""
        request_data = {
            "cards": [
                {
                    "slug": "scene_1",
                    "where": "Harbor of Lumen",
                    "who": ["Elyra"],
                    "goal": "Establish the setting"
                }
            ],
            "format": "fdx",
            "title": "The Harbor Mystery"
        }
        
        response = client.post("/screenplay/export", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "ok"
        assert data["data"]["artifact"]["type"] == "fdx"
    
    def test_export_endpoint_html(self):
        """Test export endpoint with HTML format"""
        request_data = {
            "cards": [
                {
                    "slug": "scene_1",
                    "where": "Harbor of Lumen",
                    "who": ["Elyra"],
                    "goal": "Establish the setting"
                }
            ],
            "format": "html",
            "title": "The Harbor Mystery"
        }
        
        response = client.post("/screenplay/export", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "ok"
        assert data["data"]["artifact"]["type"] == "html"
    
    def test_format_scenes_endpoint(self):
        """Test format scenes endpoint"""
        request_data = {
            "cards": [
                {
                    "slug": "scene_1",
                    "where": "Harbor of Lumen",
                    "who": ["Elyra"],
                    "goal": "Establish the setting",
                    "when": {"time": "morning"},
                    "dialogue": [
                        {"character": "Elyra", "text": "What is this fog?"}
                    ],
                    "action": "Elyra stands at the harbor."
                },
                {
                    "slug": "scene_2",
                    "where": "Forest Path",
                    "who": ["Elyra", "Mentor"],
                    "goal": "Learn about magic"
                }
            ],
            "format": "fountain"
        }
        
        response = client.post("/screenplay/format", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "ok"
        assert "scenes" in data["data"]
        assert "total_scenes" in data["data"]
        assert "total_pages" in data["data"]
        
        scenes = data["data"]["scenes"]
        assert len(scenes) == 2
        assert scenes[0]["number"] == 1
        assert scenes[1]["number"] == 2
        assert scenes[0]["heading"] == "INT. HARBOR OF LUMEN - MORNING"
        assert scenes[1]["heading"] == "INT. FOREST PATH - DAY"
    
    def test_get_formats_endpoint(self):
        """Test get formats endpoint"""
        response = client.get("/screenplay/formats")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "ok"
        assert "formats" in data["data"]
        
        formats = data["data"]["formats"]
        assert len(formats) == 4
        
        format_ids = [fmt["id"] for fmt in formats]
        assert "fdx" in format_ids
        assert "fountain" in format_ids
        assert "pdf" in format_ids
        assert "html" in format_ids
        
        # Check Fountain format details
        fountain_format = next(fmt for fmt in formats if fmt["id"] == "fountain")
        assert fountain_format["name"] == "Fountain"
        assert fountain_format["extension"] == ".fountain"

class TestContentGeneration:
    """Test content generation functions"""
    
    def test_generate_fountain_content(self):
        """Test Fountain content generation"""
        cards = [
            SceneCard(
                slug="scene_1",
                where="Harbor of Lumen",
                who=["Elyra"],
                goal="Establish the setting",
                when={"time": "morning"},
                dialogue=[
                    {"character": "Elyra", "text": "What is this fog?"}
                ],
                action="Elyra stands at the harbor."
            )
        ]
        
        request = ExportReq(
            cards=cards,
            format="fountain",
            title="The Harbor Mystery",
            author="Test Author"
        )
        
        content = generate_fountain_content(request)
        
        assert "Title: The Harbor Mystery" in content
        assert "Author: Test Author" in content
        assert "INT. HARBOR OF LUMEN - MORNING" in content
        assert "Elyra stands at the harbor." in content
        assert "ELYRA" in content
        assert "What is this fog?" in content
    
    def test_generate_fdx_content(self):
        """Test FDX content generation"""
        cards = [
            SceneCard(
                slug="scene_1",
                where="Harbor of Lumen",
                who=["Elyra"],
                goal="Establish the setting",
                when={"time": "morning"},
                action="Elyra stands at the harbor."
            )
        ]
        
        request = ExportReq(
            cards=cards,
            format="fdx",
            title="The Harbor Mystery",
            author="Test Author"
        )
        
        content = generate_fdx_content(request)
        
        assert '<?xml version="1.0" encoding="UTF-8"?>' in content
        assert "<FinalDraft DocumentType=\"Script\"" in content
        assert "<Title>The Harbor Mystery</Title>" in content
        assert "<Author>Test Author</Author>" in content
        assert "INT. HARBOR OF LUMEN - MORNING" in content
        assert "Elyra stands at the harbor." in content
    
    def test_generate_html_content(self):
        """Test HTML content generation"""
        cards = [
            SceneCard(
                slug="scene_1",
                where="Harbor of Lumen",
                who=["Elyra"],
                goal="Establish the setting",
                when={"time": "morning"},
                dialogue=[
                    {"character": "Elyra", "text": "What is this fog?"}
                ],
                action="Elyra stands at the harbor."
            )
        ]
        
        request = ExportReq(
            cards=cards,
            format="html",
            title="The Harbor Mystery",
            author="Test Author"
        )
        
        content = generate_html_content(request)
        
        assert "<!DOCTYPE html>" in content
        assert "<title>The Harbor Mystery</title>" in content
        assert "The Harbor Mystery" in content
        assert "By Test Author" in content
        assert "INT. HARBOR OF LUMEN - MORNING" in content
        assert "Elyra stands at the harbor." in content
        assert "ELYRA" in content
        assert "What is this fog?" in content
    
    def test_generate_plain_text_content(self):
        """Test plain text content generation"""
        cards = [
            SceneCard(
                slug="scene_1",
                where="Harbor of Lumen",
                who=["Elyra"],
                goal="Establish the setting",
                when={"time": "morning"},
                dialogue=[
                    {"character": "Elyra", "text": "What is this fog?"}
                ],
                action="Elyra stands at the harbor."
            )
        ]
        
        request = ExportReq(
            cards=cards,
            format="plain",
            title="The Harbor Mystery",
            author="Test Author"
        )
        
        content = generate_plain_text_content(request)
        
        assert "TITLE: The Harbor Mystery" in content
        assert "AUTHOR: Test Author" in content
        assert "SCENE 1" in content
        assert "INT. HARBOR OF LUMEN - MORNING" in content
        assert "Elyra stands at the harbor." in content
        assert "ELYRA: What is this fog?" in content
    
    def test_generate_content_without_title_author(self):
        """Test content generation without title and author"""
        cards = [
            SceneCard(
                slug="scene_1",
                where="Harbor of Lumen",
                who=["Elyra"],
                goal="Establish the setting"
            )
        ]
        
        request = ExportReq(
            cards=cards,
            format="fountain"
        )
        
        content = generate_fountain_content(request)
        
        # Should not include title/author lines
        assert "Title:" not in content
        assert "Author:" not in content
        assert "INT. HARBOR OF LUMEN - DAY" in content
    
    def test_generate_content_with_conflict_twist(self):
        """Test content generation with conflict/twist"""
        cards = [
            SceneCard(
                slug="scene_1",
                where="Harbor of Lumen",
                who=["Elyra"],
                goal="Establish the setting",
                conflict_or_twist="A mysterious fog rolls in from the sea."
            )
        ]
        
        request = ExportReq(
            cards=cards,
            format="fountain"
        )
        
        content = generate_fountain_content(request)
        
        assert "A mysterious fog rolls in from the sea." in content
    
    def test_generate_content_without_action(self):
        """Test content generation without explicit action"""
        cards = [
            SceneCard(
                slug="scene_1",
                where="Harbor of Lumen",
                who=["Elyra"],
                goal="Establish the setting"
            )
        ]
        
        request = ExportReq(
            cards=cards,
            format="fountain"
        )
        
        content = generate_fountain_content(request)
        
        # Should generate action from goal
        assert "Elyra establish the setting." in content

class TestPageEstimation:
    """Test page count estimation"""
    
    def test_estimate_page_count_single_scene(self):
        """Test page count estimation for single scene"""
        scenes = [
            Scene(
                number=1,
                heading="INT. HARBOR - DAY",
                action="Elyra stands at the harbor.",
                characters=["Elyra"],
                dialogue=[]
            )
        ]
        
        pages = estimate_page_count(scenes)
        assert pages == 2  # 1 scene * 2 pages per scene
    
    def test_estimate_page_count_multiple_scenes(self):
        """Test page count estimation for multiple scenes"""
        scenes = [
            Scene(
                number=1,
                heading="INT. HARBOR - DAY",
                action="Elyra stands at the harbor.",
                characters=["Elyra"],
                dialogue=[]
            ),
            Scene(
                number=2,
                heading="INT. FOREST - DAY",
                action="Elyra walks through the forest.",
                characters=["Elyra"],
                dialogue=[]
            ),
            Scene(
                number=3,
                heading="INT. CAVE - DAY",
                action="Elyra discovers the cave.",
                characters=["Elyra"],
                dialogue=[]
            )
        ]
        
        pages = estimate_page_count(scenes)
        assert pages == 6  # 3 scenes * 2 pages per scene
    
    def test_estimate_page_count_minimum_one(self):
        """Test page count estimation minimum of 1"""
        scenes = []
        
        pages = estimate_page_count(scenes)
        assert pages == 1  # Minimum of 1 page

class TestSceneFormatting:
    """Test scene formatting functionality"""
    
    def test_scene_heading_generation(self):
        """Test scene heading generation"""
        card = SceneCard(
            slug="scene_1",
            where="Harbor of Lumen",
            who=["Elyra"],
            goal="Establish the setting",
            when={"time": "morning"}
        )
        
        # Test the heading format
        heading = f"INT. {card.where.upper()} - {card.when.get('time', 'DAY') if card.when else 'DAY'}"
        assert heading == "INT. HARBOR OF LUMEN - MORNING"
    
    def test_scene_heading_default_time(self):
        """Test scene heading with default time"""
        card = SceneCard(
            slug="scene_1",
            where="Harbor of Lumen",
            who=["Elyra"],
            goal="Establish the setting"
        )
        
        # Test the heading format with default time
        heading = f"INT. {card.where.upper()} - {card.when.get('time', 'DAY') if card.when else 'DAY'}"
        assert heading == "INT. HARBOR OF LUMEN - DAY"
    
    def test_dialogue_formatting(self):
        """Test dialogue formatting"""
        dialogue = [
            {"character": "Elyra", "text": "What is this fog?"},
            {"character": "Captain Rios", "text": "I've never seen anything like it."}
        ]
        
        formatted_dialogue = []
        for line in dialogue:
            character = line.get('character', 'UNKNOWN')
            text = line.get('text', '')
            formatted_dialogue.append({
                "character": character.upper(),
                "text": text
            })
        
        assert formatted_dialogue[0]["character"] == "ELYRA"
        assert formatted_dialogue[0]["text"] == "What is this fog?"
        assert formatted_dialogue[1]["character"] == "CAPTAIN RIOS"
        assert formatted_dialogue[1]["text"] == "I've never seen anything like it."
