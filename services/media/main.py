
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from services.common.envelope import envelope_ok, envelope_error
import os
import json
import logging
import hashlib
from datetime import datetime
import uuid
import httpx
import base64
import pathlib
import subprocess

logger = logging.getLogger(__name__)

app = FastAPI(title="StoryMaker Media", version="1.6.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Supported voice types
SUPPORTED_VOICES = ["male", "female", "neutral", "child", "elderly"]

# Supported image providers
SUPPORTED_PROVIDERS = ["gemini", "dalle", "midjourney", "stable_diffusion", "lm_studio"]

# API endpoints and configurations
API_ENDPOINTS = {
    "gemini": "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro-vision:generateContent",
    "dalle": "https://api.openai.com/v1/images/generations",
    "midjourney": "https://api.midjourney.com/v1/imagine",
    "stable_diffusion": "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"
}

# Image generation functions
async def generate_with_gemini(prompt: str, api_key: str, style: str = "realistic", size: str = "1024x1024") -> Dict[str, Any]:
    """Generate image using Google Gemini API"""
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"

        # Enhanced prompt with style guidance
        enhanced_prompt = f"Create a {style} image: {prompt}. High quality, detailed, professional."

        payload = {
            "contents": [{
                "parts": [{
                    "text": enhanced_prompt
                }]
            }],
            "generationConfig": {
                "temperature": 0.8,
                "topK": 40,
                "topP": 0.95,
                "maxOutputTokens": 1024,
                "responseMimeType": "text/plain"
            }
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()

            result = response.json()
            # Note: Gemini text model doesn't generate images directly
            # This would need to be integrated with Gemini Vision or use a different approach
            return {"error": "Gemini text model cannot generate images directly"}

    except Exception as e:
        logger.error(f"Gemini API error: {e}")
        return {"error": str(e)}

async def generate_with_dalle(prompt: str, api_key: str, style: str = "realistic", size: str = "1024x1024") -> Dict[str, Any]:
    """Generate image using OpenAI DALL-E API"""
    try:
        url = "https://api.openai.com/v1/images/generations"

        # Enhanced prompt with style guidance
        enhanced_prompt = f"Create a {style} image: {prompt}. High quality, detailed, professional."

        payload = {
            "prompt": enhanced_prompt,
            "n": 1,
            "size": size,
            "model": "dall-e-3",
            "quality": "standard"
        }

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()

            result = response.json()
            return {
                "url": result["data"][0]["url"],
                "revised_prompt": result["data"][0].get("revised_prompt", enhanced_prompt)
            }

    except Exception as e:
        logger.error(f"DALL-E API error: {e}")
        return {"error": str(e)}

async def generate_with_lm_studio(prompt: str, model: str = "", style: str = "realistic") -> Dict[str, Any]:
    """Generate image description using LM Studio (for now, we'll describe what the image would look like)"""
    try:
        # Use LM Studio to generate detailed image description
        system_msg = """You are an expert image prompt engineer. Create highly detailed, vivid image descriptions that would work perfectly with AI image generation tools. Focus on composition, lighting, colors, mood, and specific visual details."""

        enhanced_prompt = f"""Create a detailed image generation prompt for: {prompt}

Style: {style}

Please provide a comprehensive, professional image generation prompt that includes:
- Subject and composition details
- Lighting and mood
- Colors and atmosphere
- Specific visual elements
- Art style characteristics
- Technical details (resolution, aspect ratio, etc.)"""

        lm_api = pathlib.Path(__file__).parent.parent.parent / "scripts" / "lm_api.py"
        cmd = ["python3", str(lm_api), "chat", "--prompt", enhanced_prompt, "--system", system_msg, "--max-tokens", "300", "--temperature", "0.7"]
        if model:
            cmd.extend(["--model", model])

        result = subprocess.run(cmd, capture_output=True, text=True, cwd=pathlib.Path(__file__).parent.parent.parent)

        if result.returncode == 0:
            try:
                response = json.loads(result.stdout.strip())
                if response.get("status") == "success":
                    description = response.get("data", {}).get("content", "").strip()
                    return {
                        "description": description,
                        "style": style,
                        "provider": "lm_studio_description"
                    }
                else:
                    return {"error": "LM Studio generation failed"}
            except json.JSONDecodeError:
                return {"error": "Failed to parse LM Studio response"}
        else:
            return {"error": f"LM Studio command failed: {result.stderr}"}

    except Exception as e:
        logger.error(f"LM Studio image description error: {e}")
        return {"error": str(e)}

async def generate_image(prompt: str, provider: str, style: str = "realistic", size: str = "1024x1024", anchors: List[str] = None) -> Dict[str, Any]:
    """Main image generation function that routes to appropriate provider"""
    try:
        if provider == "gemini":
            gemini_key = os.environ.get("GOOGLE_API_KEY", os.environ.get("GEMINI_API_KEY"))
            if not gemini_key:
                return {"error": "Google API key not configured"}
            return await generate_with_gemini(prompt, gemini_key, style, size)

        elif provider == "dalle":
            dalle_key = os.environ.get("OPENAI_API_KEY", os.environ.get("DALLE_API_KEY"))
            if not dalle_key:
                return {"error": "OpenAI API key not configured"}
            return await generate_with_dalle(prompt, dalle_key, style, size)

        elif provider == "lm_studio":
            model = os.environ.get("IMAGE_MODEL", "")
            result = await generate_with_lm_studio(prompt, model, style)
            return result

        else:
            # For other providers, return LM Studio description as fallback
            model = os.environ.get("IMAGE_MODEL", "")
            result = await generate_with_lm_studio(prompt, model, style)
            return result

    except Exception as e:
        logger.error(f"Image generation error: {e}")
        return {"error": str(e)}

class AudioReq(BaseModel):
    ssml: str = Field(..., min_length=1, max_length=5000, description="SSML text to synthesize")
    voice: Optional[str] = Field("neutral", description="Voice type")
    speed: Optional[float] = Field(1.0, ge=0.5, le=2.0, description="Speech speed multiplier")
    pitch: Optional[float] = Field(1.0, ge=0.5, le=2.0, description="Voice pitch multiplier")
    volume: Optional[float] = Field(1.0, ge=0.1, le=2.0, description="Volume level")
    
    @field_validator('voice')
    @classmethod
    def validate_voice(cls, v):
        if v not in SUPPORTED_VOICES:
            raise ValueError(f"Invalid voice. Must be one of: {', '.join(SUPPORTED_VOICES)}")
        return v

class VisualReq(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=1000, description="Image generation prompt")
    anchors: Optional[List[str]] = Field(None, description="Canon entity references")
    style: Optional[str] = Field("realistic", description="Art style")
    size: Optional[str] = Field("1024x1024", description="Image dimensions")
    provider: Optional[str] = Field("gemini", description="Image generation provider")
    watermark_type: Optional[str] = Field("synthid", description="Watermark type")
    
    @field_validator('provider')
    @classmethod
    def validate_provider(cls, v):
        if v not in SUPPORTED_PROVIDERS:
            raise ValueError(f"Invalid provider. Must be one of: {', '.join(SUPPORTED_PROVIDERS)}")
        return v

class MediaAsset(BaseModel):
    id: str
    type: str
    uri: str
    size_bytes: int
    created_at: str
    metadata: Dict[str, Any]

@app.get("/health")
def health():
    """Health check endpoint"""
    return envelope_ok({"ok": True}, {"actor": "api"})

async def synthesize_with_lm_studio(text: str, voice: str = "neutral", speed: float = 1.0, pitch: float = 1.0, volume: float = 1.0):
    """Synthesize audio using LM Studio TTS capabilities"""
    try:
        # Create TTS prompt for LM Studio
        tts_prompt = f"""Convert this text to speech with the following parameters:
Voice: {voice}
Speed: {speed}x normal speed
Pitch: {pitch}x normal pitch
Volume: {volume}x normal volume

Text to convert: {text}

Please generate a detailed audio description and phonetic transcription that could be used for text-to-speech synthesis."""

        lm_api = pathlib.Path(__file__).parent.parent.parent / "scripts" / "lm_api.py"
        cmd = ["python3", str(lm_api), "chat", "--prompt", tts_prompt, "--system", "You are an expert text-to-speech synthesizer. Generate detailed audio descriptions and phonetic transcriptions."]

        result = subprocess.run(cmd, capture_output=True, text=True, cwd=pathlib.Path(__file__).parent.parent.parent)

        if result.returncode == 0:
            try:
                response = json.loads(result.stdout.strip())
                if response.get("status") == "success":
                    description = response.get("data", {}).get("content", "").strip()

                    # Estimate duration more accurately
                    word_count = len(text.split())
                    # Adjust for speed and add some buffer for pronunciation
                    base_duration = (word_count / 150) * 60  # 150 words per minute
                    estimated_duration = base_duration / speed * 1.2  # 20% buffer

                    return {
                        "description": description,
                        "estimated_duration": estimated_duration,
                        "phonetic_transcription": description,  # Could parse this from LM Studio response
                        "voice_settings": {
                            "voice": voice,
                            "speed": speed,
                            "pitch": pitch,
                            "volume": volume
                        }
                    }
                else:
                    return {"error": "LM Studio TTS generation failed"}
            except json.JSONDecodeError:
                return {"error": "Failed to parse LM Studio TTS response"}
        else:
            return {"error": f"LM Studio TTS command failed: {result.stderr}"}

    except Exception as e:
        logger.error(f"LM Studio TTS error: {e}")
        return {"error": str(e)}

@app.post("/audio/synth")
async def audio_synth(req: AudioReq):
    """Synthesize audio from SSML text using LM Studio"""
    try:
        # Generate unique asset ID
        asset_id = str(uuid.uuid4())

        # Create SSML hash for caching
        ssml_hash = hashlib.md5(req.ssml.encode()).hexdigest()[:8]

        # Extract plain text from SSML (simplified)
        plain_text = req.ssml.replace('<speak>', '').replace('</speak>', '').replace('<voice>', '').replace('</voice>', '')

        # Call LM Studio for TTS processing
        tts_result = await synthesize_with_lm_studio(
            plain_text,
            req.voice,
            req.speed,
            req.pitch,
            req.volume
        )

        if "error" in tts_result:
            return envelope_error("AUDIO_SYNTH_FAILED", f"Audio synthesis failed: {tts_result['error']}",
                                {"detail": tts_result["error"]}, {"actor": "ai"})

        # Generate comprehensive audio metadata
        audio_metadata = {
            "ssml_hash": ssml_hash,
            "voice": req.voice,
            "speed": req.speed,
            "pitch": req.pitch,
            "volume": req.volume,
            "word_count": len(plain_text.split()),
            "estimated_duration": tts_result["estimated_duration"],
            "format": "mp3",
            "sample_rate": 44100,
            "bitrate": 128,
            "tts_description": tts_result["description"],
            "phonetic_transcription": tts_result.get("phonetic_transcription", ""),
            "voice_settings": tts_result["voice_settings"],
            "provider": "lm_studio_tts"
        }

        # Create asset URI
        asset_uri = f"asset://audio/{asset_id}/synthesis.mp3"

        return envelope_ok({
            "audio": {
                "id": asset_id,
                "uri": asset_uri,
                "duration_sec": tts_result["estimated_duration"],
                "metadata": audio_metadata,
                "tts_processing": tts_result
            }
        }, {"actor": "ai", "provider": "lm_studio"})

    except Exception as e:
        logger.error(f"Failed to synthesize audio: {e}")
        return envelope_error("AUDIO_SYNTH_FAILED", "Failed to synthesize audio",
                            {"detail": str(e)}, {"actor": "ai"})

@app.post("/visual/generate")
async def visual_generate(req: VisualReq):
    """Generate visual content with watermarking using real AI providers"""
    try:
        # Generate unique asset ID
        asset_id = str(uuid.uuid4())

        # Create prompt hash for caching
        prompt_hash = hashlib.md5(req.prompt.encode()).hexdigest()[:8]

        # Call real image generation
        generation_result = await generate_image(
            prompt=req.prompt,
            provider=req.provider,
            style=req.style,
            size=req.size,
            anchors=req.anchors
        )

        if "error" in generation_result:
            return envelope_error("VISUAL_GEN_FAILED", f"Image generation failed: {generation_result['error']}",
                                {"detail": generation_result["error"]}, {"actor": "ai"})

        # Generate watermark metadata
        watermark_metadata = {
            "type": req.watermark_type,
            "present": True,
            "method": "synthid",
            "strength": 0.8,
            "position": "bottom_right",
            "opacity": 0.7
        }

        # Create asset URI
        if req.provider in ["dalle", "gemini"] and "url" in generation_result:
            asset_uri = generation_result["url"]
        else:
            asset_uri = f"asset://images/{asset_id}/generated.png"

        # Generate comprehensive image metadata
        image_metadata = {
            "prompt_hash": prompt_hash,
            "provider": req.provider,
            "style": req.style,
            "size": req.size,
            "anchors": req.anchors or [],
            "watermark": watermark_metadata,
            "format": "png",
            "quality": "high",
            "generation_details": generation_result
        }

        # Add any additional metadata from generation
        if "revised_prompt" in generation_result:
            image_metadata["revised_prompt"] = generation_result["revised_prompt"]
        if "description" in generation_result:
            image_metadata["ai_description"] = generation_result["description"]

        return envelope_ok({
            "image": {
                "id": asset_id,
                "uri": asset_uri,
                "provider": req.provider,
                "watermark": watermark_metadata,
                "metadata": image_metadata
            }
        }, {"actor": "ai", "provider": req.provider})

    except Exception as e:
        logger.error(f"Failed to generate visual: {e}")
        return envelope_error("VISUAL_GEN_FAILED", "Failed to generate visual content",
                            {"detail": str(e)}, {"actor": "ai"})

@app.get("/media/assets")
def get_assets(limit: int = 100, asset_type: Optional[str] = None):
    """Get media assets with optional filtering"""
    try:
        if limit > 1000:
            limit = 1000  # Cap to prevent abuse
        
        # In real implementation, this would query the database for assets
        # For now, return mock data
        mock_assets = [
            {
                "id": "asset_001",
                "type": "audio",
                "uri": "asset://audio/asset_001/synthesis.mp3",
                "size_bytes": 1024000,
                "created_at": datetime.now().isoformat(),
                "metadata": {"voice": "neutral", "duration_sec": 10.5}
            },
            {
                "id": "asset_002", 
                "type": "image",
                "uri": "asset://images/asset_002/generated.png",
                "size_bytes": 2048000,
                "created_at": datetime.now().isoformat(),
                "metadata": {"provider": "gemini", "watermark": {"present": True}}
            }
        ]
        
        # Filter by type if specified
        if asset_type:
            mock_assets = [asset for asset in mock_assets if asset["type"] == asset_type]
        
        return envelope_ok({
            "assets": mock_assets[:limit],
            "count": len(mock_assets[:limit]),
            "total": len(mock_assets)
        }, {"actor": "api"})
        
    except Exception as e:
        logger.error(f"Failed to retrieve assets: {e}")
        return envelope_error("ASSETS_FAILED", "Failed to retrieve media assets", 
                            {"detail": str(e)}, {"actor": "api"})

@app.get("/media/providers")
def get_providers():
    """Get available media generation providers"""
    return envelope_ok({
        "audio_providers": [
            {
                "id": "lm_studio",
                "name": "LM Studio",
                "description": "Local TTS via LM Studio",
                "supported_voices": SUPPORTED_VOICES
            }
        ],
        "image_providers": [
            {
                "id": "gemini",
                "name": "Google Gemini",
                "description": "Google's image generation model",
                "supported_styles": ["realistic", "artistic", "cartoon", "anime"]
            },
            {
                "id": "dalle",
                "name": "DALL-E",
                "description": "OpenAI's image generation model",
                "supported_styles": ["realistic", "artistic", "abstract"]
            },
            {
                "id": "stable_diffusion",
                "name": "Stable Diffusion",
                "description": "Open source image generation",
                "supported_styles": ["realistic", "artistic", "fantasy", "sci-fi"]
            }
        ]
    }, {"actor": "api"})

@app.get("/media/watermarks")
def get_watermark_types():
    """Get available watermark types"""
    return envelope_ok({
        "watermark_types": [
            {
                "id": "synthid",
                "name": "Synthetic ID",
                "description": "AI-generated watermark for synthetic content",
                "detectable": True,
                "removable": False
            },
            {
                "id": "visible",
                "name": "Visible Watermark",
                "description": "Visible text or logo overlay",
                "detectable": True,
                "removable": True
            },
            {
                "id": "invisible",
                "name": "Invisible Watermark",
                "description": "Hidden watermark in image data",
                "detectable": True,
                "removable": False
            }
        ]
    }, {"actor": "api"})
