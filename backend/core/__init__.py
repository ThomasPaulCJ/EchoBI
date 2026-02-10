"""Core module exports for EchoBI backend."""

from .column_profiler import ColumnProfiler
from .dataset_classifier import DatasetClassifier, ClassificationResult
from .quality_scorer import QualityScorer, QualityReport
from .relationship_detector import RelationshipDetector, Relationship
from .feature_analyzer import FeatureAnalyzer, Feature
from .preprocessing_engine import PreprocessingEngine, PreprocessingOperation, AuditEntry
from .preprocessing_pipelines import get_pipeline, FinancialPipeline, SalesPipeline, TimeSeriesPipeline, HealthcarePipeline, GenericPipeline
from .statistical_analyzer import StatisticalAnalyzer, StatisticalInsight
from .insight_generator import InsightGenerator, Insight
from .visualization_recommender import VisualizationRecommender, ChartRecommendation, ChartType
from .chart_generator import ChartGenerator

__all__ = [
    'ColumnProfiler',
    'DatasetClassifier',
    'ClassificationResult',
    'QualityScorer',
    'QualityReport',
    'RelationshipDetector',
    'Relationship',
    'FeatureAnalyzer',
    'Feature',
    'PreprocessingEngine',
    'PreprocessingOperation',
    'AuditEntry',
    'get_pipeline',
    'FinancialPipeline',
    'SalesPipeline',
    'TimeSeriesPipeline',
    'HealthcarePipeline',
    'GenericPipeline',
    'StatisticalAnalyzer',
    'StatisticalInsight',
    'InsightGenerator',
    'Insight',
    'VisualizationRecommender',
    'ChartRecommendation',
    'ChartType',
    'ChartGenerator'
]
