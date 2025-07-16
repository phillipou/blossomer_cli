#!/usr/bin/env python3
"""
Test different TensorBlock API endpoints to find the correct one.
"""

import asyncio
import os
from dotenv import load_dotenv
load_dotenv()

import openai

# Possible TensorBlock API endpoints
endpoints_to_try = [
    "https://api.tensorblock.co/v1",
    "https://tensorblock.co/api/v1", 
    "https://forge.tensorblock.co/v1",
    "https://api.tensorblock.ai/v1",
    "https://tensorblock.ai/api/v1",
    "https://api-forge.tensorblock.co/v1",
]

api_key = os.getenv("FORGE_API_KEY")
if not api_key:
    print("❌ FORGE_API_KEY not found")
    exit(1)

print(f"🔍 Testing {len(endpoints_to_try)} potential endpoints...")
print(f"🔑 Using API key: {api_key[:10]}...")
print()

async def test_endpoint(base_url):
    try:
        client = openai.OpenAI(api_key=api_key, base_url=base_url)
        
        # Try to list models first
        try:
            models = client.models.list()
            print(f"✅ {base_url} - SUCCESS!")
            print(f"   Found {len(models.data)} models")
            if len(models.data) > 0:
                print(f"   Sample models: {[m.id for m in models.data[:3]]}")
            return True
        except Exception as e:
            print(f"❌ {base_url} - Model list failed: {str(e)[:100]}")
            return False
            
    except Exception as e:
        print(f"❌ {base_url} - Connection failed: {str(e)[:100]}")
        return False

async def main():
    working_endpoints = []
    
    for endpoint in endpoints_to_try:
        success = await test_endpoint(endpoint)
        if success:
            working_endpoints.append(endpoint)
        await asyncio.sleep(1)  # Be nice to their servers
    
    print(f"\n📋 Results:")
    if working_endpoints:
        print(f"✅ Working endpoints: {working_endpoints}")
        print(f"\n💡 Update your forge_client.py to use: {working_endpoints[0]}")
    else:
        print("❌ No working endpoints found")
        print("\n🤔 Possible issues:")
        print("   - Service might be in beta/private access")
        print("   - API key might need activation") 
        print("   - Different authentication method required")
        print("\n💡 Try contacting TensorBlock support for the correct endpoint")

if __name__ == "__main__":
    asyncio.run(main())