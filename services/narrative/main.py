
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any
from services.common.envelope import envelope_ok, envelope_error
from services.narrative.ledger import compute_promise_payoff, trope_budget_ok
from services.narrative.api import router as narrative_router
import os
import json
import logging
import subprocess
import sys
import pathlib
from datetime import datetime

logger = logging.getLogger(__name__)

def create_app() -> FastAPI:
    app = FastAPI(title="StoryMaker Narrative", version="1.6.0")
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    def health():
        return {"status": "ok", "data": {"ok": True}}

    @app.get("/health/ready")
    def ready():
        from services.narrative.providers.groq_client import GroqError, get_config
        meta = {"checks": {}}
        try:
            cfg = get_config()
            meta["checks"]["groq_env"] = {"ok": True, "model": cfg.model}
            return {"status": "ok", "data": {"ready": True}, "meta": meta}
        except GroqError as e:
            meta["checks"]["groq_env"] = {"ok": False, "error": str(e)}
            return {"status": "error", "error": "groq_misconfig", "meta": meta}

    app.include_router(narrative_router)
    return app

app = create_app()

# LM Studio integration
def lm_studio_chat(prompt: str, system_msg: str = "", model: str = "", max_tokens: int = 500, temperature: float = 0.7) -> str:
    """Call LM Studio for chat completion"""
    try:
        lm_api = pathlib.Path(__file__).parent.parent.parent / "scripts" / "lm_api.py"
        cmd = [sys.executable, str(lm_api), "chat", "--prompt", prompt]

        if system_msg:
            cmd.extend(["--system", system_msg])
        if model:
            cmd.extend(["--model", model])
        cmd.extend(["--max-tokens", str(max_tokens), "--temperature", str(temperature)])

        result = subprocess.run(cmd, capture_output=True, text=True, cwd=pathlib.Path(__file__).parent.parent.parent)

        if result.returncode == 0:
            try:
                response = json.loads(result.stdout.strip())
                logger.info(f"LM Studio response status: {response.get('status')}")
                if response.get("status") == "success":
                    content = response.get("data", {}).get("content", "").strip()
                    logger.info(f"LM Studio content length: {len(content)}")
                    return content
                else:
                    logger.error(f"LM Studio API error: {response.get('error', {}).get('message', 'Unknown error')}")
                    return ""
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse LM Studio response: {e}")
                logger.error(f"Raw output: {repr(result.stdout)}")
                return ""
        else:
            logger.error(f"LM Studio call failed with exit code {result.returncode}")
            logger.error(f"Stderr: {result.stderr}")
            return ""
    except Exception as e:
        logger.error(f"Error calling LM Studio: {e}")
        return ""

def generate_story_beat_description(beat_id: str, beat_note: str, premise: str, context: str = "") -> str:
    """Generate detailed description for a story beat using Groq"""
    try:
        # Import Groq client lazily
        from services.narrative.scribe.hf_client import generate as hf_generate
        result = hf_generate("outline", {
            "premise": premise,
            "beat_id": beat_id,
            "beat_note": beat_note,
            "context": context
        })
        return result.get("draft", f"Beat: {beat_note}")
    except Exception as e:
        logger.error(f"Groq generation failed: {e}")
        return f"Beat: {beat_note}"

def generate_plot_idea(premise: str, genre: str = "fantasy", constraints: List[str] = None) -> str:
    """Generate a plot idea based on premise and constraints using Groq"""
    try:
        from services.narrative.scribe.hf_client import generate as hf_generate
        constraint_text = f"\nConstraints: {', '.join(constraints)}" if constraints else ""
        result = hf_generate("outline", {
            "premise": premise,
            "genre": genre,
            "constraints": constraint_text
        })
        return result.get("draft", f"Plot idea for {premise}")
    except Exception as e:
        logger.error(f"Groq generation failed: {e}")
        return f"Plot idea for {premise}"

def generate_character_profile(name: str, role: str, world_context: str) -> Dict[str, Any]:
    """Generate character profile using Groq"""
    try:
        from services.narrative.scribe.hf_client import generate as hf_generate
        result = hf_generate("character_bible", {
            "name": name,
            "role": role,
            "world_context": world_context
        })
        content = result.get("draft", f"Character profile for {name}")
        return {
            "name": name,
            "role": role,
            "description": content,
            "traits": ["determined", "mysterious", "brave"],  # Could parse from AI response
            "relationships": []
        }
    except Exception as e:
        logger.error(f"Groq generation failed: {e}")
        return {
            "name": name,
            "role": role,
            "description": f"Character profile for {name}",
            "traits": ["determined", "mysterious", "brave"],
            "relationships": []
        }

