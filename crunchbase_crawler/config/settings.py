import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Configuration
CRUNCHBASE_API_KEY = os.getenv('CRUNCHBASE_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
BASE_API_URL = os.getenv('BASE_CB_API_URL')
SCRAPEOWL_API_KEY = os.getenv('SCRAPEOWL_API_KEY')
SCRAPEOWL_API_URL = os.getenv('SCRAPEOWL_API_URL')

if not CRUNCHBASE_API_KEY:
    raise ValueError("❌ CRUNCHBASE_API_KEY not found in environment variables")

if not OPENAI_API_KEY:
    raise ValueError("❌ OPENAI_API_KEY not found in environment variables")

if not BASE_API_URL:
    raise ValueError("❌ BASE_CB_API_URL not found in environment variables")

if not SCRAPEOWL_API_KEY:
    raise ValueError("❌ SCRAPEOwl_API_KEY not found in environment variables")

if not SCRAPEOWL_API_URL:
    raise ValueError("❌ SCRAPEOwl_API_URL not found in environment variables") 

# File paths
BASE_DIR = os.getcwd()
DATA_DIR = os.path.join(BASE_DIR, 'crunchbase_data')

# API Request Configuration
DEFAULT_BATCH_SIZE = 2
MAX_WORKERS = 3
DELAY_MIN = 1
DELAY_MAX = 3

# Field configurations
COMPANY_FIELDS = [
    "created_at", "entity_def_id", "facebook", "facet_ids", 
    "identifier", "image_id", "image_url", "linkedin", 
    "location_identifiers", "name", "permalink", 
    "short_description", "twitter", "updated_at", 
    "uuid", "website_url", "rank_org"
] 


