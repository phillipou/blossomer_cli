#!/usr/bin/env python3
"""
Test script for TensorBlock Forge migration

This script tests the Forge-based LLM services to ensure the migration 
from individual providers to unified Forge access is working correctly.

IMPORTANT: Set FORGE_API_KEY environment variable before running.
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

# Add CLI modules to path
sys.path.insert(0, str(Path(__file__).parent))

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("📁 Loaded .env file")
except ImportError:
    print("⚠️  python-dotenv not installed, using system environment only")

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def test_forge_client_initialization():
    """Test that the Forge client can be initialized"""
    print("🔧 Testing Forge client initialization...")
    
    try:
        from app.core.forge_client import get_forge_client
        
        # Check if API key is available
        if not os.getenv("FORGE_API_KEY") and not os.getenv("OPENAI_API_KEY"):
            print("  ⚠️  No API key found. Set FORGE_API_KEY or OPENAI_API_KEY to test properly")
            return False
        
        # Try to initialize the client
        forge_client = get_forge_client()
        print("  ✓ Forge client initialized successfully")
        
        # Test model listing
        models = forge_client.list_available_models()
        print(f"  ✓ Available models: {len(models)} models found")
        for model in models[:3]:  # Show first 3 models
            print(f"    - {model}")
        
        # Test model recommendations (TensorBlock provides many options!)
        fast_model = forge_client.get_recommended_model("fast")     # Ultra fast Gemini
        cost_model = forge_client.get_recommended_model("cost")     # Deepseek (very cheap)
        quality_model = forge_client.get_recommended_model("quality") # Latest Claude Sonnet 4
        coding_model = forge_client.get_recommended_model("coding")   # Deepseek (great for code)
        print(f"  ✓ Model recommendations:")
        print(f"    Fast: {fast_model}")
        print(f"    Cost: {cost_model}")
        print(f"    Quality: {quality_model}")
        print(f"    Coding: {coding_model}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Forge client initialization failed: {e}")
        return False


def test_llm_singleton_migration():
    """Test that the LLM singleton uses Forge"""
    print("🤖 Testing LLM singleton migration...")
    
    try:
        from app.core.llm_singleton import get_llm_client
        
        # Get the client
        llm_client = get_llm_client()
        print("  ✓ LLM singleton returns Forge service")
        
        # Check it's the right type
        from app.core.forge_llm_service import ForgeLLMService
        if isinstance(llm_client, ForgeLLMService):
            print("  ✓ LLM client is ForgeLLMService instance")
        else:
            print(f"  ❌ Expected ForgeLLMService, got {type(llm_client)}")
            return False
        
        # Test model management
        default_model = llm_client.default_model
        print(f"  ✓ Default model: {default_model}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ LLM singleton migration test failed: {e}")
        return False


async def test_llm_generation():
    """Test actual LLM generation through Forge"""
    print("🎯 Testing LLM generation...")
    
    try:
        from app.core.forge_llm_service import get_forge_llm_service, LLMRequest
        
        # Check if we have an API key
        if not os.getenv("FORGE_API_KEY") and not os.getenv("OPENAI_API_KEY"):
            print("  ⚠️  Skipping generation test - no API key available")
            return True
        
        # Get the service
        llm_service = get_forge_llm_service()
        
        # Create a simple test request with a fast model
        # Note: Model ID may need to be updated with correct TensorBlock format
        fast_model = llm_service.get_recommended_model("fast")
        request = LLMRequest(
            system_prompt="You are a helpful assistant.",
            user_prompt="Say hello in exactly 3 words.",
            model=fast_model  # Use recommended fast model
        )
        
        print("  🔄 Generating test response...")
        response = await llm_service.generate(request)
        
        print(f"  ✓ Generation successful!")
        print(f"    Model: {response.model}")
        print(f"    Response: {response.text}")
        print(f"    Cost estimate: ${response.cost_estimate:.6f}" if response.cost_estimate else "    Cost estimate: N/A")
        
        return True
        
    except Exception as e:
        print(f"  ❌ LLM generation test failed: {e}")
        return False


async def test_structured_output():
    """Test structured output generation"""
    print("📊 Testing structured output generation...")
    
    try:
        from app.core.forge_llm_service import get_forge_llm_service
        from pydantic import BaseModel
        
        # Check if we have an API key
        if not os.getenv("FORGE_API_KEY") and not os.getenv("OPENAI_API_KEY"):
            print("  ⚠️  Skipping structured output test - no API key available")
            return True
        
        # Define a test schema
        class TestResponse(BaseModel):
            message: str
            word_count: int
            
        # Get the service
        llm_service = get_forge_llm_service()
        
        print("  🔄 Generating structured response...")
        # Use OpenAI for structured output (more reliable for JSON)
        response = await llm_service.generate_structured_output(
            prompt="Create a greeting message with exactly 5 words",
            response_model=TestResponse,
            model="OpenAI/gpt-4o-nano"  # Use 4o-nano - ultra cheap and reliable
        )
        
        print(f"  ✓ Structured generation successful!")
        print(f"    Message: {response.message}")
        print(f"    Word count: {response.word_count}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Structured output test failed: {e}")
        return False


def test_cli_integration():
    """Test that CLI services work with Forge"""
    print("🔧 Testing CLI integration...")
    
    try:
        from cli.services.llm_singleton import get_llm_client
        from app.core.forge_llm_service import ForgeLLMService
        
        # Get CLI client
        cli_client = get_llm_client()
        
        if isinstance(cli_client, ForgeLLMService):
            print("  ✓ CLI LLM singleton uses Forge service")
        else:
            print(f"  ❌ CLI client is not Forge service: {type(cli_client)}")
            return False
        
        # Test model management from CLI
        models = cli_client.get_available_models()
        print(f"  ✓ CLI can access {len(models)} models")
        
        return True
        
    except Exception as e:
        print(f"  ❌ CLI integration test failed: {e}")
        return False


async def run_all_tests():
    """Run all Forge migration tests"""
    print("🚀 Starting TensorBlock Forge migration tests...\n")
    
    # Check environment
    forge_key = os.getenv("FORGE_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")
    
    if forge_key:
        print("✅ FORGE_API_KEY found - unified access to ALL providers!")
        print("🎯 Available: OpenAI, Anthropic (Claude), Gemini, xAI (Grok), Deepseek")
    elif openai_key:
        print("⚠️  Only OPENAI_API_KEY found - limited to OpenAI models")
        print("💡 Set FORGE_API_KEY for access to Claude, Gemini, Grok, and more!")
    else:
        print("❌ No API keys found - some tests will be skipped")
    
    print()
    
    # Run tests
    tests = [
        ("Forge Client", test_forge_client_initialization),
        ("LLM Singleton", test_llm_singleton_migration),
        ("CLI Integration", test_cli_integration),
    ]
    
    async_tests = [
        ("LLM Generation", test_llm_generation),
        ("Structured Output", test_structured_output),
    ]
    
    results = []
    
    # Run sync tests
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
        print()
    
    # Run async tests
    for test_name, test_func in async_tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
        print()
    
    # Summary
    print("📋 Test Results Summary:")
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Forge migration is successful.")
        if not forge_key and openai_key:
            print("💡 Consider setting FORGE_API_KEY for access to Gemini models")
        elif forge_key:
            print("🚀 Unified access enabled - access to Claude 4, Gemini 2.5, Grok 3, and more!")
    else:
        print("⚠️  Some tests failed. Check the logs above for details.")
        
    return passed == total


if __name__ == "__main__":
    print("TensorBlock Forge Migration Test Suite")
    print("=====================================")
    print()
    
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)