def generate_dialogue(scene_context: str, characters: List[str], tone: str = "natural") -> str:
    """Generate dialogue for a scene using Groq"""
    try:
        from services.narrative.scribe.hf_client import generate as hf_generate
        result = hf_generate("scene", {
            "scene_context": scene_context,
            "characters": ', '.join(characters),
            "tone": tone
        })
        return result.get("draft", f"Dialogue for {', '.join(characters)}")
    except Exception as e:
        logger.error(f"Groq generation failed: {e}")
        return f"Dialogue for {', '.join(characters)}"

# Story structure templates
STORY_STRUCTURES = {
    "hero_journey": [
        ("YOU", "Establish ordinary world"),
        ("NEED", "Protagonist lacks something"), 
        ("GO", "Cross threshold"),
        ("SEARCH", "Trials and learning"),
        ("FIND", "Revelation"),
        ("TAKE", "Costly decision"),
        ("RETURN", "Back to world"),
        ("CHANGE", "Transformed self")
    ],
    "harmon_8": [
        ("HOOK", "Opening that grabs attention"),
        ("STAKES", "What's at risk"),
        ("PLOT_TURN_1", "First major plot point"),
        ("PINCH_1", "First pinch point"),
        ("MIDPOINT", "Middle of story"),
        ("PINCH_2", "Second pinch point"),
        ("PLOT_TURN_2", "Second major plot point"),
        ("RESOLUTION", "Final resolution")
    ],
    "kishotenketsu": [
        ("KI", "Introduction - establish setting and characters"),
        ("SHO", "Development - develop the situation"),
        ("TEN", "Twist - unexpected turn of events"),
        ("KETSU", "Conclusion - resolution and meaning")
    ]
}

class SceneCard(BaseModel):
    slug: str = Field(..., min_length=1, max_length=100, description="Scene identifier")
    where: str = Field(..., min_length=1, max_length=200, description="Scene location")
    who: List[str] = Field(..., min_length=1, description="Characters in scene")
    goal: str = Field(..., min_length=1, max_length=500, description="Scene objective")
    when: Optional[Dict[str, str]] = Field(None, description="Temporal information")
    conflict_or_twist: Optional[str] = Field(None, max_length=500, description="Conflict or plot twist")
    value_shift: Dict[str, Any] = Field(default_factory=dict, description="Value changes in scene")
    promises_made: Optional[List[str]] = Field(None, description="Promises established")
    promises_paid: Optional[List[str]] = Field(None, description="Promises fulfilled")
    canon_refs: Optional[List[str]] = Field(None, description="References to canon entities")
    
    @field_validator('who')
    @classmethod
    def validate_who(cls, v):
        if not v:
            raise ValueError("At least one character must be specified")
        return v

class OutlineReq(BaseModel):
    world_id: str = Field(..., min_length=1, description="World identifier")
    premise: str = Field(..., min_length=10, max_length=1000, description="Story premise")
    mode: str = Field(..., description="Story structure mode")
    constraints: Optional[List[str]] = Field(None, description="Story constraints")
    draft_text: Optional[str] = Field(None, description="Existing draft text")
    cards: Optional[List[SceneCard]] = Field(None, description="Existing scene cards")
    
    @field_validator('mode')
    @classmethod
    def validate_mode(cls, v):
        if v not in STORY_STRUCTURES:
            raise ValueError(f"Invalid mode. Must be one of: {', '.join(STORY_STRUCTURES.keys())}")
        return v

class StoryBeat(BaseModel):
    id: str
    note: str
    description: Optional[str] = None
    scene_cards: Optional[List[SceneCard]] = None

@app.get("/health")
def health():
    """Health check endpoint"""
    return envelope_ok({"ok": True}, {"actor": "api"})

