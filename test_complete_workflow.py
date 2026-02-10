"""
End-to-End Test for EchoBI v2.0
Tests the complete workflow: Upload → Analysis → Insights → Visualizations
"""

import requests
import pandas as pd
import json
import time

BASE_URL = "http://localhost:8000"

def test_complete_workflow():
    """Test the entire EchoBI v2.0 workflow."""
    
    print("=" * 70)
    print("EchoBI v2.0 - COMPLETE WORKFLOW TEST")
    print("=" * 70)
    print()
    
    # Create comprehensive test dataset
    data = {
        'date': pd.date_range('2024-01-01', periods=200, freq='D'),
        'transaction_id': [f'TXN{i:05d}' for i in range(200)],
        'amount': [1000 + i*50 + (i%30)*100 for i in range(200)],
        'category': ['Food', 'Transport', 'Shopping', 'Entertainment', 'Bills', 'Healthcare'] * 33 + ['Food', 'Transport'],
        'merchant': [f'Merchant {i%15}' for i in range(200)],
        'quantity': [i % 25 + 1 for i in range(200)],
        'customer_id': [f'CUST{i%50:03d}' for i in range(200)],
        'payment_method': ['Credit Card', 'Debit Card', 'Cash', 'Online'] * 50
    }
    df = pd.DataFrame(data)
    csv_data = df.to_csv(index=False)
    
    session_id = None
    test_results = {
        'upload': False,
        'analyze': False,
        'relationships': False,
        'insights': False,
        'visualizations': False,
        'chart_generation': False
    }
    
    try:
        # ===== STEP 1: UPLOAD =====
        print("📤 STEP 1: UPLOAD DATASET")
        print("-" * 70)
        
        files = {'file': ('financial_data.csv', csv_data, 'text/csv')}
        response = requests.post(f"{BASE_URL}/api/v1/upload", files=files)
        
        if response.status_code == 200:
            result = response.json()
            session_id = result['session_id']
            print(f"✅ Upload successful")
            print(f"   Session ID: {session_id[:30]}...")
            print(f"   Status: {result.get('status', 'uploaded')}")
            test_results['upload'] = True
        else:
            print(f"❌ Upload failed: {response.status_code}")
            return test_results
        
        time.sleep(1)
        
        # ===== STEP 2: ANALYZE DATASET =====
        print("\n🔍 STEP 2: ANALYZE DATASET")
        print("-" * 70)
        
        response = requests.post(f"{BASE_URL}/api/v1/analyze/{session_id}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Analysis successful")
            print(f"   Dataset Type: {result.get('classification', {}).get('type', 'Unknown')}")
            print(f"   Confidence: {result.get('classification', {}).get('confidence', 0):.2f}")
            print(f"   Status: {result.get('status', 'analyzed')}")
            test_results['analyze'] = True
        else:
            print(f"❌ Analysis failed: {response.status_code}")
            return test_results
        
        time.sleep(1)
        
        # ===== STEP 3: DETECT RELATIONSHIPS =====
        print("\n🔗 STEP 3: DETECT RELATIONSHIPS")
        print("-" * 70)
        
        response = requests.get(f"{BASE_URL}/api/v1/relationships/{session_id}")
        
        if response.status_code == 200:
            result = response.json()
            relationships = result['relationships']
            print(f"✅ Relationship detection successful")
            print(f"   Total Relationships: {len(relationships)}")
            print(f"   Numeric Correlations: {len([r for r in relationships if r['type'] == 'numeric_correlation'])}")
            print(f"   Keys Detected: {len([r for r in relationships if r['type'] == 'key_foreign_key'])}")
            test_results['relationships'] = True
        else:
            print(f"❌ Relationship detection failed: {response.status_code}")
        
        time.sleep(1)
        
        # ===== STEP 4: GENERATE INSIGHTS =====
        print("\n💡 STEP 4: GENERATE INSIGHTS")
        print("-" * 70)
        
        response = requests.get(f"{BASE_URL}/api/v1/insights/{session_id}?use_ai=false")
        
        if response.status_code == 200:
            result = response.json()
            insights = result['insights']
            recommendations = result['recommendations']
            print(f"✅ Insight generation successful")
            print(f"   Total Insights: {len(insights)}")
            print(f"   High Severity: {result['summary']['by_severity'].get('high', 0)}")
            print(f"   Recommendations: {len(recommendations)}")
            if insights:
                print(f"   Sample Insight: {insights[0]['title'][:50]}...")
            test_results['insights'] = True
        else:
            print(f"❌ Insight generation failed: {response.status_code}")
        
        time.sleep(1)
        
        # ===== STEP 5: GET VISUALIZATION RECOMMENDATIONS =====
        print("\n📊 STEP 5: GET VISUALIZATION RECOMMENDATIONS")
        print("-" * 70)
        
        response = requests.get(f"{BASE_URL}/api/v1/visualizations/recommendations/{session_id}")
        
        if response.status_code == 200:
            result = response.json()
            recommendations = result['recommendations']
            print(f"✅ Visualization recommendations successful")
            print(f"   Total Recommendations: {len(recommendations)}")
            print(f"   High Priority: {result['high_priority_count']}")
            print(f"   Chart Types: {len(result['summary']['by_type'])}")
            print(f"   Top Types: {list(result['summary']['by_type'].keys())[:5]}")
            test_results['visualizations'] = True
            
            # Store recommendations for next step
            top_recommendations = recommendations[:5]
        else:
            print(f"❌ Visualization recommendations failed: {response.status_code}")
            return test_results
        
        time.sleep(1)
        
        # ===== STEP 6: GENERATE CHARTS =====
        print("\n🎨 STEP 6: GENERATE CHARTS")
        print("-" * 70)
        
        charts_generated = 0
        chart_types_generated = set()
        
        for i, rec in enumerate(top_recommendations, 1):
            payload = {
                "session_id": session_id,
                "chart_id": rec['chart_id']
            }
            
            response = requests.post(
                f"{BASE_URL}/api/v1/visualizations/generate",
                json=payload
            )
            
            if response.status_code == 200:
                chart = response.json()
                charts_generated += 1
                chart_types_generated.add(chart['chart_type'])
                print(f"   ✅ Chart {i}: {chart['title'][:40]}... ({chart['chart_type']})")
            else:
                print(f"   ❌ Chart {i} failed: {response.status_code}")
        
        if charts_generated > 0:
            print(f"\n✅ Chart generation successful")
            print(f"   Charts Generated: {charts_generated}/{len(top_recommendations)}")
            print(f"   Chart Types: {', '.join(chart_types_generated)}")
            test_results['chart_generation'] = True
        
        # ===== FINAL SUMMARY =====
        print("\n" + "=" * 70)
        print("WORKFLOW TEST SUMMARY")
        print("=" * 70)
        
        total_tests = len(test_results)
        passed_tests = sum(test_results.values())
        success_rate = (passed_tests / total_tests) * 100
        
        for step, passed in test_results.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"{step.upper():30} {status}")
        
        print("-" * 70)
        print(f"Total: {passed_tests}/{total_tests} tests passed ({success_rate:.0f}%)")
        print("=" * 70)
        
        if passed_tests == total_tests:
            print("\n🎉 ALL TESTS PASSED! EchoBI v2.0 is fully operational!")
        else:
            print(f"\n⚠️  {total_tests - passed_tests} test(s) failed. Please review errors above.")
        
        return test_results
        
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return test_results

if __name__ == "__main__":
    test_complete_workflow()
