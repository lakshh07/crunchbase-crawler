import pandas as pd
from concurrent.futures import ThreadPoolExecutor
from crunchbase_crawler.utils.logger import logger
from crunchbase_crawler.config.settings import MAX_WORKERS

class DataProcessor:
    @staticmethod
    def process_single_company(uuid, crawler):
        """Process a single company by UUID"""
        try:
            properties = crawler.get_company_details(uuid)
            if properties:
                company_data = crawler.process_company(properties, uuid)
                if company_data:
                    logger.info(f"✅ Processed company: {company_data.get('name', 'Unknown')}")
                    return company_data
            else:
                logger.error(f"❌ Failed to get details for UUID: {uuid}")
        except Exception as e:
            logger.error(f"❌ Error processing UUID {uuid}: {str(e)}")
        return None

    @staticmethod
    def process_csv_data(file_path, crawler):
        """Process UUIDs from CSV file and fetch company details in parallel"""
        try:
            logger.info(f"📂 Reading data from: {file_path}")
            df = pd.read_csv(file_path, usecols=['uuid'])
            logger.info(f"📊 Found {len(df)} companies in file")

            companies_data = []
            with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
                futures = [
                    executor.submit(DataProcessor.process_single_company, row['uuid'], crawler)
                    for _, row in df.iterrows()
                ]
                
                for future in futures:
                    try:
                        result = future.result()
                        if result:
                            companies_data.append(result)
                    except Exception as e:
                        logger.error(f"❌ Error in thread execution: {str(e)}")

            return companies_data
            
        except Exception as e:
            logger.error(f"❌ Failed to process CSV file: {str(e)}")
            return []