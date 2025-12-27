#!/usr/bin/env python3
"""
Test backend connectivity and upload one file
"""

import requests
import json

BASE_URL = "http://localhost:8000"

# Test 1: Health check
print("🔍 Testing backend health...")
try:
    resp = requests.get(f"{BASE_URL}/api/v1/system/health", timeout=5)
    if resp.status_code == 200:
        print(f"   ✅ Health check: {resp.json()}")
    else:
        print(f"   ❌ Health check failed: {resp.status_code}")
except Exception as e:
    print(f"   ❌ Cannot connect to backend: {e}")
    exit(1)

# Test 2: Upload calls
print("\n📤 Testing data upload...")
try:
    with open("data/sample_calls.csv", "rb") as f:
        files = {"file": f}
        params = {"file_type": "calls"}
        resp = requests.post(
            f"{BASE_URL}/api/v1/data/upload",
            files=files,
            params=params,
            timeout=30
        )
    
    if resp.status_code == 200:
        result = resp.json()
        print(f"   ✅ Upload successful!")
        print(f"      Status: {result.get('status')}")
        if result.get('ingestion_result'):
            ing = result['ingestion_result']
            print(f"      Inserted: {ing.get('inserted')}, Errors: {ing.get('errors')}")
    else:
        print(f"   ❌ Upload failed: {resp.status_code}")
        print(f"      {resp.text[:200]}")
except Exception as e:
    print(f"   ❌ Upload error: {e}")

# Test 3: Get graph stats
print("\n📊 Testing graph stats...")
try:
    resp = requests.get(f"{BASE_URL}/api/v1/system/graph/stats", timeout=5)
    if resp.status_code == 200:
        stats = resp.json()
        print(f"   ✅ Nodes: {stats.get('total_nodes')}, Relationships: {stats.get('total_relationships')}")
    else:
        print(f"   ❌ Stats failed: {resp.status_code}")
except Exception as e:
    print(f"   ❌ Stats error: {e}")

print("\n✨ Backend test complete!")
