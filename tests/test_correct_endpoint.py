#!/usr/bin/env python3
"""
Test TensorBlock Forge with the correct API endpoint.
"""

import asyncio
import os
from dotenv import load_dotenv
load_dotenv()

print("🔧 Testing correct TensorBlock Forge endpoint...")
print(f"🔑 API Key: {os.getenv('FORGE_API_KEY', 'NOT_SET')[:15]}...")
print()

# Test 1: Quick connection test
try:
    from app.core.forge_client import get_forge_client
    
    print("1️⃣  Testing Forge client initialization...")
    client = get_forge_client()
    print("   ✅ Forge client created successfully")
    
    print("2️⃣  Testing model list...")
    models = client.list_available_models()
    print(f"   ✅ Found {len(models)} available models")
    
    print("3️⃣  Testing model recommendations...")
    fast_model = client.get_recommended_model("fast")
    cost_model = client.get_recommended_model("cost")
    print(f"   ✅ Fast model: {fast_model}")
    print(f"   ✅ Cost model: {cost_model}")
    
except Exception as e:
    print(f"   ❌ Error: {e}")

print()

# Test 2: Simple generation test
async def test_generation():
    try:
        from app.core.forge_llm_service import get_forge_llm_service, LLMRequest
        
        print("4️⃣  Testing LLM generation...")
        service = get_forge_llm_service()
        
        # Use OpenAI model first (most likely to work)
        request = LLMRequest(
            user_prompt="Say hello in exactly 3 words",
            model="OpenAI/gpt-4o-mini"  # Start with OpenAI
        )
        
        print("   🔄 Generating response...")
        response = await service.generate(request)
        
        print("   ✅ Generation successful!")
        print(f"      Model: {response.model}")
        print(f"      Response: {response.text}")
        print(f"      Cost: ${response.cost_estimate:.6f}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Generation failed: {e}")
        return False

# Test 3: Try different models
async def test_different_models():
    try:
        from app.core.forge_llm_service import get_forge_llm_service, LLMRequest
        
        print("5️⃣  Testing different provider models...")
        service = get_forge_llm_service()
        
        models_to_test = [
            "OpenAI/gpt-4o-mini",           # OpenAI
            "Gemini/models/gemini-1.5-flash", # Google  
            "Deepseek/deepseek-chat",       # Deepseek
        ]
        
        for model in models_to_test:
            try:
                request = LLMRequest(
                    user_prompt="Hi!",
                    model=model
                )
                response = await service.generate(request)
                print(f"   ✅ {model}: {response.text[:50]}...")
            except Exception as e:
                print(f"   ❌ {model}: {str(e)[:100]}")
    
    except Exception as e:
        print(f"   ❌ Multi-model test failed: {e}")

async def main():
    success = await test_generation()
    if success:
        await test_different_models()
        print("\n🎉 TensorBlock Forge is working! Migration successful!")
    else:
        print("\n⚠️  Still having issues. Check API key or contact TensorBlock support.")

if __name__ == "__main__":
    asyncio.run(main())