from concurrent.futures import ThreadPoolExecutor
import time
import random
import os
from crunchbase_crawler.core.crawler import CrunchbaseCrawler
from crunchbase_crawler.core.data_processor import DataProcessor
from crunchbase_crawler.utils.file_handler import FileHandler
from crunchbase_crawler.utils.logger import logger
from crunchbase_crawler.config.settings import (
    CRUNCHBASE_API_KEY, OPENAI_API_KEY, MAX_WORKERS, 
    DELAY_MIN, DELAY_MAX, DEFAULT_BATCH_SIZE
)

def process_api_data(crawler):
    """Process data by fetching from Crunchbase API"""
    page_number = 1
    total_processed = 0
    organizations = crawler.get_organizations(limit=DEFAULT_BATCH_SIZE)
    
    while organizations:
        logger.info(f"📑 Processing page {page_number} with {len(organizations)} organizations")
        
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = [
                executor.submit(crawler.process_company, entity, entity['uuid']) 
                for entity in organizations
            ]
            
            for future in futures:
                try:
                    result = future.result()
                    total_processed += 1
                    if result:
                        logger.info(f"✅ Processed: {result['name']}")
                except Exception as e:
                    logger.error(f"❌ Error processing company: {str(e)}")
        
        if total_processed >= DEFAULT_BATCH_SIZE:
            logger.info(f"🎯 Reached requested limit of {DEFAULT_BATCH_SIZE} companies")
            break
            
        if len(organizations) == DEFAULT_BATCH_SIZE:
            last_uuid = organizations[-1]['uuid']
            logger.info(f"🔄 Fetching next page after UUID: {last_uuid}")
            organizations = crawler.get_organizations(after_id=last_uuid, limit=DEFAULT_BATCH_SIZE)
            page_number += 1
            time.sleep(random.uniform(DELAY_MIN, DELAY_MAX))
        else:
            logger.info("🏁 No more organizations to process")
            break
    
    logger.info(f"🎉 Crawling complete! Total companies processed: {total_processed}")

def get_next_batch(crawler, last_uuid):
    """Get next batch of organizations"""
    logger.info(f"🔄 Fetching next page after UUID: {last_uuid}")
    return crawler.get_organizations(after_id=last_uuid, limit=DEFAULT_BATCH_SIZE)

def main():
    print("\n🔄 Choose data source:")
    print("1. Fetch from Crunchbase API")
    print("2. Use existing CSV file")
    
    choice = input("\nEnter your choice (1 or 2): ").strip()
    while choice not in ['1', '2']:
        print("❌ Invalid choice. Please enter 1 or 2.")
        choice = input("\nEnter your choice (1 or 2): ").strip()

    data_dir = FileHandler.create_data_directory()
    
    try:
        if choice == '1':
            crawler = CrunchbaseCrawler(data_dir, CRUNCHBASE_API_KEY, OPENAI_API_KEY)
            process_api_data(crawler)
        else:
            csv_file = FileHandler.get_latest_csv_file()
            if not csv_file:
                logger.error("❌ No existing CSV files found")
                return
            
            print(f"\n📁 Latest data file found: {csv_file}")
            use_latest = input("Use this file? (y/n): ").strip().lower()
            
            file_path = csv_file if use_latest == 'y' else input("\nEnter the path to your CSV file: ").strip()
            
            if not os.path.exists(file_path):
                logger.error("❌ File not found")
                return
            
            crawler = CrunchbaseCrawler(data_dir, CRUNCHBASE_API_KEY, OPENAI_API_KEY)
            companies_data = DataProcessor.process_csv_data(file_path, crawler)
            crawler.companies_data = companies_data

        FileHandler.save_to_json(
            crawler.companies_data,
            os.path.join(data_dir, 'companies_data.json')
        )
        
        crawler.save_to_sql()
        
        logger.info(f"🎉 Process completed! Total companies saved: {len(crawler.companies_data)}")

    except Exception as e:
        logger.error(f"💥 An error occurred in main process: {str(e)}")

if __name__ == "__main__":
    main() 