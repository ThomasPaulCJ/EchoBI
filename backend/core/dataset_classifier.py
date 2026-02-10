"""
DatasetClassifier v2.0 - Robust Multi-Class Dataset Classification

This module implements a hybrid classification system to identify dataset domains:
- Financial (transactions, accounting, banking, investments)
- Sales/Retail (products, customers, orders, e-commerce)
- Time-Series (temporal data with regular intervals, trends)
- Healthcare (medical records, diagnoses, treatments, vitals)
- Marketing (campaigns, leads, conversions, engagement)
- HR/Employee (workforce, payroll, attendance, performance)
- Logistics/Supply Chain (shipping, inventory, warehouses)
- Generic (fallback for unclassified data)

Classification Strategy:
1. Weighted keyword matching with domain-specific importance scores
2. Fuzzy matching for keyword variations and abbreviations
3. Column combination analysis (semantic groups)
4. Value pattern detection (currency, dates, codes)
5. Data type distribution analysis
6. Statistical feature analysis
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass
import re
from collections import Counter


@dataclass
class ClassificationResult:
    """Result of dataset classification."""
    type: str
    confidence: float
    description: str
    features: List[str]
    suggestions: List[str]
    all_scores: Dict[str, float]  # All domain scores for transparency


class DomainPatterns:
    """Domain-specific patterns with weighted keywords and semantic groups."""
    
    # Keyword weight: 1.0 = strong indicator, 0.5 = moderate, 0.3 = weak
    FINANCIAL = {
        'strong_keywords': {
            'transaction': 1.0, 'account': 1.0, 'balance': 1.0, 'debit': 1.0, 'credit': 1.0,
            'ledger': 1.0, 'invoice': 1.0, 'payment': 1.0, 'revenue': 1.0, 'expense': 1.0,
            'profit': 1.0, 'loss': 1.0, 'fiscal': 1.0, 'budget': 1.0, 'equity': 1.0,
            'liability': 1.0, 'asset': 1.0, 'capital': 1.0, 'dividend': 1.0, 'interest': 1.0,
            'loan': 1.0, 'mortgage': 1.0, 'deposit': 1.0, 'withdrawal': 1.0, 'transfer': 1.0,
            'bank': 0.9, 'finance': 0.9, 'financial': 0.9, 'accounting': 0.9,
        },
        'moderate_keywords': {
            'amount': 0.7, 'total': 0.6, 'price': 0.5, 'cost': 0.5, 'fee': 0.7,
            'charge': 0.6, 'tax': 0.7, 'vat': 0.8, 'gst': 0.8, 'currency': 0.8,
            'rate': 0.4, 'exchange': 0.7, 'forex': 0.9, 'usd': 0.8, 'eur': 0.8,
            'gbp': 0.8, 'inr': 0.8, 'net': 0.4, 'gross': 0.5, 'margin': 0.6,
        },
        'weak_keywords': {
            'value': 0.3, 'money': 0.4, 'fund': 0.4, 'cash': 0.5, 'check': 0.4,
            'cheque': 0.5, 'card': 0.3, 'receipt': 0.5, 'statement': 0.4,
        },
        'abbreviations': {
            'amt': 'amount', 'txn': 'transaction', 'acct': 'account', 'bal': 'balance',
            'acc': 'account', 'trx': 'transaction', 'cr': 'credit', 'dr': 'debit',
            'inv': 'invoice', 'pmt': 'payment', 'rev': 'revenue', 'exp': 'expense',
        },
        'value_patterns': [
            r'^\$[\d,]+\.?\d*$',  # $1,234.56
            r'^[\d,]+\.?\d*\s*(USD|EUR|GBP|JPY|INR|CAD|AUD)$',  # 1234.56 USD
            r'^(USD|EUR|GBP|JPY|INR|CAD|AUD)\s*[\d,]+\.?\d*$',  # USD 1234.56
            r'^\(?[\d,]+\.?\d*\)?$',  # Accounting format (1,234.56)
        ],
    }
    
    SALES = {
        'strong_keywords': {
            'product': 1.0, 'customer': 1.0, 'order': 1.0, 'purchase': 1.0, 'sale': 1.0,
            'sales': 1.0, 'sku': 1.0, 'inventory': 1.0, 'cart': 1.0, 'checkout': 1.0,
            'ecommerce': 1.0, 'retail': 1.0, 'wholesale': 1.0, 'merchant': 1.0,
            'store': 0.8, 'shop': 0.8, 'buyer': 0.9, 'seller': 0.9, 'vendor': 0.8,
        },
        'moderate_keywords': {
            'item': 0.6, 'quantity': 0.7, 'qty': 0.7, 'shipping': 0.7, 'delivery': 0.6,
            'discount': 0.7, 'promotion': 0.7, 'coupon': 0.8, 'promo': 0.7, 'category': 0.5,
            'brand': 0.6, 'supplier': 0.7, 'warehouse': 0.6, 'stock': 0.6, 'unit': 0.4,
            'order_id': 1.0, 'orderid': 1.0, 'order_number': 1.0, 'customer_id': 0.9,
        },
        'weak_keywords': {
            'name': 0.2, 'description': 0.2, 'size': 0.3, 'color': 0.3, 'weight': 0.3,
            'manufacturer': 0.4, 'model': 0.3, 'refund': 0.5, 'return': 0.4,
        },
        'abbreviations': {
            'qty': 'quantity', 'prod': 'product', 'cust': 'customer', 'ord': 'order',
            'inv': 'inventory', 'cat': 'category', 'desc': 'description',
        },
    }
    
    TIMESERIES = {
        'strong_keywords': {
            'timestamp': 1.0, 'datetime': 1.0, 'date_time': 1.0, 'time_series': 1.0,
            'timeseries': 1.0, 'trend': 0.9, 'forecast': 1.0, 'seasonal': 1.0,
            'period': 0.8, 'interval': 0.8, 'frequency': 0.8, 'cycle': 0.7,
            'lag': 0.9, 'rolling': 0.9, 'moving_average': 1.0, 'ma': 0.7,
        },
        'moderate_keywords': {
            'date': 0.7, 'time': 0.5, 'year': 0.6, 'month': 0.6, 'day': 0.5,
            'hour': 0.6, 'minute': 0.5, 'second': 0.4, 'week': 0.6, 'quarter': 0.7,
            'duration': 0.5, 'epoch': 0.8, 'utc': 0.7, 'timezone': 0.7,
        },
        'weak_keywords': {
            'created': 0.3, 'updated': 0.3, 'modified': 0.3, 'start': 0.3, 'end': 0.3,
        },
        'abbreviations': {
            'ts': 'timestamp', 'dt': 'datetime', 'yr': 'year', 'mo': 'month',
            'hr': 'hour', 'min': 'minute', 'sec': 'second',
        },
    }
    
    HEALTHCARE = {
        'strong_keywords': {
            'patient': 1.0, 'diagnosis': 1.0, 'treatment': 1.0, 'prescription': 1.0,
            'medication': 1.0, 'drug': 0.9, 'symptom': 1.0, 'condition': 0.8,
            'disease': 1.0, 'doctor': 1.0, 'physician': 1.0, 'hospital': 1.0,
            'clinic': 0.9, 'medical': 1.0, 'health': 0.8, 'healthcare': 1.0,
            'clinical': 1.0, 'surgical': 1.0, 'procedure': 0.8, 'surgery': 1.0,
            'admission': 0.9, 'discharge': 0.9, 'icd': 1.0, 'cpt': 1.0, 'ndc': 1.0,
            'ehr': 1.0, 'emr': 1.0, 'hipaa': 1.0,
        },
        'moderate_keywords': {
            'vital': 0.8, 'blood': 0.7, 'pressure': 0.5, 'heart': 0.6, 'rate': 0.3,
            'temperature': 0.5, 'lab': 0.6, 'test': 0.3, 'result': 0.3, 'bmi': 0.8,
            'pulse': 0.8, 'oxygen': 0.8, 'saturation': 0.7, 'respiratory': 0.9,
            'insurance': 0.5, 'claim': 0.4, 'provider': 0.5, 'nurse': 0.8,
        },
        'weak_keywords': {
            'age': 0.3, 'gender': 0.3, 'dob': 0.4, 'birth': 0.3, 'weight': 0.3,
            'height': 0.3, 'allergy': 0.6, 'emergency': 0.5,
        },
        'abbreviations': {
            'pt': 'patient', 'dx': 'diagnosis', 'rx': 'prescription', 'tx': 'treatment',
            'hx': 'history', 'bp': 'blood_pressure', 'hr': 'heart_rate', 'spo2': 'oxygen',
            'bpm': 'beats_per_minute', 'mg': 'milligram', 'ml': 'milliliter',
        },
        'code_patterns': [
            r'^[A-Z]\d{2}(\.\d{1,2})?$',  # ICD-10 codes like A01.1
            r'^\d{5}$',  # CPT codes (5 digits)
            r'^\d{11}$',  # NDC codes (11 digits)
        ],
    }
    
    MARKETING = {
        'strong_keywords': {
            'campaign': 1.0, 'lead': 1.0, 'conversion': 1.0, 'click': 0.9, 'impression': 1.0,
            'ctr': 1.0, 'roi': 0.9, 'engagement': 1.0, 'bounce': 0.9, 'subscriber': 0.9,
            'email': 0.7, 'newsletter': 0.9, 'advertisement': 1.0, 'ad': 0.6, 'ads': 0.7,
            'channel': 0.6, 'audience': 0.8, 'segment': 0.6, 'funnel': 1.0,
            'acquisition': 0.8, 'retention': 0.8, 'churn': 0.9, 'ltv': 1.0,
        },
        'moderate_keywords': {
            'open_rate': 1.0, 'click_rate': 1.0, 'view': 0.4, 'reach': 0.6, 'follower': 0.7,
            'like': 0.4, 'share': 0.4, 'comment': 0.4, 'social': 0.5, 'media': 0.4,
            'seo': 0.9, 'sem': 0.9, 'ppc': 1.0, 'cpc': 1.0, 'cpm': 1.0, 'cpa': 1.0,
        },
        'abbreviations': {
            'ctr': 'click_through_rate', 'roi': 'return_on_investment',
            'cpc': 'cost_per_click', 'cpm': 'cost_per_mille', 'cpa': 'cost_per_acquisition',
        },
    }
    
    HR = {
        'strong_keywords': {
            'employee': 1.0, 'salary': 1.0, 'payroll': 1.0, 'attendance': 1.0,
            'leave': 0.8, 'vacation': 0.8, 'pto': 1.0, 'hire': 0.9, 'termination': 1.0,
            'department': 0.7, 'manager': 0.6, 'performance': 0.7, 'appraisal': 1.0,
            'bonus': 0.8, 'compensation': 1.0, 'benefits': 0.8, 'headcount': 1.0,
            'recruitment': 1.0, 'onboarding': 1.0, 'workforce': 1.0,
        },
        'moderate_keywords': {
            'staff': 0.6, 'worker': 0.5, 'job': 0.4, 'position': 0.5, 'title': 0.4,
            'team': 0.4, 'shift': 0.6, 'overtime': 0.8, 'hours': 0.4, 'worked': 0.5,
            'training': 0.5, 'skill': 0.4, 'experience': 0.3, 'tenure': 0.7,
        },
        'abbreviations': {
            'emp': 'employee', 'dept': 'department', 'mgr': 'manager',
            'pto': 'paid_time_off', 'ot': 'overtime', 'fy': 'fiscal_year',
        },
    }
    
    LOGISTICS = {
        'strong_keywords': {
            'shipment': 1.0, 'shipping': 0.9, 'tracking': 0.9, 'carrier': 1.0,
            'freight': 1.0, 'logistics': 1.0, 'warehouse': 0.9, 'fulfillment': 1.0,
            'dispatch': 1.0, 'delivery': 0.8, 'route': 0.7, 'fleet': 1.0,
            'container': 0.9, 'pallet': 1.0, 'consignment': 1.0, 'manifest': 1.0,
        },
        'moderate_keywords': {
            'origin': 0.6, 'destination': 0.7, 'pickup': 0.6, 'dropoff': 0.6,
            'eta': 0.8, 'transit': 0.7, 'inbound': 0.7, 'outbound': 0.7,
            'weight': 0.4, 'dimension': 0.5, 'volume': 0.4, 'package': 0.5,
        },
        'abbreviations': {
            'eta': 'estimated_arrival', 'awb': 'airway_bill', 'bol': 'bill_of_lading',
            'wh': 'warehouse', 'dc': 'distribution_center', 'po': 'purchase_order',
        },
    }


class DatasetClassifier:
    """
    Robust multi-class dataset classifier using hybrid approach.
    
    Classification is performed using:
    1. Weighted keyword scoring (strong > moderate > weak)
    2. Abbreviation expansion and fuzzy matching
    3. Column combination analysis (semantic groups)
    4. Value pattern detection
    5. Data type distribution analysis
    """
    
    # Minimum threshold to classify as a specific domain
    MIN_CONFIDENCE_THRESHOLD = 0.30
    
    # Domain weights for tie-breaking (based on specificity)
    DOMAIN_SPECIFICITY = {
        'Healthcare': 1.2,  # Medical terms are highly specific
        'HR': 1.1,
        'Logistics': 1.1,
        'Marketing': 1.0,
        'Financial': 1.0,
        'Sales': 0.95,  # Sales terms overlap with financial
        'Time-Series': 0.9,  # Time columns present in many domains
        'Generic': 0.5,
    }
    
    def __init__(self, df: pd.DataFrame):
        """Initialize classifier with a dataframe."""
        self.df = df
        self.columns = list(df.columns)
        self.column_names_lower = [self._normalize_column_name(col) for col in df.columns]
        self.column_name_set = set(self.column_names_lower)
        self._sample_values = self._extract_sample_values()
    
    def _normalize_column_name(self, name: str) -> str:
        """Normalize column name for matching."""
        # Convert to lowercase, replace separators with underscores
        name = str(name).lower()
        name = re.sub(r'[\s\-\.]', '_', name)
        name = re.sub(r'[^a-z0-9_]', '', name)
        return name
    
    def _extract_sample_values(self) -> Dict[str, List]:
        """Extract sample values from each column for pattern analysis."""
        samples = {}
        for col in self.df.columns:
            try:
                non_null = self.df[col].dropna()
                if len(non_null) > 0:
                    samples[col] = non_null.head(100).astype(str).tolist()
            except:
                samples[col] = []
        return samples
    
    def classify(self) -> ClassificationResult:
        """Classify the dataset into a domain type."""
        # Calculate scores for each domain
        scores = {
            'Financial': self._score_domain(DomainPatterns.FINANCIAL, 'Financial'),
            'Sales': self._score_domain(DomainPatterns.SALES, 'Sales'),
            'Time-Series': self._score_timeseries(),
            'Healthcare': self._score_domain(DomainPatterns.HEALTHCARE, 'Healthcare'),
            'Marketing': self._score_domain(DomainPatterns.MARKETING, 'Marketing'),
            'HR': self._score_domain(DomainPatterns.HR, 'HR'),
            'Logistics': self._score_domain(DomainPatterns.LOGISTICS, 'Logistics'),
        }
        
        # Apply domain specificity weights
        weighted_scores = {
            domain: score * self.DOMAIN_SPECIFICITY.get(domain, 1.0)
            for domain, score in scores.items()
        }
        
        # Get the highest scoring domain
        best_domain = max(weighted_scores, key=weighted_scores.get)
        best_score = scores[best_domain]  # Use unweighted for confidence
        
        # Require minimum confidence threshold
        if best_score < self.MIN_CONFIDENCE_THRESHOLD:
            return self._create_classification('Generic', 0.5, scores)
        
        # Cap confidence at 0.95 (leave room for user correction)
        confidence = min(best_score, 0.95)
        
        return self._create_classification(best_domain, confidence, scores)
    
    def _score_domain(self, patterns: dict, domain_name: str) -> float:
        """Calculate domain score using weighted keyword matching."""
        total_score = 0.0
        max_possible = 0.0
        matches = []
        
        # Combine all keywords with their weights
        all_keywords = {}
        all_keywords.update(patterns.get('strong_keywords', {}))
        all_keywords.update(patterns.get('moderate_keywords', {}))
        all_keywords.update(patterns.get('weak_keywords', {}))
        
        # Get abbreviation expansions
        abbreviations = patterns.get('abbreviations', {})
        
        # Check each column name against keywords
        for col_name in self.column_names_lower:
            # Direct keyword matching
            matched = False
            for keyword, weight in all_keywords.items():
                keyword_normalized = self._normalize_column_name(keyword)
                
                # Exact match (column contains keyword as a word)
                if self._keyword_in_column(keyword_normalized, col_name):
                    total_score += weight
                    matches.append((col_name, keyword, weight, 'direct'))
                    max_possible += weight
                    matched = True
                    break
            
            if not matched:
                # Check abbreviations
                for abbrev, full_word in abbreviations.items():
                    if self._keyword_in_column(abbrev, col_name):
                        # Get weight of the full word
                        weight = all_keywords.get(full_word, 0.5)
                        total_score += weight * 0.8  # Slight penalty for abbreviation
                        matches.append((col_name, abbrev, weight * 0.8, 'abbreviation'))
                        max_possible += weight * 0.8
                        break
        
        # Value pattern matching (for domains with specific value patterns)
        if 'value_patterns' in patterns:
            pattern_score = self._score_value_patterns(patterns['value_patterns'])
            total_score += pattern_score * 0.3  # Value patterns add up to 0.3
            if pattern_score > 0:
                max_possible += 0.3
        
        if 'code_patterns' in patterns:
            code_score = self._score_value_patterns(patterns['code_patterns'])
            total_score += code_score * 0.4  # Code patterns are strong indicators
            if code_score > 0:
                max_possible += 0.4
        
        # Semantic combination bonus
        combination_bonus = self._score_semantic_combinations(domain_name)
        total_score += combination_bonus
        
        # Normalize score (0 to 1)
        if max_possible > 0:
            # Use log scaling for better distribution
            raw_score = total_score / max(len(self.columns), 1)
            # Apply sigmoid-like normalization
            normalized = min(raw_score * 2, 1.0)
            return normalized
        
        return 0.0
    
    def _keyword_in_column(self, keyword: str, column_name: str) -> bool:
        """Check if keyword appears as a word (or word part) in column name."""
        # Exact word boundary match
        if re.search(rf'\b{re.escape(keyword)}\b', column_name):
            return True
        
        # Substring match for compound words (e.g., 'transaction_id' contains 'transaction')
        if keyword in column_name.split('_'):
            return True
        
        # Fuzzy match for common variations
        if len(keyword) >= 4 and keyword in column_name:
            return True
        
        return False
    
    def _score_value_patterns(self, patterns: List[str]) -> float:
        """Score based on value pattern matching."""
        total_matches = 0
        total_checked = 0
        
        for col, values in self._sample_values.items():
            if not values:
                continue
                
            matches = 0
            for value in values[:20]:  # Check first 20 values
                for pattern in patterns:
                    if re.match(pattern, str(value).strip(), re.IGNORECASE):
                        matches += 1
                        break
            
            if matches > 0:
                total_matches += matches / len(values[:20])
                total_checked += 1
        
        if total_checked > 0:
            return total_matches / total_checked
        return 0.0
    
    def _score_semantic_combinations(self, domain: str) -> float:
        """Score bonus for semantic column combinations."""
        bonus = 0.0
        col_set = ' '.join(self.column_names_lower)
        
        if domain == 'Financial':
            # Financial patterns: amount + account, transaction + date, balance + account
            has_amount = any(kw in col_set for kw in ['amount', 'amt', 'balance', 'total', 'price', 'cost', 'revenue', 'expense'])
            has_account = any(kw in col_set for kw in ['account', 'acct', 'acc'])
            has_transaction = any(kw in col_set for kw in ['transaction', 'txn', 'trx', 'payment', 'transfer'])
            has_date = any(kw in col_set for kw in ['date', 'time', 'timestamp'])
            has_type = any(kw in col_set for kw in ['type', 'category', 'credit', 'debit'])
            has_balance = any(kw in col_set for kw in ['balance', 'bal'])
            
            if has_amount and has_transaction:
                bonus += 0.25
            if has_account and (has_amount or has_balance):
                bonus += 0.2
            if has_transaction and has_date:
                bonus += 0.15
            if has_type and has_amount:
                bonus += 0.1
                
        elif domain == 'Sales':
            has_product = any(kw in col_set for kw in ['product', 'item', 'sku', 'prod'])
            has_customer = any(kw in col_set for kw in ['customer', 'cust', 'buyer', 'client'])
            has_order = any(kw in col_set for kw in ['order', 'purchase', 'sale'])
            has_quantity = any(kw in col_set for kw in ['quantity', 'qty', 'count', 'units'])
            has_price = any(kw in col_set for kw in ['price', 'amount', 'total', 'revenue'])
            
            if has_product and has_customer:
                bonus += 0.2
            if has_order and has_quantity:
                bonus += 0.2
            if has_product and has_price:
                bonus += 0.15
                
        elif domain == 'Healthcare':
            has_patient = any(kw in col_set for kw in ['patient', 'pt', 'person', 'subject'])
            has_medical = any(kw in col_set for kw in ['diagnosis', 'dx', 'treatment', 'tx', 'medication', 'rx', 'symptom', 'condition'])
            has_vitals = any(kw in col_set for kw in ['blood', 'pressure', 'heart', 'pulse', 'temperature', 'bp', 'hr'])
            has_provider = any(kw in col_set for kw in ['doctor', 'physician', 'provider', 'nurse', 'hospital', 'clinic'])
            
            if has_patient and has_medical:
                bonus += 0.3
            if has_patient and has_vitals:
                bonus += 0.2
            if has_provider and has_patient:
                bonus += 0.15
                
        elif domain == 'HR':
            has_employee = any(kw in col_set for kw in ['employee', 'emp', 'staff', 'worker'])
            has_salary = any(kw in col_set for kw in ['salary', 'payroll', 'compensation', 'wage'])
            has_department = any(kw in col_set for kw in ['department', 'dept', 'team', 'division'])
            has_time = any(kw in col_set for kw in ['attendance', 'leave', 'hours', 'shift'])
            
            if has_employee and has_salary:
                bonus += 0.25
            if has_employee and has_department:
                bonus += 0.15
            if has_employee and has_time:
                bonus += 0.15
                
        elif domain == 'Marketing':
            has_campaign = any(kw in col_set for kw in ['campaign', 'ad', 'advertisement'])
            has_metrics = any(kw in col_set for kw in ['click', 'impression', 'conversion', 'ctr', 'engagement'])
            has_channel = any(kw in col_set for kw in ['channel', 'source', 'medium', 'platform'])
            
            if has_campaign and has_metrics:
                bonus += 0.25
            if has_metrics and has_channel:
                bonus += 0.15
                
        elif domain == 'Logistics':
            has_shipment = any(kw in col_set for kw in ['shipment', 'shipping', 'freight', 'tracking'])
            has_location = any(kw in col_set for kw in ['origin', 'destination', 'warehouse', 'location'])
            has_carrier = any(kw in col_set for kw in ['carrier', 'vehicle', 'fleet', 'driver'])
            
            if has_shipment and has_location:
                bonus += 0.25
            if has_shipment and has_carrier:
                bonus += 0.2
        
        return min(bonus, 0.5)  # Cap bonus at 0.5
    
    def _score_timeseries(self) -> float:
        """Calculate time-series domain score with special datetime detection."""
        score = 0.0
        datetime_cols = []
        
        # Check for datetime columns
        for col in self.df.columns:
            col_lower = col.lower()
            
            # Check if column is datetime type
            if pd.api.types.is_datetime64_any_dtype(self.df[col]):
                datetime_cols.append(col)
                score += 0.3
                continue
            
            # Check if column name suggests datetime
            if any(kw in col_lower for kw in ['date', 'time', 'timestamp', 'datetime']):
                # Try to parse as datetime
                try:
                    sample = self.df[col].dropna().head(50)
                    if len(sample) > 0:
                        pd.to_datetime(sample)
                        datetime_cols.append(col)
                        score += 0.25
                except:
                    pass
        
        # Keyword matching
        keywords = DomainPatterns.TIMESERIES
        keyword_score = 0
        for col_name in self.column_names_lower:
            for keyword, weight in {**keywords.get('strong_keywords', {}), **keywords.get('moderate_keywords', {})}.items():
                if self._keyword_in_column(keyword, col_name):
                    keyword_score += weight
                    break
        
        score += min(keyword_score / max(len(self.columns), 1), 0.4)
        
        # Check for regular intervals (strong indicator)
        if datetime_cols:
            for col in datetime_cols[:2]:
                try:
                    dates = pd.to_datetime(self.df[col].dropna()).sort_values()
                    if len(dates) > 10:
                        diffs = dates.diff().dropna()
                        if len(diffs) > 0 and diffs.mean() > pd.Timedelta(0):
                            std_ratio = diffs.std() / diffs.mean()
                            if std_ratio < 0.3:  # Very regular intervals
                                score += 0.3
                            elif std_ratio < 0.6:
                                score += 0.15
                except:
                    pass
        
        return min(score, 1.0)
    
    def _create_classification(self, domain: str, confidence: float, all_scores: Dict[str, float]) -> ClassificationResult:
        """Create classification result with features and suggestions."""
        
        # Domain-specific descriptions and suggestions
        domain_info = {
            'Financial': {
                'description': "This dataset contains financial/accounting data with monetary values, transactions, and financial metrics.",
                'suggestions': [
                    "Apply currency normalization and formatting",
                    "Validate account numbers and transaction IDs",
                    "Check for fraudulent patterns and anomalies",
                    "Calculate financial ratios and metrics",
                    "Handle missing amounts with domain-appropriate methods"
                ]
            },
            'Sales': {
                'description': "This dataset contains sales/retail data with products, customers, orders, and transaction details.",
                'suggestions': [
                    "Standardize product names and SKUs",
                    "Calculate customer lifetime value (CLV)",
                    "Detect seasonal patterns in sales",
                    "Perform RFM (Recency, Frequency, Monetary) analysis",
                    "Identify top products and customer segments"
                ]
            },
            'Time-Series': {
                'description': "This dataset contains temporal data with time-based patterns suitable for trend analysis and forecasting.",
                'suggestions': [
                    "Ensure datetime columns are properly parsed",
                    "Check for and handle gaps in time series",
                    "Resample to regular intervals if needed",
                    "Detect trends and seasonal patterns",
                    "Create lag features for time-based analysis"
                ]
            },
            'Healthcare': {
                'description': "This dataset contains healthcare/medical data with patient information, diagnoses, or clinical records.",
                'suggestions': [
                    "Ensure patient data is properly anonymized (HIPAA)",
                    "Validate medical codes (ICD, CPT, NDC)",
                    "Handle missing clinical data appropriately",
                    "Check for outliers in vital signs and lab values",
                    "Consider temporal patterns in treatments and outcomes"
                ]
            },
            'Marketing': {
                'description': "This dataset contains marketing/advertising data with campaigns, engagement metrics, and conversion data.",
                'suggestions': [
                    "Calculate key marketing KPIs (CTR, conversion rate, ROI)",
                    "Segment by channel and campaign performance",
                    "Analyze customer acquisition and retention",
                    "Identify high-performing campaigns and content",
                    "Track funnel metrics and drop-off points"
                ]
            },
            'HR': {
                'description': "This dataset contains HR/workforce data with employee information, compensation, and attendance records.",
                'suggestions': [
                    "Ensure sensitive employee data is protected",
                    "Calculate workforce metrics (turnover, headcount)",
                    "Analyze compensation distribution and equity",
                    "Track attendance and leave patterns",
                    "Identify performance trends by department"
                ]
            },
            'Logistics': {
                'description': "This dataset contains logistics/supply chain data with shipments, inventory, and delivery information.",
                'suggestions': [
                    "Calculate delivery time and transit metrics",
                    "Analyze route efficiency and carrier performance",
                    "Track inventory levels and stockouts",
                    "Identify shipping delays and bottlenecks",
                    "Optimize warehouse and fulfillment operations"
                ]
            },
            'Generic': {
                'description': "This dataset does not strongly match any specific domain. Generic analysis and preprocessing will be applied.",
                'suggestions': [
                    "Apply standard data cleaning (nulls, duplicates)",
                    "Validate data types and value ranges",
                    "Check for outliers using statistical methods",
                    "Examine column correlations and relationships",
                    "Consider manual domain specification if pattern is known"
                ]
            }
        }
        
        info = domain_info.get(domain, domain_info['Generic'])
        
        # Identify detected features
        features = self._identify_features(domain)
        
        return ClassificationResult(
            type=domain,
            confidence=confidence,
            description=info['description'],
            features=features,
            suggestions=info['suggestions'],
            all_scores=all_scores
        )
    
    def _identify_features(self, domain: str) -> List[str]:
        """Identify which features led to the classification."""
        features = []
        col_set = ' '.join(self.column_names_lower)
        
        # Add column count
        features.append(f"{len(self.columns)} columns detected")
        features.append(f"{len(self.df)} rows in dataset")
        
        # Add numeric column info
        numeric_cols = len([col for col in self.df.columns if pd.api.types.is_numeric_dtype(self.df[col])])
        if numeric_cols > 0:
            features.append(f"{numeric_cols} numeric columns")
        
        # Domain-specific features
        if domain == 'Financial':
            if any(kw in col_set for kw in ['transaction', 'txn', 'payment']):
                features.append("Transaction/payment columns detected")
            if any(kw in col_set for kw in ['amount', 'balance', 'total']):
                features.append("Monetary value columns present")
            if any(kw in col_set for kw in ['account', 'acct']):
                features.append("Account information found")
                
        elif domain == 'Sales':
            if any(kw in col_set for kw in ['product', 'item', 'sku']):
                features.append("Product/item columns detected")
            if any(kw in col_set for kw in ['customer', 'buyer']):
                features.append("Customer information present")
            if any(kw in col_set for kw in ['order', 'quantity']):
                features.append("Order/quantity metrics found")
                
        elif domain == 'Healthcare':
            if any(kw in col_set for kw in ['patient', 'person']):
                features.append("Patient identifiers detected")
            if any(kw in col_set for kw in ['diagnosis', 'treatment', 'medication']):
                features.append("Medical/clinical columns present")
                
        elif domain == 'Time-Series':
            datetime_cols = [col for col in self.df.columns 
                           if pd.api.types.is_datetime64_any_dtype(self.df[col]) or 'date' in col.lower()]
            if datetime_cols:
                features.append(f"Temporal columns: {', '.join(datetime_cols[:3])}")
            features.append("Time-based patterns detected")
            
        elif domain == 'Marketing':
            if any(kw in col_set for kw in ['campaign', 'ad']):
                features.append("Campaign/advertising columns detected")
            if any(kw in col_set for kw in ['click', 'impression', 'conversion']):
                features.append("Engagement metrics present")
                
        elif domain == 'HR':
            if any(kw in col_set for kw in ['employee', 'emp', 'staff']):
                features.append("Employee information detected")
            if any(kw in col_set for kw in ['salary', 'payroll', 'compensation']):
                features.append("Compensation data present")
                
        elif domain == 'Logistics':
            if any(kw in col_set for kw in ['shipment', 'shipping', 'tracking']):
                features.append("Shipment/tracking columns detected")
            if any(kw in col_set for kw in ['warehouse', 'inventory']):
                features.append("Inventory/warehouse data present")
        
        return features if len(features) > 2 else features + ["Domain patterns detected"]
    
    def get_available_types(self) -> List[Dict[str, str]]:
        """Return all available classification types for manual selection."""
        return [
            {'type': 'Financial', 'description': 'Financial transactions, accounting, banking, investments'},
            {'type': 'Sales', 'description': 'Products, customers, orders, retail, e-commerce'},
            {'type': 'Time-Series', 'description': 'Temporal data, trends, forecasting, sequential'},
            {'type': 'Healthcare', 'description': 'Medical records, diagnoses, treatments, clinical data'},
            {'type': 'Marketing', 'description': 'Campaigns, leads, conversions, engagement metrics'},
            {'type': 'HR', 'description': 'Employees, payroll, attendance, workforce management'},
            {'type': 'Logistics', 'description': 'Shipping, inventory, warehouses, supply chain'},
            {'type': 'Generic', 'description': 'No specific domain - apply general analysis'},
        ]
