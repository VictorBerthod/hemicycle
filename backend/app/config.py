from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

DATABASE_URL = f"sqlite:///{DATA_DIR / 'hemicycle.db'}"

# API Sources
CIVIX_API_BASE = "https://www.civix.fr/api/v1"
AN_BASE_URL = "https://www.assemblee-nationale.fr"

# ETL Settings
CIVIX_PAGE_SIZE = 100
REQUEST_DELAY = 0.5  # seconds between requests
LEGISLATURE = 17
