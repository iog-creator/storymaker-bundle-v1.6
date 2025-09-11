
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any
from services.common.envelope import envelope_ok, envelope_error
import os
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

app = FastAPI(title="StoryMaker Screenplay", version="1.6.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Supported export formats
SUPPORTED_FORMATS = ["fdx", "fountain", "pdf", "html"]

class SceneCard(BaseModel):
    slug: str = Field(..., min_length=1, max_length=100, description="Scene identifier")
    where: str = Field(..., min_length=1, max_length=200, description="Scene location")
    who: List[str] = Field(..., min_length=1, description="Characters in scene")
    goal: str = Field(..., min_length=1, max_length=500, description="Scene objective")
    when: Optional[Dict[str, str]] = Field(None, description="Temporal information")
    conflict_or_twist: Optional[str] = Field(None, max_length=500, description="Conflict or plot twist")
    value_shift: Dict[str, Any] = Field(default_factory=dict, description="Value changes in scene")
    dialogue: Optional[List[Dict[str, str]]] = Field(None, description="Scene dialogue")
    action: Optional[str] = Field(None, description="Scene action/description")
    
    @field_validator('who')
    @classmethod
    def validate_who(cls, v):
        if not v:
            raise ValueError("At least one character must be specified")
        return v

class ExportReq(BaseModel):
    cards: List[SceneCard] = Field(..., min_length=1, description="Scene cards to export")
    format: str = Field(..., description="Export format")
    title: Optional[str] = Field(None, max_length=200, description="Screenplay title")
    author: Optional[str] = Field(None, max_length=200, description="Author name")
    version: Optional[str] = Field("1.0", description="Version number")
    
    @field_validator('format')
    @classmethod
    def validate_format(cls, v):
        if v not in SUPPORTED_FORMATS:
            raise ValueError(f"Invalid format. Must be one of: {', '.join(SUPPORTED_FORMATS)}")
        return v

class Scene(BaseModel):
    number: int
    heading: str
    action: str
    characters: List[str]
    dialogue: List[Dict[str, str]]

@app.get("/health")
def health():
    """Health check endpoint"""
    return envelope_ok({"ok": True}, {"actor": "api"})

@app.post("/screenplay/export")
def export(req: ExportReq):
    """Export screenplay in specified format"""
    try:
        # Generate screenplay content
        screenplay_content = generate_screenplay_content(req)
        
        # Create artifact metadata
        artifact = {
            "type": req.format,
            "uri": f"asset://screenplays/{req.title or 'untitled'}/script.{req.format}",
            "size_bytes": len(screenplay_content.encode('utf-8')),
            "created_at": datetime.now().isoformat(),
            "title": req.title or "Untitled Screenplay",
            "author": req.author or "Unknown",
            "version": req.version,
            "scene_count": len(req.cards)
        }
        
        # Store content (in real implementation, this would save to MinIO)
        # For now, we'll just return the metadata
        
        return envelope_ok({"artifact": artifact}, {"actor": "ai"})
        
    except Exception as e:
        logger.error(f"Failed to export screenplay: {e}")
        return envelope_error("EXPORT_FAILED", "Failed to export screenplay", 
                            {"detail": str(e)}, {"actor": "ai"})

@app.post("/screenplay/format")
def format_scenes(req: ExportReq):
    """Format scene cards into screenplay format"""
    try:
        formatted_scenes = []
        
        for i, card in enumerate(req.cards, 1):
            # Generate scene heading
            heading = f"INT. {card.where.upper()} - {card.when.get('time', 'DAY') if card.when else 'DAY'}"
            
            # Generate action lines
            action_lines = []
            if card.action:
                action_lines.append(card.action)
            else:
                action_lines.append(f"{', '.join(card.who)} {card.goal.lower()}.")
            
            if card.conflict_or_twist:
                action_lines.append(card.conflict_or_twist)
            
            # Format dialogue
            dialogue_lines = []
            if card.dialogue:
                for line in card.dialogue:
                    character = line.get('character', 'UNKNOWN')
                    text = line.get('text', '')
                    dialogue_lines.append({
                        "character": character.upper(),
                        "text": text
                    })
            
            formatted_scenes.append(Scene(
                number=i,
                heading=heading,
                action="\n".join(action_lines),
                characters=card.who,
                dialogue=dialogue_lines
            ))
        
        return envelope_ok({
            "scenes": [scene.model_dump() for scene in formatted_scenes],
            "total_scenes": len(formatted_scenes),
            "total_pages": estimate_page_count(formatted_scenes)
        }, {"actor": "ai"})
        
    except Exception as e:
        logger.error(f"Failed to format scenes: {e}")
        return envelope_error("FORMAT_FAILED", "Failed to format scenes", 
                            {"detail": str(e)}, {"actor": "ai"})

@app.get("/screenplay/formats")
def get_formats():
    """Get supported export formats"""
    return envelope_ok({
        "formats": [
            {
                "id": "fdx",
                "name": "Final Draft",
                "description": "Final Draft XML format",
                "extension": ".fdx"
            },
            {
                "id": "fountain",
                "name": "Fountain",
                "description": "Fountain markup format",
                "extension": ".fountain"
            },
            {
                "id": "pdf",
                "name": "PDF",
                "description": "Portable Document Format",
                "extension": ".pdf"
            },
            {
                "id": "html",
                "name": "HTML",
                "description": "Web format with styling",
                "extension": ".html"
            }
        ]
    }, {"actor": "api"})

def generate_screenplay_content(req: ExportReq) -> str:
    """Generate screenplay content in the requested format"""
    if req.format == "fountain":
        return generate_fountain_content(req)
    elif req.format == "fdx":
        return generate_fdx_content(req)
    elif req.format == "html":
        return generate_html_content(req)
    else:
        return generate_plain_text_content(req)

def generate_fountain_content(req: ExportReq) -> str:
    """Generate Fountain format content"""
    content = []
    
    # Title page
    if req.title:
        content.append(f"Title: {req.title}")
    if req.author:
        content.append(f"Author: {req.author}")
    content.append("")
    
    # Scenes
    for i, card in enumerate(req.cards, 1):
        # Scene heading
        heading = f"INT. {card.where.upper()} - {card.when.get('time', 'DAY') if card.when else 'DAY'}"
        content.append(heading)
        content.append("")
        
        # Action
        if card.action:
            content.append(card.action)
        else:
            content.append(f"{', '.join(card.who)} {card.goal.lower()}.")
        
        if card.conflict_or_twist:
            content.append(card.conflict_or_twist)
        
        content.append("")
        
        # Dialogue
        if card.dialogue:
            for line in card.dialogue:
                character = line.get('character', 'UNKNOWN')
                text = line.get('text', '')
                content.append(f"{character.upper()}")
                content.append(text)
                content.append("")
    
    return "\n".join(content)

def generate_fdx_content(req: ExportReq) -> str:
    """Generate Final Draft XML content"""
    # Simplified FDX structure
    content = f"""<?xml version="1.0" encoding="UTF-8"?>
<FinalDraft DocumentType="Script" Template="No" Version="1">
    <Content>
        <TitlePage>
            <Title>{req.title or 'Untitled'}</Title>
            <Author>{req.author or 'Unknown'}</Author>
        </TitlePage>
"""
    
    for i, card in enumerate(req.cards, 1):
        content += f"""        <Paragraph Type="Scene Heading">
            <Text>INT. {card.where.upper()} - {card.when.get('time', 'DAY') if card.when else 'DAY'}</Text>
        </Paragraph>
        <Paragraph Type="Action">
            <Text>{card.action or f"{', '.join(card.who)} {card.goal.lower()}."}</Text>
        </Paragraph>
"""
        
        if card.dialogue:
            for line in card.dialogue:
                character = line.get('character', 'UNKNOWN')
                text = line.get('text', '')
                content += f"""        <Paragraph Type="Character">
            <Text>{character.upper()}</Text>
        </Paragraph>
        <Paragraph Type="Dialogue">
            <Text>{text}</Text>
        </Paragraph>
"""
    
    content += """    </Content>
</FinalDraft>"""
    return content

def generate_html_content(req: ExportReq) -> str:
    """Generate HTML format content"""
    content = f"""<!DOCTYPE html>
<html>
<head>
    <title>{req.title or 'Untitled Screenplay'}</title>
    <style>
        body {{ font-family: 'Courier New', monospace; margin: 40px; }}
        .scene-heading {{ text-transform: uppercase; font-weight: bold; margin-top: 20px; }}
        .action {{ margin: 10px 0; }}
        .character {{ text-transform: uppercase; font-weight: bold; margin-left: 40px; }}
        .dialogue {{ margin-left: 60px; margin-bottom: 10px; }}
    </style>
</head>
<body>
    <h1>{req.title or 'Untitled Screenplay'}</h1>
    <p>By {req.author or 'Unknown'}</p>
    <hr>
"""
    
    for i, card in enumerate(req.cards, 1):
        content += f"""    <div class="scene-heading">INT. {card.where.upper()} - {card.when.get('time', 'DAY') if card.when else 'DAY'}</div>
    <div class="action">{card.action or f"{', '.join(card.who)} {card.goal.lower()}."}</div>
"""
        
        if card.dialogue:
            for line in card.dialogue:
                character = line.get('character', 'UNKNOWN')
                text = line.get('text', '')
                content += f"""    <div class="character">{character.upper()}</div>
    <div class="dialogue">{text}</div>
"""
    
    content += """</body>
</html>"""
    return content

def generate_plain_text_content(req: ExportReq) -> str:
    """Generate plain text content"""
    content = []
    
    if req.title:
        content.append(f"TITLE: {req.title}")
    if req.author:
        content.append(f"AUTHOR: {req.author}")
    content.append("")
    
    for i, card in enumerate(req.cards, 1):
        content.append(f"SCENE {i}")
        content.append(f"INT. {card.where.upper()} - {card.when.get('time', 'DAY') if card.when else 'DAY'}")
        content.append("")
        content.append(card.action or f"{', '.join(card.who)} {card.goal.lower()}.")
        content.append("")
        
        if card.dialogue:
            for line in card.dialogue:
                character = line.get('character', 'UNKNOWN')
                text = line.get('text', '')
                content.append(f"{character.upper()}: {text}")
            content.append("")
    
    return "\n".join(content)

def estimate_page_count(scenes: List[Scene]) -> int:
    """Estimate page count (roughly 1 page per minute of screen time)"""
    # Simple estimation: 1 scene ≈ 2-3 minutes ≈ 2-3 pages
    return max(1, len(scenes) * 2)
