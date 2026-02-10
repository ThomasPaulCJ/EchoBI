#!/usr/bin/env python3
"""Test insights endpoint"""
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

# Get Insights
response = requests.get(f"{BASE_URL}/insights/{session_id}?use_ai=false")
if response.status_code == 200:
    data = response.json()
    print(f"\n✅ INSIGHTS GENERATED!")
    print(f"  Total Insights: {data['summary']['total_insights']}")
    print(f"  By Category: {data['summary']['by_category']}")
    print(f"  By Severity: {data['summary']['by_severity']}")
    print(f"  Recommendations: {data['summary']['recommendations_count']}")
    
    if data['insights']:
        print(f"\n📊 Sample Insight:")
        insight = data['insights'][0]
        print(f"  Title: {insight['title']}")
        print(f"  Category: {insight['category']}")
        print(f"  Severity: {insight['severity']}")
        print(f"  Confidence: {insight['confidence']:.2f}")
        print(f"  Affected Columns: {', '.join(insight['affected_columns'])}")
        
    if data['recommendations']:
        print(f"\n💡 Sample Recommendation:")
        rec = data['recommendations'][0]
        print(f"  Priority: {rec['priority']}")
        print(f"  Category: {rec['category']}")
        print(f"  Title: {rec['title']}")
else:
    print(f"✗ Failed: {response.status_code}")
    print(response.text)
