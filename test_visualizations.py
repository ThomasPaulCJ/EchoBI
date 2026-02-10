#!/usr/bin/env python3
"""Test visualization recommendations endpoint"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000/api/v1"

# Upload
with open("/tmp/verify_test.csv", "rb") as f:
    response = requests.post(f"{BASE_URL}/upload", files={"file": f})
    session_id = response.json()["session_id"]
    print(f"✓ Uploaded - Session: {session_id[:20]}...")

# Analyze
response = requests.post(f"{BASE_URL}/analyze/{session_id}")
print(f"✓ Analyzed")

# Get relationships
response = requests.get(f"{BASE_URL}/relationships/{session_id}")
print(f"✓ Relationships detected")

# Get Visualization Recommendations
response = requests.get(f"{BASE_URL}/visualizations/recommendations/{session_id}")
if response.status_code == 200:
    data = response.json()
    print(f"\n✅ VISUALIZATION RECOMMENDATIONS GENERATED!")
    print(f"  Total Recommendations: {data['total_recommendations']}")
    print(f"  High Priority: {data['high_priority_count']}")
    print(f"  Dataset Type: {data['dataset_type']}")
    print(f"\n  Summary by Type: {json.dumps(data['summary']['by_type'], indent=4)}")
    print(f"  Summary by Priority: {json.dumps(data['summary']['by_priority'], indent=4)}")
    
    if data['recommendations']:
        print(f"\n📊 Top 3 Recommendations:")
        for i, rec in enumerate(data['recommendations'][:3], 1):
            print(f"\n  {i}. {rec['title']}")
            print(f"     Type: {rec['chart_type']}")
            print(f"     Priority: {rec['priority']}, Confidence: {rec['confidence']:.2f}")
            print(f"     Description: {rec['description']}")
            print(f"     Use Case: {rec['use_case']}")
else:
    print(f"✗ Failed: {response.status_code}")
    print(response.text)
