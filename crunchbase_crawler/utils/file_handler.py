import os
import json
import time
from crunchbase_crawler.utils.logger import logger
from crunchbase_crawler.config.settings import DATA_DIR

class FileHandler:
    @staticmethod
    def create_data_directory():
        """Create a directory for storing data with timestamp"""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        data_dir = os.path.join(DATA_DIR, timestamp)
        os.makedirs(data_dir, exist_ok=True)
        logger.info(f"📁 Created data directory: {data_dir}")
        return data_dir

    @staticmethod
    def get_latest_csv_file():
        """Get the most recent companies_data.csv file by recursively searching from root directory"""
        try:
            if not os.path.exists(DATA_DIR):
                return None
            
            csv_files = []
            for root, _, files in os.walk(DATA_DIR):
                if 'companies_data.csv' in files:
                    full_path = os.path.join(root, 'companies_data.csv')
                    csv_files.append(full_path)
            
            if not csv_files:
                return None
            
            return max(csv_files, key=os.path.getmtime)
            
        except Exception as e:
            logger.error(f"❌ Error finding companies_data.csv: {str(e)}")
            return None

    @staticmethod
    def save_to_json(data, filepath):
        """Save data to JSON file"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            logger.info(f"💾 Saved data to: {filepath}")
        except Exception as e:
            logger.error(f"❌ Failed to save JSON: {str(e)}") 