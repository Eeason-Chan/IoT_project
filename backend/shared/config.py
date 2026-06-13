"""
Configuration center - fail-fast on missing required env vars.
"""
import os
from dotenv import load_dotenv

load_dotenv()


def get_db_config():
    return {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('DB_NAME', 'xai_traffic'),
        'USER': os.getenv('DB_USER', 'root'),
        'PASSWORD': os.getenv('DB_PASSWORD', ''),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '3306'),
        'OPTIONS': {'charset': 'utf8mb4'},
    }


def get_csv_path():
    path = os.getenv('CSV_DATA_PATH')
    if not path:
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        path = os.path.join(base, '..', 'smart_city_traffic_stress_dataset.csv')
    return path