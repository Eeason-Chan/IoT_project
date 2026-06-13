"""
Traffic Service - data cleaning, statistics, timeseries, zone analysis.
"""
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
from django.conf import settings
from django.db import transaction
from .models import TrafficRecord


class TrafficService:
    """Handle all traffic data operations."""

    @staticmethod
    def load_csv(path=None):
        """Load raw CSV data."""
        path = path or settings.CSV_DATA_PATH
        df = pd.read_csv(path)

        # Auto-generate timestamp-like index for time features
        df['timestamp'] = pd.date_range('2024-01-01', periods=len(df), freq='10min')

        return df

    @staticmethod
    def clean_data(df):
        """
        Data cleaning:
        1. Missing value imputation (mean/median)
        2. Outlier filtering (IQR-based)
        3. Data type standardization
        """
        # 1. Missing values - fill with median for numeric columns
        numeric_cols = ['traffic_density', 'horn_events_per_min', 'avg_speed',
                        'signal_wait_time', 'road_quality_score', 'stress_index']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = df[col].fillna(df[col].median())

        # Fill categorical with mode
        for col in ['weather_condition', 'driver_experience_level']:
            if col in df.columns:
                df[col] = df[col].fillna(df[col].mode()[0] if not df[col].mode().empty else 'Clear')

        # 2. Outlier filtering using IQR for stress_index
        Q1 = df['stress_index'].quantile(0.25)
        Q3 = df['stress_index'].quantile(0.75)
        IQR = Q3 - Q1
        lower = Q1 - 1.5 * IQR
        upper = Q3 + 1.5 * IQR
        df = df[(df['stress_index'] >= lower) & (df['stress_index'] <= upper)]

        # 3. Data type standardization
        df['traffic_density'] = df['traffic_density'].astype(float)
        df['horn_events_per_min'] = df['horn_events_per_min'].astype(float)
        df['avg_speed'] = df['avg_speed'].astype(float)
        df['signal_wait_time'] = df['signal_wait_time'].astype(float)
        df['road_quality_score'] = df['road_quality_score'].astype(float)
        df['stress_index'] = df['stress_index'].astype(float)

        return df

    @staticmethod
    def engineer_features(df):
        """
        Feature engineering:
        1. Time features: hour, day_of_week, is_weekend
        2. Target variable: stress_level (Low/Medium/High)
        3. Standardization and encoding
        """
        # 1. Time features
        df['hour'] = df['timestamp'].dt.hour
        df['day_of_week'] = df['timestamp'].dt.dayofweek
        df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(bool)

        # 2. Stress level categorization
        def categorize_stress(val):
            if val < 40:
                return 'Low'
            elif val < 65:
                return 'Medium'
            else:
                return 'High'

        df['stress_level'] = df['stress_index'].apply(categorize_stress)

        return df

    @staticmethod
    @transaction.atomic
    def persist_records(df):
        """Bulk create records into MySQL with sequential record_id starting from 1."""
        # Delete all records but keep table structure
        TrafficRecord.objects.all().delete()

        records = []
        for idx, (_, row) in enumerate(df.iterrows(), start=1):
            records.append(TrafficRecord(
                record_id=idx,
                traffic_density=row['traffic_density'],
                horn_events_per_min=row['horn_events_per_min'],
                avg_speed=row['avg_speed'],
                signal_wait_time=row['signal_wait_time'],
                weather_condition=row['weather_condition'],
                road_quality_score=row['road_quality_score'],
                driver_experience_level=row['driver_experience_level'],
                stress_index=row['stress_index'],
                hour=row['hour'],
                day_of_week=row['day_of_week'],
                is_weekend=row['is_weekend'],
                stress_level=row['stress_level'],
            ))

        TrafficRecord.objects.bulk_create(records, batch_size=1000)
        return len(records)

    @staticmethod
    def get_summary():
        """KPI overview: avg stress, total records, high stress ratio."""
        records = TrafficRecord.objects.all()
        total = records.count()
        if total == 0:
            return {'avg_stress': 0, 'total': 0, 'high_stress_ratio': 0}

        avg_stress = round(sum(r.stress_index for r in records) / total, 2)
        high_count = records.filter(stress_level='High').count()
        high_ratio = round(high_count / total * 100, 2)

        return {
            'avg_stress': avg_stress,
            'total': total,
            'high_stress_ratio': high_ratio,
        }

    @staticmethod
    def get_distribution():
        """Pressure distribution: Low/Medium/High counts and ratios."""
        records = TrafficRecord.objects.all()
        total = records.count()
        if total == 0:
            return {'low': {'count': 0, 'ratio': 0}, 'medium': {'count': 0, 'ratio': 0}, 'high': {'count': 0, 'ratio': 0}}

        distribution = {}
        for level in ['Low', 'Medium', 'High']:
            count = records.filter(stress_level=level).count()
            distribution[level.lower()] = {
                'count': count,
                'ratio': round(count / total * 100, 2)
            }
        return distribution

    @staticmethod
    def get_timeseries(granularity='hour'):
        """Time series data by hour or day."""
        records = TrafficRecord.objects.all()

        if granularity == 'day':
            data = {}
            for r in records:
                key = f"Day {r.day_of_week}"
                if key not in data:
                    data[key] = []
                data[key].append(r.stress_index)
            result = [{'period': k, 'avg_stress': round(sum(v) / len(v), 2)} for k, v in data.items()]
        else:
            data = {}
            for r in records:
                key = f"Hour {r.hour}"
                if key not in data:
                    data[key] = []
                data[key].append(r.stress_index)
            result = [{'period': k, 'avg_stress': round(sum(v) / len(v), 2)} for k, v in data.items()]

        return sorted(result, key=lambda x: x['period'])

    @staticmethod
    def get_zone_stats():
        """Zone stats: road_quality_score as zone proxy, average stress index."""
        records = TrafficRecord.objects.all()
        zones = {}

        for r in records:
            zone = f"Road Quality {int(r.road_quality_score)}"
            if zone not in zones:
                zones[zone] = []
            zones[zone].append(r.stress_index)

        result = []
        for zone, indices in zones.items():
            result.append({
                'zone': zone,
                'avg_stress': round(sum(indices) / len(indices), 2),
                'count': len(indices)
            })

        return sorted(result, key=lambda x: x['avg_stress'], reverse=True)

    @staticmethod
    def get_records_paginated(page=1, page_size=20, sort='record_id'):
        """Paginated raw data table."""
        records = TrafficRecord.objects.all().order_by(sort)
        total = records.count()
        start = (page - 1) * page_size
        end = start + page_size
        items = list(records[start:end].values(
            'record_id', 'traffic_density', 'horn_events_per_min', 'avg_speed',
            'signal_wait_time', 'weather_condition', 'road_quality_score',
            'driver_experience_level', 'stress_index', 'stress_level',
            'hour', 'day_of_week', 'is_weekend'
        ))
        return {'items': items, 'total': total, 'page': page, 'page_size': page_size}

    @staticmethod
    def get_all_records_for_xai():
        """Return all records as list for XAI computation."""
        records = TrafficRecord.objects.all()
        return list(records.values(
            'record_id', 'traffic_density', 'horn_events_per_min', 'avg_speed',
            'signal_wait_time', 'weather_condition', 'road_quality_score',
            'driver_experience_level', 'stress_index', 'hour', 'day_of_week', 'is_weekend',
            'stress_level'
        ))