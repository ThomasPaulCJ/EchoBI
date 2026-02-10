#!/usr/bin/env python3
"""Test script for preprocessing workflow with before/after comparison."""
import requests

BASE = "http://localhost:8000"

print("=" * 60)
print("PREPROCESSING WORKFLOW TEST")
print("=" * 60)

# Create test file with missing values
with open('/tmp/test.csv', 'w') as f:
    f.write("date,amount,category\n2024-01-01,100,Food\n2024-01-02,,Transport\n2024-01-03,150,\n")

# Step 1: Upload
print("\n1. Upload dataset...")
with open('/tmp/test.csv', 'rb') as f:
    r = requests.post(f"{BASE}/api/v1/upload", files={"file": f})
print(f"   Status: {r.status_code}")
if r.status_code != 200:
    print(f"   ERROR: {r.text}")
    exit(1)
sid = r.json()['session_id']
print(f"   Session: {sid[:20]}...")

# Step 2: Analyze
print("\n2. Analyze dataset...")
r = requests.post(f"{BASE}/api/v1/analyze/{sid}")
print(f"   Status: {r.status_code}")
if r.status_code == 200:
    data = r.json()
    print(f"   Type: {data.get('classification',{}).get('type')}")
    print(f"   Confidence: {data.get('classification',{}).get('confidence', 0):.0%}")

# Step 3: Get suggestions
print("\n3. Get preprocessing suggestions...")
r = requests.get(f"{BASE}/api/v1/preprocessing/suggestions/{sid}")
print(f"   Status: {r.status_code}")
if r.status_code == 200:
    data = r.json()
    print(f"   Total suggestions: {data.get('total_suggestions')}")
    ops = [s['operation_id'] for s in data.get('suggestions', [])[:3]]
    for s in data.get('suggestions', [])[:3]:
        print(f"   - {s['operation_id']}: {s['operation_type']} on {s.get('column', 'N/A')}")

# Step 4: Get comparison BEFORE preprocessing
print("\n4. Get comparison BEFORE preprocessing...")
r = requests.get(f"{BASE}/api/v1/preprocessing/comparison/{sid}")
print(f"   Status: {r.status_code}")
if r.status_code == 200:
    data = r.json()
    before = data.get('comparison', {}).get('before', {})
    print(f"   Preprocessing applied: {data.get('preprocessing_applied')}")
    print(f"   Before: {before.get('rows')} rows, {before.get('missing_cells')} missing")

# Step 5: Apply preprocessing
print("\n5. Apply preprocessing...")
r = requests.post(f"{BASE}/api/v1/preprocess", json={
    "session_id": sid, 
    "operation_ids": ops, 
    "preview_only": False
})
print(f"   Status: {r.status_code}")
if r.status_code == 200:
    data = r.json()
    print(f"   Operations applied: {data.get('operations_applied')}")
    print(f"   Before shape: {data.get('before_shape')}")
    print(f"   After shape: {data.get('after_shape')}")
    
    # Check comparison in response
    if 'comparison' in data:
        changes = data['comparison'].get('changes', {})
        print(f"   Missing fixed: {changes.get('missing_cells_fixed', 0)}")
    
    # Check audit trail
    trail = data.get('audit_trail', [])
    print(f"   Audit trail entries: {len(trail)}")
    for entry in trail[:3]:
        print(f"     - {entry.get('operation_type')}: {entry.get('values_changed', 0)} values changed")
else:
    print(f"   ERROR: {r.text}")

# Step 6: Get comparison AFTER preprocessing
print("\n6. Get comparison AFTER preprocessing...")
r = requests.get(f"{BASE}/api/v1/preprocessing/comparison/{sid}")
print(f"   Status: {r.status_code}")
if r.status_code == 200:
    data = r.json()
    before = data.get('comparison', {}).get('before', {})
    after = data.get('comparison', {}).get('after', {})
    changes = data.get('comparison', {}).get('changes', {})
    
    print(f"   Preprocessing applied: {data.get('preprocessing_applied')}")
    print(f"   BEFORE: {before.get('rows')} rows, {before.get('missing_cells')} missing, {before.get('duplicate_rows')} duplicates")
    print(f"   AFTER:  {after.get('rows')} rows, {after.get('missing_cells')} missing, {after.get('duplicate_rows')} duplicates")
    print(f"   CHANGES: {changes.get('missing_cells_fixed')} missing fixed")

# Step 7: Get AI summary
print("\n7. Get AI preprocessing summary...")
r = requests.get(f"{BASE}/api/v1/ai-summary/preprocessing/{sid}")
print(f"   Status: {r.status_code}")
if r.status_code == 200:
    data = r.json()
    print(f"   Steps count: {data.get('steps_count')}")
    summary = data.get('summary', 'N/A')
    print(f"\n   AI Summary:")
    print(f"   {summary[:500]}...")

print("\n" + "=" * 60)
print("TEST COMPLETE!")
print("=" * 60)
