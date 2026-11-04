import os

from dotenv import load_dotenv

from pathlib import Path

load_dotenv(Path(__file__).resolve().parent.parent / '.env')

META_API_KEY = (os.getenv("META_API_KEY") or os.getenv("MODEL_API_KEY") or "").strip()
META_API_BASE_URL = (os.getenv("META_API_BASE_URL") or "https://api.meta.ai/v1").rstrip('/')
META_MODEL = os.getenv("META_MODEL", "muse-spark-1.3")
META_TIMEOUT_SECONDS = float(os.getenv("META_TIMEOUT_SECONDS", "30"))
META_MAX_OUTPUT_TOKENS = int(os.getenv("META_MAX_OUTPUT_TOKENS", "2048"))
META_MAX_CALLS_PER_HOUR = int(os.getenv("META_MAX_CALLS_PER_HOUR", "50"))
META_MAX_CALLS_PER_OWNER_PER_HOUR = int(os.getenv("META_MAX_CALLS_PER_OWNER_PER_HOUR", "10"))
# local = perceptual hash + histogram (no key needed), mock = fixed fake result, meta = Meta Model API
COMPARER = os.getenv("COMPARER", "local")
ML_ENABLED = os.getenv('ML_ENABLED', 'true').lower() in {'1', 'true', 'yes'}
ML_MODEL_PATH = Path(os.getenv('ML_MODEL_PATH', str(Path(__file__).resolve().parent.parent / 'outputs/ml/profile_risk_model.json')))
PAIR_ML_MODEL_PATH = Path(os.getenv('PAIR_ML_MODEL_PATH', str(Path(__file__).resolve().parent.parent / 'outputs/ml/pair_risk_model.json')))
# Shared secret for reviewer endpoints (X-Admin-Token header). Empty = those endpoints are disabled (503).
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "")
PUBLIC_DEMO_ENABLED = os.getenv('PUBLIC_DEMO_ENABLED', 'false').lower() in {'true', '1', 'yes'}
DEMO_SESSION_SECRET = os.getenv('DEMO_SESSION_SECRET', '')
DEMO_DATA_ROOT = Path(os.getenv('DEMO_DATA_ROOT', str(Path(__file__).resolve().parent.parent / 'outputs' / 'sandboxes')))
