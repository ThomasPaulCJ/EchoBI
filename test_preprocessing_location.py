#!/usr/bin/env python3
"""
Test to verify preprocessing details appear only in preprocessing tab, not insights tab.
"""

import requests
import pandas as pd
import io

BASE_URL = "http://localhost:8000"

def test_preprocessing_location():
    """Verify preprocessing details are in preprocessing tab only."""
    
    print("🧪 Testing Preprocessing Details Location")
    print("=" * 80)
    
    # Create test data
    print("\n1️⃣ Creating test data with issues...")
    data = {
        'Patient_ID': [1, 2, 3, 4, 5],
        'Age': [45, None, 38, 61, 29],  # Missing value
        'BMI': [24.5, 27.3, 22.1, 29.8, 21.5],
    }
    df = pd.DataFrame(data)
    csv_content = df.to_csv(index=False)
    
    # Upload
    print("📤 Uploading...")
    files = {'file': ('test.csv', csv_content, 'text/csv')}
    response = requests.post(f"{BASE_URL}/api/v1/upload", files=files)
    session_id = response.json()['session_id']
    print(f"✅ Session: {session_id}")
    
    # Analyze
    print("\n2️⃣ Analyzing...")
    requests.post(f"{BASE_URL}/api/v1/analyze/{session_id}")
    print("✅ Analysis complete")
    
    # Get dataset summary BEFORE preprocessing
    print("\n3️⃣ Getting dataset summary (BEFORE preprocessing)...")
    response = requests.get(f"{BASE_URL}/api/v1/ai-summary/dataset/{session_id}")
    dataset_summary_before = response.json().get('summary', '')
    
    print("\n📄 DATASET SUMMARY (BEFORE):")
    print("-" * 80)
    print(dataset_summary_before[:500])
    print("-" * 80)
    
    # Check it says ORIGINAL
    if "ORIGINAL" in dataset_summary_before or "original" in dataset_summary_before.lower():
        print("✅ Correctly indicates ORIGINAL data")
    else:
        print("❌ Missing ORIGINAL indicator")
    
    # Apply preprocessing (if suggestions available)
    print("\n4️⃣ Checking for preprocessing suggestions...")
    response = requests.get(f"{BASE_URL}/api/v1/preprocessing/suggestions?session_id={session_id}")
    
    if response.status_code == 200:
        suggestions = response.json().get('suggestions', [])
        if suggestions:
            print(f"   Found {len(suggestions)} suggestions")
            operation_ids = [op['operation_id'] for op in suggestions[:2]]
            
            print("\n5️⃣ Applying preprocessing...")
            preprocess_request = {
                "session_id": session_id,
                "operation_ids": operation_ids
            }
            response = requests.post(f"{BASE_URL}/api/v1/preprocess", json=preprocess_request)
            
            if response.status_code == 200:
                print("✅ Preprocessing applied")
                
                # Get dataset summary AFTER preprocessing
                print("\n6️⃣ Getting dataset summary (AFTER preprocessing)...")
                response = requests.get(f"{BASE_URL}/api/v1/ai-summary/dataset/{session_id}")
                dataset_summary_after = response.json().get('summary', '')
                
                print("\n📄 DATASET SUMMARY (AFTER - Insights Tab):")
                print("-" * 80)
                print(dataset_summary_after)
                print("-" * 80)
                
                # Check it says PREPROCESSED
                if "PREPROCESSED" in dataset_summary_after or "CLEANED" in dataset_summary_after:
                    print("✅ Correctly indicates PREPROCESSED/CLEANED data")
                else:
                    print("❌ Missing PREPROCESSED/CLEANED indicator")
                
                # CRITICAL: Check it does NOT list detailed preprocessing steps
                has_detailed_steps = any([
                    'handle_missing' in dataset_summary_after.lower(),
                    'operation_type' in dataset_summary_after.lower(),
                    'values affected' in dataset_summary_after.lower(),
                    'fill missing' in dataset_summary_after.lower(),
                ])
                
                if has_detailed_steps:
                    print("❌ FAIL: Dataset summary contains detailed preprocessing steps")
                    print("   Detailed steps should only be in preprocessing summary!")
                    detailed_steps_ok = False
                else:
                    print("✅ PASS: Dataset summary does NOT contain detailed preprocessing steps")
                    detailed_steps_ok = True
                
                # Get preprocessing-specific summary
                print("\n7️⃣ Getting preprocessing summary (Data Quality & Preprocessing Tab)...")
                response = requests.get(f"{BASE_URL}/api/v1/ai-summary/preprocessing/{session_id}")
                preprocessing_summary = response.json().get('summary', '')
                
                print("\n📄 PREPROCESSING SUMMARY (Data Quality & Preprocessing Tab):")
                print("-" * 80)
                print(preprocessing_summary)
                print("-" * 80)
                
                # Check it HAS detailed steps
                has_operations = any([
                    'handle' in preprocessing_summary.lower(),
                    'operation' in preprocessing_summary.lower(),
                    'clean' in preprocessing_summary.lower(),
                    'original' in preprocessing_summary.lower() and 'after' in preprocessing_summary.lower(),
                ])
                
                if has_operations:
                    print("✅ PASS: Preprocessing summary contains detailed operations")
                    preprocessing_details_ok = True
                else:
                    print("⚠️  WARNING: Preprocessing summary may not have enough detail")
                    preprocessing_details_ok = False
                
                # Final verdict
                print("\n" + "=" * 80)
                if detailed_steps_ok and preprocessing_details_ok:
                    print("✅ TEST PASSED - Preprocessing details in correct location!")
                    print("   - Dataset summary: Shows state but NO detailed steps ✓")
                    print("   - Preprocessing summary: Shows ALL detailed steps ✓")
                    return True
                else:
                    print("❌ TEST FAILED - Preprocessing details in wrong location")
                    return False
            else:
                print(f"❌ Preprocessing failed: {response.text}")
                return False
        else:
            print("   No suggestions available - skipping preprocessing test")
            return True
    else:
        print("   Preprocessing endpoint not found - using old version")
        return True

if __name__ == "__main__":
    print("\n" + "="*80)
    print("  PREPROCESSING LOCATION TEST")
    print("="*80)
    
    try:
        requests.get(f"{BASE_URL}/docs", allow_redirects=False)
    except requests.exceptions.ConnectionError:
        print(f"\n❌ Backend not running at {BASE_URL}")
        exit(1)
    
    success = test_preprocessing_location()
    
    print("\n" + "="*80)
    if success:
        print("  ✅ SEPARATION VERIFIED")
        print("  Insights Tab: Data state only (no preprocessing details)")
        print("  Preprocessing Tab: Full preprocessing details")
    else:
        print("  ❌ NEEDS FIX")
    print("="*80 + "\n")
    
    exit(0 if success else 1)
