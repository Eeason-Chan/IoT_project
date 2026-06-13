"""
XAI Service - SHAP and LIME explanation computation.
Uses TreeExplainer with HistGradientBoostingRegressor (trained once, saved to file).
"""
import os
import numpy as np
import pandas as pd
import shap
import lime
import lime.lime_tabular
from sklearn.ensemble import HistGradientBoostingRegressor
from django.conf import settings
from django.db import transaction
from traffic.service import TrafficService
from .models import SHAPGlobal, SHAPLocal, LIMELocal

# Path to saved model
MODEL_PATH = os.path.join(settings.BASE_DIR, 'hgb_model.joblib')


class SHAPService:
    """SHAP explanation using TreeExplainer."""

    FEATURE_COLS = ['traffic_density', 'horn_events_per_min', 'avg_speed',
                    'signal_wait_time', 'road_quality_score']

    @classmethod
    def _get_model(cls):
        """Load trained model from disk, or train and save if not exists."""
        if not os.path.exists(MODEL_PATH):
            cls._train_and_save_model()
        import joblib
        return joblib.load(MODEL_PATH)

    @classmethod
    def _train_and_save_model(cls):
        """Train HistGradientBoostingRegressor on all records and save to disk."""
        records = TrafficService.get_all_records_for_xai()
        df = pd.DataFrame(records)
        X = df[cls.FEATURE_COLS].values
        y = df['stress_index'].values

        model = HistGradientBoostingRegressor(
            max_iter=100,
            max_depth=10,
            learning_rate=0.1,
            random_state=42
        )
        model.fit(X, y)

        import joblib
        os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
        joblib.dump(model, MODEL_PATH)
        print(f"[SHAPService] Model trained and saved to {MODEL_PATH}")

    @classmethod
    def compute_global(cls, records):
        """Compute global SHAP feature importance using TreeExplainer."""
        model = cls._get_model()
        df = pd.DataFrame(records)
        X = df[cls.FEATURE_COLS].values
        feature_names = cls.FEATURE_COLS

        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(X)

        # Global importance: mean of |SHAP values|
        importance = np.abs(shap_values).mean(axis=0)
        idx = np.argsort(importance)[::-1]

        results = []
        for i in idx:
            results.append({
                'feature': feature_names[int(i)],
                'shap_value': round(float(importance[int(i)]), 4)
            })

        with transaction.atomic():
            SHAPGlobal.objects.all().delete()
            for r in results:
                SHAPGlobal.objects.create(feature=r['feature'], shap_value=r['shap_value'])

        return results

    @classmethod
    def compute_local(cls, record_id):
        """Get SHAP local explanation from DB cache."""
        try:
            local = SHAPLocal.objects.get(record_id=record_id)
            return local.shap_values
        except SHAPLocal.DoesNotExist:
            return None

    @classmethod
    def compute_all_local(cls, records):
        """Compute SHAP local for ALL records using TreeExplainer (no sampling).
        TreeExplainer is fast enough to compute all 49982 records directly.
        """
        model = cls._get_model()
        df = pd.DataFrame(records)
        X = df[cls.FEATURE_COLS].values

        print("[SHAPService] Computing SHAP for all records with TreeExplainer...")
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(X)

        with transaction.atomic():
            SHAPLocal.objects.all().delete()
            batch = []
            for i, row in df.iterrows():
                rid = row['record_id']
                shap_dict = {}
                for j, col in enumerate(cls.FEATURE_COLS):
                    shap_dict[col] = round(float(shap_values[i][j]), 4)
                batch.append(SHAPLocal(record_id=rid, shap_values=shap_dict))
                if len(batch) >= 1000:
                    SHAPLocal.objects.bulk_create(batch, batch_size=1000)
                    batch = []
            if batch:
                SHAPLocal.objects.bulk_create(batch, batch_size=1000)

        print(f"[SHAPService] Saved SHAP for {len(df)} records to DB")

    @classmethod
    def get_summary_scatter(cls, records):
        """SHAP summary scatter plot data (limited sample for visualization)."""
        df = pd.DataFrame(records)
        shap_locals = {sl.record_id: sl.shap_values for sl in SHAPLocal.objects.all()}

        # Limit to 5000 records for scatter plot performance
        sample_size = 5000
        df_sample = df.sample(n=min(sample_size, len(df)), random_state=42)

        results = []
        for _, row in df_sample.iterrows():
            rid = row['record_id']
            if rid in shap_locals:
                for feature in cls.FEATURE_COLS:
                    results.append({
                        'record_id': rid,
                        'feature': feature,
                        'feature_value': row[feature],
                        'shap_value': shap_locals[rid].get(feature, 0),
                        'stress_level': row['stress_level']
                    })
        return results


class LIMEService:
    """LIME explanation using LimeTabularExplainer with trained model."""

    FEATURE_COLS = ['traffic_density', 'horn_events_per_min', 'avg_speed',
                    'signal_wait_time', 'road_quality_score']

    @classmethod
    def compute_local(cls, record_id, all_records):
        """Compute LIME local explanation for a specific record."""
        model = SHAPService._get_model()
        df = pd.DataFrame(all_records)
        X = df[cls.FEATURE_COLS].values

        sample_size = min(1000, len(X))
        X_sample = X[np.random.choice(len(X), sample_size, replace=False)]

        explainer = lime.lime_tabular.LimeTabularExplainer(
            X_sample,
            feature_names=cls.FEATURE_COLS,
            class_names=['stress_index'],
            mode='regression'
        )

        record = next((r for r in all_records if r['record_id'] == record_id), None)
        if not record:
            return None

        record_features = [record.get(col, 0) for col in cls.FEATURE_COLS]
        exp = explainer.explain_instance(
            np.array(record_features),
            lambda x: model.predict(x),
            num_features=len(cls.FEATURE_COLS)
        )

        weights = {}
        for feat, weight in exp.as_list():
            weights[feat] = round(float(weight), 4)

        with transaction.atomic():
            LIMELocal.objects.filter(record_id=record_id).delete()
            LIMELocal.objects.create(record_id=record_id, lime_weights=weights)

        return weights

    @classmethod
    def compute_all_local(cls, records):
        """Clear LIME table. LIME is computed on-demand, not pre-stored."""
        with transaction.atomic():
            LIMELocal.objects.all().delete()

    @classmethod
    def compute_local(cls, record_id, all_records):
        """Compute LIME on-demand for a specific record (no storage)."""
        model = SHAPService._get_model()
        df = pd.DataFrame(all_records)
        X = df[cls.FEATURE_COLS].values

        sample_size = min(1000, len(X))
        X_sample = X[np.random.choice(len(X), sample_size, replace=False)]

        explainer = lime.lime_tabular.LimeTabularExplainer(
            X_sample,
            feature_names=cls.FEATURE_COLS,
            class_names=['stress_index'],
            mode='regression'
        )

        record = next((r for r in all_records if r['record_id'] == record_id), None)
        if not record:
            return None

        record_features = [record.get(col, 0) for col in cls.FEATURE_COLS]
        exp = explainer.explain_instance(
            np.array(record_features),
            lambda x: model.predict(x),
            num_features=len(cls.FEATURE_COLS)
        )

        weights = {}
        for feat, weight in exp.as_list():
            weights[feat] = round(float(weight), 4)

        return weights

    @classmethod
    def get_local(cls, record_id):
        """Get LIME explanation for a record (not stored, returns None)."""
        return None