"""Test script for analysis pipeline."""
import pandas as pd
import numpy as np

from core.quality_scorer import QualityScorer
from core.column_profiler import ColumnProfiler
from core.dataset_classifier import DatasetClassifier

# Simulate a diverse dataframe with edge cases
df = pd.DataFrame({
    'id': [1, 2, 3, 4, 5],
    'name': ['Alice', 'Bob', 'Charlie', 'Diana', None],
    'age': [25, 30, 35, 40, 28],
    'amount': [100.5, 200.0, -50.0, 300.0, 150.25],
    'is_active': [True, False, True, True, False],
    'status': [1, 0, 1, 1, 0],  # might be treated as numeric but is boolean-like
    'category': ['A', 'B', 'A', 'C', 'B'],
    'date': pd.to_datetime(['2024-01-01', '2024-02-01', '2024-03-01', '2024-04-01', '2024-05-01'])
})

print('=== Full Analysis Test ===')

print('1. Testing Dataset Classifier...')
classifier = DatasetClassifier(df)
classification = classifier.classify()
print(f'   Classification: {classification.type} ({classification.confidence:.0%})')

print('2. Testing Column Profiler...')
profiler = ColumnProfiler(df)
profiles = profiler.profile_all_columns()
print('   Profiles:', {k: v['type'] for k, v in profiles.items()})

print('3. Testing Quality Scorer...')
scorer = QualityScorer(df, profiles)
report = scorer.assess_quality()
print(f'   Overall score: {report.overall_score:.2f}')
print(f'   Completeness: {report.completeness:.2f}')
print(f'   Validity: {report.validity:.2f}')
print(f'   Consistency: {report.consistency:.2f}')
print(f'   Uniqueness: {report.uniqueness:.2f}')

print('\n=== All tests passed! ===')
