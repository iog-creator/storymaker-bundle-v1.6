"""
Enhanced Media Service Tests
Tests for the improved Media service with watermarking and asset management
"""

import pytest
from fastapi.testclient import TestClient
from services.media.main import (
    app, AudioReq, VisualReq, MediaAsset,
    SUPPORTED_VOICES, SUPPORTED_PROVIDERS
)

client = TestClient(app)

class TestAudioRequestValidation:
    """Test AudioReq validation"""
    
    def test_valid_audio_request(self):
        """Test creating a valid audio request"""
        request = AudioReq(
            ssml="<speak>Hello, this is a test.</speak>",
            voice="neutral",
            speed=1.0,
            pitch=1.0,
            volume=1.0
        )
        assert request.ssml == "<speak>Hello, this is a test.</speak>"
        assert request.voice == "neutral"
        assert request.speed == 1.0
    
    def test_invalid_voice(self):
        """Test audio request with invalid voice"""
        with pytest.raises(ValueError, match="Invalid voice"):
            AudioReq(
                ssml="<speak>Hello</speak>",
                voice="invalid_voice"
            )
    
    def test_ssml_too_short(self):
        """Test audio request with SSML too short"""
        with pytest.raises(ValueError):
            AudioReq(
                ssml="",  # Empty
                voice="neutral"
            )
    
    def test_ssml_too_long(self):
        """Test audio request with SSML too long"""
        with pytest.raises(ValueError):
            AudioReq(
                ssml="a" * 5001,  # Too long
                voice="neutral"
            )
    
    def test_speed_out_of_range(self):
        """Test audio request with speed out of range"""
        with pytest.raises(ValueError):
            AudioReq(
                ssml="<speak>Hello</speak>",
                voice="neutral",
                speed=3.0  # Too high
            )
    
    def test_pitch_out_of_range(self):
        """Test audio request with pitch out of range"""
        with pytest.raises(ValueError):
            AudioReq(
                ssml="<speak>Hello</speak>",
                voice="neutral",
                pitch=0.1  # Too low
            )
    
    def test_volume_out_of_range(self):
        """Test audio request with volume out of range"""
        with pytest.raises(ValueError):
            AudioReq(
                ssml="<speak>Hello</speak>",
                voice="neutral",
                volume=3.0  # Too high
            )

class TestVisualRequestValidation:
    """Test VisualReq validation"""
    
    def test_valid_visual_request(self):
        """Test creating a valid visual request"""
        request = VisualReq(
            prompt="A mysterious harbor shrouded in fog",
            anchors=["p_harbor", "ch_elyra"],
            style="realistic",
            size="1024x1024",
            provider="gemini",
            watermark_type="synthid"
        )
        assert request.prompt == "A mysterious harbor shrouded in fog"
        assert request.anchors == ["p_harbor", "ch_elyra"]
        assert request.provider == "gemini"
    
    def test_invalid_provider(self):
        """Test visual request with invalid provider"""
        with pytest.raises(ValueError, match="Invalid provider"):
            VisualReq(
                prompt="A mysterious harbor",
                provider="invalid_provider"
            )
    
    def test_prompt_too_short(self):
        """Test visual request with prompt too short"""
        with pytest.raises(ValueError):
            VisualReq(
                prompt="",  # Empty
                provider="gemini"
            )
    
    def test_prompt_too_long(self):
        """Test visual request with prompt too long"""
        with pytest.raises(ValueError):
            VisualReq(
                prompt="a" * 1001,  # Too long
                provider="gemini"
            )

