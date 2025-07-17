#!/usr/bin/env python3
"""
Test structured output with improved JSON prompting.
"""

import asyncio
import os
from dotenv import load_dotenv
load_dotenv()

from pydantic import BaseModel
from app.core.forge_llm_service import get_forge_llm_service

class TestResponse(BaseModel):
    message: str
    word_count: int

async def test_structured_output():
    print("🧪 Testing improved structured output...")
    
    try:
        service = get_forge_llm_service()
        
        # Test with different models
        models_to_test = [
            "OpenAI/gpt-4o-mini",           # OpenAI should handle JSON well
            "Gemini/models/gemini-1.5-flash-8b",  # Test Gemini with better prompting
        ]
        
        for model in models_to_test:
            try:
                print(f"\n📋 Testing {model}...")
                
                response = await service.generate_structured_output(
                    prompt="Create a greeting message with exactly 5 words",
                    response_model=TestResponse,
                    model=model
                )
                
                print(f"  ✅ SUCCESS!")
                print(f"     Message: {response.message}")
                print(f"     Word count: {response.word_count}")
                
            except Exception as e:
                print(f"  ❌ FAILED: {str(e)[:100]}")
    
    except Exception as e:
        print(f"❌ Test setup failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_structured_output())