#!/usr/bin/env python3
"""
Test different authentication methods for TensorBlock Forge.
"""

import requests
import os
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv("FORGE_API_KEY")
base_url = "https://api.tensorblock.co"

# Different auth methods to try
auth_methods = [
    {"Authorization": f"Bearer {api_key}"},
    {"Authorization": f"Token {api_key}"},
    {"X-API-Key": api_key},
    {"Forge-API-Key": api_key},
    {"Authorization": f"Forge {api_key}"},
]

endpoints_to_test = [
    f"{base_url}/v1/models",
    f"{base_url}/models", 
    f"{base_url}/api/v1/models",
    f"{base_url}/forge/v1/models",
]

print(f"🔍 Testing authentication methods...")
print(f"🔑 API Key: {api_key[:15]}...")
print()

for endpoint in endpoints_to_test:
    print(f"📡 Testing endpoint: {endpoint}")
    
    for i, headers in enumerate(auth_methods):
        try:
            response = requests.get(endpoint, headers=headers, timeout=10)
            status = response.status_code
            
            if status == 200:
                print(f"  ✅ Method {i+1} SUCCESS: {headers}")
                try:
                    data = response.json()
                    if 'data' in data:
                        print(f"     Found {len(data['data'])} models")
                except:
                    print(f"     Response: {response.text[:100]}")
                break
            elif status == 401:
                print(f"  🔐 Method {i+1} Auth failed: {headers}")
            elif status == 404:
                print(f"  🔍 Method {i+1} Not found: {headers}")
            else:
                print(f"  ❌ Method {i+1} Status {status}: {headers}")
                
        except requests.exceptions.ConnectTimeout:
            print(f"  ⏱️  Method {i+1} Timeout: {headers}")
        except requests.exceptions.ConnectionError as e:
            print(f"  🔌 Method {i+1} Connection error: {str(e)[:50]}")
        except Exception as e:
            print(f"  ❌ Method {i+1} Error: {str(e)[:50]}")
    
    print()

print("💡 If no methods work, the service might:")
print("   - Be in private beta")
print("   - Use a different endpoint")
print("   - Require account activation")
print("   - Have different authentication")