class TestMediaAPI:
    """Test Media API endpoints"""
    
    def test_health_endpoint(self):
        """Test health endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "ok"
        assert data["data"]["ok"] is True
    
    def test_audio_synth_endpoint(self):
        """Test audio synthesis endpoint"""
        request_data = {
            "ssml": "<speak>Hello, this is a test of the audio synthesis system.</speak>",
            "voice": "neutral",
            "speed": 1.0,
            "pitch": 1.0,
            "volume": 1.0
        }
        
        response = client.post("/audio/synth", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "ok"
        assert "audio" in data["data"]
        
        audio = data["data"]["audio"]
        assert "id" in audio
        assert "uri" in audio
        assert "duration_sec" in audio
        assert "metadata" in audio
        
        metadata = audio["metadata"]
        assert metadata["voice"] == "neutral"
        assert metadata["speed"] == 1.0
        assert metadata["pitch"] == 1.0
        assert metadata["volume"] == 1.0
        assert metadata["format"] == "mp3"
    
    def test_audio_synth_duration_calculation(self):
        """Test audio synthesis duration calculation"""
        request_data = {
            "ssml": "Hello world " * 10,  # 20 words
            "voice": "neutral",
            "speed": 2.0  # Double speed
        }
        
        response = client.post("/audio/synth", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        audio = data["data"]["audio"]
        metadata = audio["metadata"]
        
        # 20 words at 150 words/minute = 8 seconds, at 2x speed = 4 seconds
        expected_duration = (20 / 150) * 60 / 2.0
        assert abs(audio["duration_sec"] - expected_duration) < 0.1
        assert metadata["word_count"] == 20
    
    def test_visual_generate_endpoint(self):
        """Test visual generation endpoint"""
        request_data = {
            "prompt": "A mysterious harbor shrouded in fog at dawn",
            "anchors": ["p_harbor", "ch_elyra"],
            "style": "realistic",
            "size": "1024x1024",
            "provider": "gemini",
            "watermark_type": "synthid"
        }
        
        response = client.post("/visual/generate", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "ok"
        assert "image" in data["data"]
        
        image = data["data"]["image"]
        assert "id" in image
        assert "uri" in image
        assert "provider" in image
        assert "watermark" in image
        assert "metadata" in image
        
        assert image["provider"] == "gemini"
        assert image["watermark"]["type"] == "synthid"
        assert image["watermark"]["present"] is True
        
        metadata = image["metadata"]
        assert metadata["provider"] == "gemini"
        assert metadata["style"] == "realistic"
        assert metadata["size"] == "1024x1024"
        assert metadata["anchors"] == ["p_harbor", "ch_elyra"]
    
    def test_visual_generate_watermark_metadata(self):
        """Test visual generation watermark metadata"""
        request_data = {
            "prompt": "A test image",
            "provider": "gemini",
            "watermark_type": "visible"
        }
        
        response = client.post("/visual/generate", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        image = data["data"]["image"]
        watermark = image["watermark"]
        
        assert watermark["type"] == "visible"
        assert watermark["present"] is True
        assert watermark["method"] == "synthid"
        assert watermark["strength"] == 0.8
        assert watermark["position"] == "bottom_right"
        assert watermark["opacity"] == 0.7
    
    def test_get_assets_endpoint(self):
        """Test get assets endpoint"""
        response = client.get("/media/assets")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "ok"
        assert "assets" in data["data"]
        assert "count" in data["data"]
        assert "total" in data["data"]
        
        assets = data["data"]["assets"]
        assert len(assets) >= 0  # Should have some test assets
        
        if assets:
            asset = assets[0]
            assert "id" in asset
            assert "type" in asset
            assert "uri" in asset
            assert "size_bytes" in asset
            assert "created_at" in asset
            assert "metadata" in asset
    
    def test_get_assets_with_limit(self):
        """Test get assets endpoint with limit"""
        response = client.get("/media/assets?limit=50")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "ok"
        assert data["data"]["count"] <= 50
    
    def test_get_assets_with_type_filter(self):
        """Test get assets endpoint with type filter"""
        response = client.get("/media/assets?asset_type=audio")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "ok"
        
        assets = data["data"]["assets"]
        for asset in assets:
            assert asset["type"] == "audio"
    
    def test_get_assets_limit_cap(self):
        """Test get assets endpoint with limit cap"""
        response = client.get("/media/assets?limit=2000")  # Over the 1000 cap
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "ok"
        # The limit should be capped to 1000 internally
    
    def test_get_providers_endpoint(self):
        """Test get providers endpoint"""
        response = client.get("/media/providers")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "ok"
        assert "audio_providers" in data["data"]
        assert "image_providers" in data["data"]
        
        audio_providers = data["data"]["audio_providers"]
        assert len(audio_providers) > 0
        
        image_providers = data["data"]["image_providers"]
        assert len(image_providers) > 0
        
        # Check LM Studio provider
        lm_studio = next((p for p in audio_providers if p["id"] == "lm_studio"), None)
        assert lm_studio is not None
        assert lm_studio["name"] == "LM Studio"
        assert "supported_voices" in lm_studio
        
        # Check Gemini provider
        gemini = next((p for p in image_providers if p["id"] == "gemini"), None)
        assert gemini is not None
        assert gemini["name"] == "Google Gemini"
        assert "supported_styles" in gemini
    
    def test_get_watermark_types_endpoint(self):
        """Test get watermark types endpoint"""
        response = client.get("/media/watermarks")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "ok"
        assert "watermark_types" in data["data"]
        
        watermark_types = data["data"]["watermark_types"]
        assert len(watermark_types) >= 3
        
        # Check synthid watermark
        synthid = next((w for w in watermark_types if w["id"] == "synthid"), None)
        assert synthid is not None
        assert synthid["name"] == "Synthetic ID"
        assert synthid["detectable"] is True
        assert synthid["removable"] is False
        
        # Check visible watermark
        visible = next((w for w in watermark_types if w["id"] == "visible"), None)
        assert visible is not None
        assert visible["name"] == "Visible Watermark"
        assert visible["detectable"] is True
        assert visible["removable"] is True
        
        # Check invisible watermark
        invisible = next((w for w in watermark_types if w["id"] == "invisible"), None)
        assert invisible is not None
        assert invisible["name"] == "Invisible Watermark"
        assert invisible["detectable"] is True
        assert invisible["removable"] is False

class TestAssetGeneration:
    """Test asset generation functionality"""
    
    def test_audio_asset_metadata(self):
        """Test audio asset metadata generation"""
        request_data = {
            "ssml": "<speak>This is a test with multiple words for duration calculation.</speak>",
            "voice": "female",
            "speed": 1.5,
            "pitch": 0.8,
            "volume": 0.9
        }
        
        response = client.post("/audio/synth", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        audio = data["data"]["audio"]
        metadata = audio["metadata"]
        
        # Check all metadata fields
        assert "ssml_hash" in metadata
        assert metadata["voice"] == "female"
        assert metadata["speed"] == 1.5
        assert metadata["pitch"] == 0.8
        assert metadata["volume"] == 0.9
        assert "word_count" in metadata
        assert "estimated_duration" in metadata
        assert metadata["format"] == "mp3"
        assert metadata["sample_rate"] == 44100
        assert metadata["bitrate"] == 128
        
        # Check URI format
        assert audio["uri"].startswith("asset://audio/")
        assert audio["uri"].endswith("/synthesis.mp3")
    
    def test_image_asset_metadata(self):
        """Test image asset metadata generation"""
        request_data = {
            "prompt": "A test image with specific details for metadata testing",
            "anchors": ["p_harbor", "ch_elyra", "w_eldershore"],
            "style": "artistic",
            "size": "2048x2048",
            "provider": "dalle",
            "watermark_type": "invisible"
        }
        
        response = client.post("/visual/generate", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        image = data["data"]["image"]
        metadata = image["metadata"]
        
        # Check all metadata fields
        assert "prompt_hash" in metadata
        assert metadata["provider"] == "dalle"
        assert metadata["style"] == "artistic"
        assert metadata["size"] == "2048x2048"
        assert metadata["anchors"] == ["p_harbor", "ch_elyra", "w_eldershore"]
        assert metadata["watermark"]["type"] == "invisible"
        assert metadata["format"] == "png"
        assert metadata["quality"] == "high"
        
        # Check URI format
        assert image["uri"].startswith("asset://images/")
        assert image["uri"].endswith("/generated.png")
    
    def test_asset_id_uniqueness(self):
        """Test that asset IDs are unique"""
        request_data = {
            "ssml": "<speak>Test</speak>",
            "voice": "neutral"
        }
        
        response1 = client.post("/audio/synth", json=request_data)
        response2 = client.post("/audio/synth", json=request_data)
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        data1 = response1.json()
        data2 = response2.json()
        
        audio1 = data1["data"]["audio"]
        audio2 = data2["data"]["audio"]
        
        assert audio1["id"] != audio2["id"]
        assert audio1["uri"] != audio2["uri"]
    
    def test_prompt_hash_consistency(self):
        """Test that identical prompts generate consistent hashes"""
        request_data = {
            "prompt": "A consistent test prompt for hash testing",
            "provider": "gemini"
        }
        
        response1 = client.post("/visual/generate", json=request_data)
        response2 = client.post("/visual/generate", json=request_data)
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        data1 = response1.json()
        data2 = response2.json()
        
        metadata1 = data1["data"]["image"]["metadata"]
        metadata2 = data2["data"]["image"]["metadata"]
        
        assert metadata1["prompt_hash"] == metadata2["prompt_hash"]
    
    def test_ssml_hash_consistency(self):
        """Test that identical SSML generates consistent hashes"""
        request_data = {
            "ssml": "<speak>A consistent test for hash testing</speak>",
            "voice": "neutral"
        }
        
        response1 = client.post("/audio/synth", json=request_data)
        response2 = client.post("/audio/synth", json=request_data)
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        data1 = response1.json()
        data2 = response2.json()
        
        metadata1 = data1["data"]["audio"]["metadata"]
        metadata2 = data2["data"]["audio"]["metadata"]
        
        assert metadata1["ssml_hash"] == metadata2["ssml_hash"]

class TestSupportedValues:
    """Test supported values and constants"""
    
    def test_supported_voices(self):
        """Test supported voice types"""
        expected_voices = ["male", "female", "neutral", "child", "elderly"]
        assert SUPPORTED_VOICES == expected_voices
    
    def test_supported_providers(self):
        """Test supported image providers"""
        expected_providers = ["gemini", "dalle", "midjourney", "stable_diffusion"]
        assert SUPPORTED_PROVIDERS == expected_providers
    
    def test_all_supported_voices_work(self):
        """Test that all supported voices work in requests"""
        for voice in SUPPORTED_VOICES:
            request_data = {
                "ssml": f"<speak>Testing {voice} voice</speak>",
                "voice": voice
            }
            
            response = client.post("/audio/synth", json=request_data)
            assert response.status_code == 200
            
            data = response.json()
            assert data["data"]["audio"]["metadata"]["voice"] == voice
    
    def test_all_supported_providers_work(self):
        """Test that all supported providers work in requests"""
        for provider in SUPPORTED_PROVIDERS:
            request_data = {
                "prompt": f"Testing {provider} provider",
                "provider": provider
            }
            
            response = client.post("/visual/generate", json=request_data)
            assert response.status_code == 200
            
            data = response.json()
            assert data["data"]["image"]["provider"] == provider
