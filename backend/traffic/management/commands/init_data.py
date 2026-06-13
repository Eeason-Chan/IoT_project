"""
Management command: python manage.py init_data
Loads CSV, cleans data, computes SHAP/LIME, persists to MySQL.
"""
from django.core.management.base import BaseCommand
from traffic.service import TrafficService
from xai.service import SHAPService, LIMEService
from xai.models import SHAPGlobal, SHAPLocal, LIMELocal
import time


class Command(BaseCommand):
    help = 'Initialize data: load CSV, clean, compute XAI, persist to MySQL'

    def handle(self, *args, **options):
        self.stdout.write('Starting ETL pipeline...')
        start = time.time()

        # Step 1: Load CSV
        self.stdout.write('[1/6] Loading CSV data...')
        df = TrafficService.load_csv()
        self.stdout.write(f'  Loaded {len(df)} records')

        # Step 2: Clean data
        self.stdout.write('[2/6] Cleaning data...')
        df = TrafficService.clean_data(df)
        self.stdout.write(f'  After cleaning: {len(df)} records')

        # Step 3: Engineer features
        self.stdout.write('[3/6] Engineering features...')
        df = TrafficService.engineer_features(df)
        self.stdout.write(f'  Stress levels: {df["stress_level"].value_counts().to_dict()}')

        # Step 4: Persist traffic records
        self.stdout.write('[4/6] Persisting traffic records to MySQL...')
        count = TrafficService.persist_records(df)
        self.stdout.write(f'  Persisted {count} records')

        # Step 5: Get all records for XAI
        self.stdout.write('[5/6] Computing XAI explanations...')
        records = TrafficService.get_all_records_for_xai()

        # Compute SHAP global
        self.stdout.write('  Computing SHAP global importance...')
        SHAPService.compute_global(records)

        # Compute SHAP local for all
        self.stdout.write('  Computing SHAP local for all records...')
        SHAPService.compute_all_local(records)

        # Clear LIME table (LIME is computed on-demand, not pre-stored)
        self.stdout.write('  Clearing LIME table (on-demand computation)...')
        LIMEService.compute_all_local(records)

        elapsed = time.time() - start
        self.stdout.write(self.style.SUCCESS(f'ETL pipeline completed in {elapsed:.2f}s'))