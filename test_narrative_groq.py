#!/usr/bin/env python3
"""
Test script for PR-0034 - Narrative Groq Hardening
Run this to verify the implementation works before starting the service.
"""

import os
import sys
import time

# Add the project root to Python path
sys.path.insert(0, '/home/mccoy/Projects/StoryMaker/storymaker-bundle-v1.6-unified-full')

def test_groq_client():
    """Test the Groq client configuration"""
    print("🔧 Testing Groq client configuration...")
    
    try:
        from services.narrative.providers.groq_client import get_config, GroqError
        cfg = get_config()
        print(f"✅ Groq config loaded: model={cfg.model}")
        return True
    except GroqError as e:
        print(f"❌ Groq config error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_generator():
    """Test the generator service"""
    print("🔧 Testing generator service...")
    
    try:
        from services.narrative.services.generator import generate_outline
        result = generate_outline("test", "A test story", "hero_journey")
        if result.get("status") == "ok":
            print("✅ Generator service working")
            return True
        else:
            print(f"❌ Generator error: {result}")
            return False
    except Exception as e:
        print(f"❌ Generator error: {e}")
        return False

def test_api():
    """Test the API structure"""
    print("🔧 Testing API structure...")
    
    try:
        from services.narrative.api import router
        print("✅ API router loaded")
        return True
    except Exception as e:
        print(f"❌ API error: {e}")
        return False

def test_main_app():
    """Test the main FastAPI app"""
    print("🔧 Testing main app...")
    
    try:
        from services.narrative.main_new import app
        print("✅ Main app loaded")
        return True
    except Exception as e:
        print(f"❌ Main app error: {e}")
        return False

def main():
    print("🚀 Testing PR-0034 - Narrative Groq Hardening")
    print("=" * 50)
    
    # Check environment
    groq_key = os.environ.get("GROQ_API_KEY", "")
    if groq_key:
        print(f"✅ GROQ_API_KEY found: {groq_key[:10]}...")
    else:
        print("❌ GROQ_API_KEY not found in environment")
        print("   Set it with: export GROQ_API_KEY=your_key_here")
        return False
    
    groq_model = os.environ.get("GROQ_MODEL", "")
    if groq_model:
        print(f"✅ GROQ_MODEL found: {groq_model}")
    else:
        print("❌ GROQ_MODEL not found in environment")
        print("   Set it with: export GROQ_MODEL=llama-3.3-70b-versatile")
        return False
    
    print()
    
    # Run tests
    tests = [
        test_groq_client,
        test_generator,
        test_api,
        test_main_app
    ]
    
    passed = 0
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 All tests passed! The implementation is ready.")
        print()
        print("Next steps:")
        print("1. Install dependencies: uv add groq python-dotenv")
        print("2. Start the service: uv run uvicorn services.narrative.main_new:app --port 8001")
        print("3. Test endpoints:")
        print("   curl http://127.0.0.1:8001/health")
        print("   curl http://127.0.0.1:8001/health/ready")
        print("   curl http://127.0.0.1:8001/narrative/diag/provider")
        return True
    else:
        print("❌ Some tests failed. Check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