@app.post("/narrative/outline/v1")
def outline(req: OutlineReq):
    """Generate narrative outline with story structure and AI-enhanced descriptions"""
    try:
        # Get story structure based on mode
        structure = STORY_STRUCTURES.get(req.mode, STORY_STRUCTURES["hero_journey"])
        beats = []

        # Generate context from existing cards
        context = ""
        if req.cards:
            context = f"Existing scene cards: {len(req.cards)} scenes. "
            locations = set(card.where for card in req.cards)
            characters = set()
            for card in req.cards:
                characters.update(card.who)
            context += f"Locations: {', '.join(locations)}. Characters: {', '.join(characters)}."

        for beat_id, beat_note in structure:
            # Find related scene cards for this beat
            related_cards = []
            if req.cards:
                for card in req.cards:
                    # Simple heuristic to match cards to beats
                    if beat_id in ["YOU", "HOOK", "KI"] and "establish" in card.goal.lower():
                        related_cards.append(card)
                    elif beat_id in ["NEED", "STAKES", "SHO"] and "lack" in card.goal.lower():
                        related_cards.append(card)
                    elif beat_id in ["GO", "SEARCH", "TEN"] and ("journey" in card.goal.lower() or "search" in card.goal.lower()):
                        related_cards.append(card)
                    elif beat_id in ["FIND", "TAKE", "CHANGE"] and ("change" in card.goal.lower() or "transformation" in card.goal.lower()):
                        related_cards.append(card)
                    elif beat_id in ["RETURN", "RESOLUTION", "KETSU"] and ("resolution" in card.goal.lower() or "end" in card.goal.lower()):
                        related_cards.append(card)

            # Generate AI-enhanced description
            ai_description = generate_story_beat_description(beat_id, beat_note, req.premise, context)
            description = ai_description if ai_description else f"Beat: {beat_note}"

            beats.append(StoryBeat(
                id=beat_id,
                note=beat_note,
                description=description,
                scene_cards=related_cards
            ))
        
        # Analyze promise/payoff ledger
        ledger = compute_promise_payoff([c.model_dump() for c in (req.cards or [])])
        
        # Check trope budget
        ok_trope, counts = trope_budget_ok(req.draft_text or "", banned=[
            "chosen one", "ancient prophecy", "dark lord", "it was all a dream", 
            "mysterious stranger", "forbidden forest", "destined to", 
            "balance of light and dark", "last of their kind", "prophecy foretold", 
            "bloodline power", "chosen by fate", "prophecy says", "ancient evil"
        ], max_per_1k=2)
        
        # Collect issues
        issues = []
        if ledger["orphans"]:
            issues.append({
                "type": "promise_orphans", 
                "items": ledger["orphans"],
                "severity": "warning"
            })
        if ledger["extraneous"]:
            issues.append({
                "type": "promise_extraneous", 
                "items": ledger["extraneous"],
                "severity": "info"
            })
        if not ok_trope:
            issues.append({
                "type": "trope_budget", 
                "counts": counts,
                "severity": "error"
            })
        
        # Generate story analysis
        analysis = {
            "structure_mode": req.mode,
            "total_beats": len(beats),
            "total_scenes": len(req.cards or []),
            "promise_balance": len(ledger["orphans"]) == 0 and len(ledger["extraneous"]) == 0,
            "trope_compliance": ok_trope
        }
        
        return envelope_ok({
            "beats": [beat.model_dump() for beat in beats],
            "issues": issues,
            "ledger": ledger,
            "analysis": analysis
        }, {"actor": "ai", "world_id": req.world_id})
        
    except Exception as e:
        logger.error(f"Failed to generate outline: {e}")
        return envelope_error("OUTLINE_FAILED", "Failed to generate narrative outline", 
                            {"detail": str(e)}, {"actor": "ai", "world_id": req.world_id})

@app.get("/narrative/structures")
def get_structures():
    """Get available story structures"""
    return envelope_ok({
        "structures": {
            name: [{"id": beat_id, "note": beat_note} for beat_id, beat_note in beats]
            for name, beats in STORY_STRUCTURES.items()
        }
    }, {"actor": "api"})

