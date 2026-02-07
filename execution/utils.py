import os
import json
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.tmp')
DATA_FILE = os.path.join(DATA_DIR, 'dashboard_data.json')

def ensure_tmp_dir():
    """Ensures that the .tmp directory exists."""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

def save_json(data, filename=DATA_FILE):
    """Saves data to a JSON file."""
    ensure_tmp_dir()
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        logger.info(f"Data saved to {filename}")
    except Exception as e:
        logger.error(f"Error saving data to {filename}: {e}")

def load_json(filename=DATA_FILE):
    """Loads data from a JSON file."""
    if not os.path.exists(filename):
        logger.warning(f"File {filename} not found.")
        return {}
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading data from {filename}: {e}")
        return {}
