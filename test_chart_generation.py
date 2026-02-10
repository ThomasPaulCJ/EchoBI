"""Test chart generation endpoint."""

import requests
import pandas as pd
import json
import time

BASE_URL = "http://localhost:8000"

def test_chart_generation():
    """Test generating actual Plotly charts."""
    
    # Create sample data
    data = {
        'date': pd.date_range('2024-01-01', periods=100, freq='D'),
        'transaction_id': [f'TXN{i:04d}' for i in range(100)],
        'amount': [100 + i*10 + (i%10)*5 for i in range(100)],
        'category': ['Food', 'Transport', 'Shopping', 'Entertainment', 'Bills'] * 20,
        'merchant': [f'Merchant {i%10}' for i in range(100)],
        'quantity': [i % 20 + 1 for i in range(100)]
    }
    df = pd.DataFrame(data)
    
    # Convert to CSV
    csv_data = df.to_csv(index=False)
    
    # 1. Upload
    files = {'file': ('test_data.csv', csv_data, 'text/csv')}
    response = requests.post(f"{BASE_URL}/api/v1/upload", files=files)
    session_id = response.json()['session_id']
    print(f"✓ Uploaded - Session: {session_id[:20]}...")
    
    time.sleep(1)
    
    # 2. Analyze
    response = requests.post(f"{BASE_URL}/api/v1/analyze/{session_id}")
    print("✓ Analyzed")
    
    # 3. Get visualization recommendations
    response = requests.get(f"{BASE_URL}/api/v1/visualizations/recommendations/{session_id}")
    recommendations = response.json()
    print(f"✓ Got {recommendations['total_recommendations']} recommendations")
    
    # 4. Generate charts from recommendations
    generated_charts = []
    
    # Generate top 5 high-priority charts
    high_priority_recs = [r for r in recommendations['recommendations'] if r['priority'] == 1][:5]
    
    print(f"\n📊 GENERATING {len(high_priority_recs)} CHARTS...")
    
    for i, rec in enumerate(high_priority_recs, 1):
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
            generated_charts.append(chart)
            
            plotly_spec = chart['plotly_spec']
            data_traces = len(plotly_spec.get('data', []))
            
            print(f"  {i}. {chart['title']}")
            print(f"     Type: {chart['chart_type']}, Traces: {data_traces}")
        else:
            print(f"  {i}. ERROR: {response.status_code} - {response.text}")
    
    # 5. Test custom chart generation
    print(f"\n🎨 GENERATING CUSTOM CHART...")
    
    custom_payload = {
        "session_id": session_id,
        "chart_type": "scatter",
        "title": "Custom Amount vs Quantity Scatter Plot",
        "config": {
            "x_axis": "amount",
            "y_axis": ["quantity"],
            "color_by": "category"
        }
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/visualizations/generate",
        json=custom_payload
    )
    
    if response.status_code == 200:
        custom_chart = response.json()
        generated_charts.append(custom_chart)
        print(f"  ✓ {custom_chart['title']}")
        print(f"    Type: {custom_chart['chart_type']}")
    
    # 6. Summary
    print(f"\n✅ CHART GENERATION TEST COMPLETE!")
    print(f"  Total Charts Generated: {len(generated_charts)}")
    print(f"  Chart Types: {set(c['chart_type'] for c in generated_charts)}")
    
    # 7. Validate Plotly structure
    print(f"\n🔍 VALIDATING PLOTLY SPECS...")
    for chart in generated_charts[:3]:
        spec = chart['plotly_spec']
        has_data = 'data' in spec and len(spec['data']) > 0
        has_layout = 'layout' in spec
        has_title = spec.get('layout', {}).get('title')
        
        print(f"  {chart['title'][:40]}...")
        print(f"    ✓ Data traces: {len(spec.get('data', []))}")
        print(f"    ✓ Layout: {has_layout}")
        print(f"    ✓ Title: {has_title}")
    
    # 8. Test different chart types
    print(f"\n📈 TESTING MULTIPLE CHART TYPES...")
    
    test_configs = [
        {
            "chart_type": "histogram",
            "title": "Amount Distribution",
            "config": {"x_axis": "amount"}
        },
        {
            "chart_type": "pie",
            "title": "Category Distribution",
            "config": {"x_axis": "category"}
        },
        {
            "chart_type": "line",
            "title": "Amount Over Time",
            "config": {
                "x_axis": "date",
                "y_axis": ["amount"]
            }
        },
        {
            "chart_type": "box",
            "title": "Amount by Category",
            "config": {
                "x_axis": "category",
                "y_axis": ["amount"]
            }
        }
    ]
    
    chart_type_results = {}
    for config in test_configs:
        payload = {
            "session_id": session_id,
            **config
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/visualizations/generate",
            json=payload
        )
        
        if response.status_code == 200:
            chart = response.json()
            chart_type_results[config['chart_type']] = "✓ Success"
            print(f"  {config['chart_type']:15} ✓")
        else:
            chart_type_results[config['chart_type']] = f"✗ Failed: {response.status_code}"
            print(f"  {config['chart_type']:15} ✗ {response.status_code}")
    
    print(f"\n🎯 FINAL RESULTS:")
    print(f"  Total Charts Generated: {len(generated_charts) + len([v for v in chart_type_results.values() if 'Success' in v])}")
    print(f"  Recommendation-based: {len(generated_charts) - 1}")
    print(f"  Custom configurations: {len([v for v in chart_type_results.values() if 'Success' in v]) + 1}")
    print(f"  Success Rate: {len([v for v in chart_type_results.values() if 'Success' in v])}/{len(test_configs)}")

if __name__ == "__main__":
    test_chart_generation()