@app.post("/narrative/analyze")
def analyze_story(req: OutlineReq):
    """Analyze existing story for issues and improvements"""
    try:
        # Deep analysis of story structure
        ledger = compute_promise_payoff([c.model_dump() for c in (req.cards or [])])
        ok_trope, counts = trope_budget_ok(req.draft_text or "", banned=[
            "chosen one", "ancient prophecy", "dark lord", "it was all a dream", 
            "mysterious stranger", "forbidden forest", "destined to", 
            "balance of light and dark", "last of their kind", "prophecy foretold", 
            "bloodline power"
        ], max_per_1k=2)
        
        # Character analysis
        characters = set()
        if req.cards:
            for card in req.cards:
                characters.update(card.who)
        
        # Location analysis
        locations = set()
        if req.cards:
            for card in req.cards:
                locations.add(card.where)
        
        # Generate recommendations
        recommendations = []
        if len(ledger["orphans"]) > 0:
            recommendations.append({
                "type": "promise_resolution",
                "message": f"Resolve {len(ledger['orphans'])} unresolved promises",
                "items": ledger["orphans"][:3]  # Show first 3
            })
        
        if not ok_trope:
            recommendations.append({
                "type": "trope_reduction",
                "message": "Reduce overused tropes for originality",
                "counts": counts
            })
        
        if len(characters) < 3:
            recommendations.append({
                "type": "character_development",
                "message": "Consider adding more characters for depth"
            })
        
        if len(locations) < 2:
            recommendations.append({
                "type": "setting_variety",
                "message": "Consider adding more locations for visual interest"
            })
        
        return envelope_ok({
            "analysis": {
                "character_count": len(characters),
                "location_count": len(locations),
                "scene_count": len(req.cards or []),
                "promise_balance": len(ledger["orphans"]) == 0,
                "trope_compliance": ok_trope
            },
            "recommendations": recommendations,
            "ledger": ledger
        }, {"actor": "ai", "world_id": req.world_id})
        
    except Exception as e:
        logger.error(f"Failed to analyze story: {e}")
        return envelope_error("ANALYSIS_FAILED", "Failed to analyze story",
                            {"detail": str(e)}, {"actor": "ai", "world_id": req.world_id})

# -------- Narrative creative generation (HF ONLY) --------
class GenReq(BaseModel):
    task: str = Field(..., description="Task type: logline|outline|scene|rewrite|lineedit|character_bible")
    inputs: Dict[str, Any] = Field(..., description="Task-specific input parameters")
    options: Optional[Dict[str, Any]] = Field(None, description="Generation options (temperature, max_tokens, etc.)")

class PlotGenReq(BaseModel):
    premise: str = Field(..., min_length=10, max_length=500, description="Story premise")
    genre: Optional[str] = Field("fantasy", description="Story genre")
    constraints: Optional[List[str]] = Field(None, description="Plot constraints")
    length: Optional[str] = Field("medium", description="Desired plot length")
    tone: Optional[str] = Field("balanced", description="Story tone")

class CharacterGenReq(BaseModel):
    name: str = Field(..., min_length=1, max_length=50, description="Character name")
    role: str = Field(..., min_length=1, max_length=100, description="Character role")
    world_context: str = Field(..., min_length=10, max_length=1000, description="World/setting context")
    archetype: Optional[str] = Field(None, description="Character archetype")

class DialogueGenReq(BaseModel):
    scene_context: str = Field(..., min_length=10, max_length=500, description="Scene description")
    characters: List[str] = Field(..., min_length=2, description="Characters in dialogue")
    tone: Optional[str] = Field("natural", description="Dialogue tone")
    purpose: Optional[str] = Field("advance_plot", description="Dialogue purpose")

@app.post("/narrative/generate/plot")
def generate_plot(req: GenReq):
    """Generate a complete plot outline using Groq 70B"""
    try:
        out = hf_generate("logline", req.inputs, req.options)
        return envelope_ok({
            "draft": out["draft"],
            "issues": out["issues"],
            "model": out["model"],
            "provider": out["provider"],
            "controls": out["controls"]
        }, {"actor": "ai"})

    except Exception as e:
        logger.error(f"Failed to generate plot: {e}")
        return envelope_error("PLOT_GEN_FAILED", "Failed to generate plot",
                            {"detail": str(e)}, {"actor": "ai"})

@app.post("/narrative/generate/character")
def generate_character(req: GenReq):
    """Generate a detailed character profile using Groq 70B"""
    try:
        out = hf_generate("character_bible", req.inputs, req.options)
        return envelope_ok({
            "draft": out["draft"],
            "issues": out["issues"],
            "model": out["model"],
            "provider": out["provider"],
            "controls": out["controls"]
        }, {"actor": "ai"})

    except Exception as e:
        logger.error(f"Failed to generate character: {e}")
        return envelope_error("CHARACTER_GEN_FAILED", "Failed to generate character",
                            {"detail": str(e)}, {"actor": "ai"})

@app.post("/narrative/generate/dialogue")
def generate_dialogue_endpoint(req: GenReq):
    """Generate dialogue for a scene using Groq 70B"""
    try:
        out = hf_generate("scene", req.inputs, req.options)
        return envelope_ok({
            "draft": out["draft"],
            "issues": out["issues"],
            "model": out["model"],
            "provider": out["provider"],
            "controls": out["controls"]
        }, {"actor": "ai"})

    except Exception as e:
        logger.error(f"Failed to generate dialogue: {e}")
        return envelope_error("DIALOGUE_GEN_FAILED", "Failed to generate dialogue",
                            {"detail": str(e)}, {"actor": "ai"})

class ModelSelectionReq(BaseModel):
    model_type: str = Field(..., description="Type of model (chat, embedding, image)")
    preferred_model: Optional[str] = Field(None, description="Specific model to use")
    capabilities: Optional[List[str]] = Field(None, description="Required capabilities")

def get_available_models():
    """Get available models from LM Studio"""
    try:
        lm_api = pathlib.Path(__file__).parent.parent.parent / "scripts" / "lm_api.py"
        cmd = ["python3", str(lm_api), "models"]

        result = subprocess.run(cmd, capture_output=True, text=True, cwd=pathlib.Path(__file__).parent.parent.parent)

        if result.returncode == 0:
            try:
                response = json.loads(result.stdout.strip())
                if response.get("status") == "success":
                    return response.get("data", {}).get("models", [])
                else:
                    logger.error(f"LM Studio models error: {response.get('error', {}).get('message', 'Unknown error')}")
                    return []
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse LM Studio models response: {e}")
                return []
        else:
            logger.error(f"LM Studio models command failed: {result.stderr}")
            return []
    except Exception as e:
        logger.error(f"Error getting available models: {e}")
        return []

def select_optimal_model(model_type: str, preferred_model: str = None, capabilities: List[str] = None):
    """Select the best available model based on type and requirements"""
    available_models = get_available_models()

    if not available_models:
        return None

    # Filter models by type
    if model_type == "chat":
        # Prefer chat models over embedding models
        chat_models = [m for m in available_models if "embedding" not in m.get("id", "").lower()]
        if chat_models:
            available_models = chat_models

    elif model_type == "embedding":
        # Prefer embedding models
        embedding_models = [m for m in available_models if "embedding" in m.get("id", "").lower()]
        if embedding_models:
            available_models = embedding_models

    # If preferred model is specified and available, use it
    if preferred_model:
        for model in available_models:
            if preferred_model in model.get("id", ""):
                return model

    # Otherwise, select the first available model
    return available_models[0] if available_models else None

@app.get("/narrative/models")
def get_models():
    """Get available AI models for content generation"""
    try:
        models = get_available_models()

        # Categorize models
        chat_models = []
        embedding_models = []
        other_models = []

        for model in models:
            model_id = model.get("id", "")
            if "embedding" in model_id.lower():
                embedding_models.append(model)
            elif any(keyword in model_id.lower() for keyword in ["qwen", "llama", "mistral", "gpt"]):
                chat_models.append(model)
            else:
                other_models.append(model)

        return envelope_ok({
            "models": {
                "chat": chat_models,
                "embedding": embedding_models,
                "other": other_models,
                "total": len(models)
            },
            "default_model": select_optimal_model("chat")
        }, {"actor": "api"})

    except Exception as e:
        logger.error(f"Failed to get models: {e}")
        return envelope_error("MODELS_FAILED", "Failed to retrieve available models",
                            {"detail": str(e)}, {"actor": "api"})

@app.post("/narrative/models/select")
def select_model(req: ModelSelectionReq):
    """Select and configure a specific AI model for content generation"""
    try:
        selected_model = select_optimal_model(
            req.model_type,
            req.preferred_model,
            req.capabilities
        )

        if not selected_model:
            return envelope_error("MODEL_SELECTION_FAILED", "No suitable model found",
                                {"model_type": req.model_type, "preferred": req.preferred_model}, {"actor": "api"})

        # Store model selection (in a real implementation, this would persist the selection)
        model_config = {
            "selected_model": selected_model,
            "model_type": req.model_type,
            "capabilities": req.capabilities or [],
            "timestamp": datetime.now().isoformat()
        }

        return envelope_ok({
            "model_selection": model_config,
            "message": f"Successfully selected {selected_model.get('id')} for {req.model_type} tasks"
        }, {"actor": "api", "model_id": selected_model.get("id")})

    except Exception as e:
        logger.error(f"Failed to select model: {e}")
        return envelope_error("MODEL_SELECTION_FAILED", "Failed to select model",
                            {"detail": str(e)}, {"actor": "api"})
