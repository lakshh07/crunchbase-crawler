import requests
import os
from crunchbase_crawler.utils.logger import logger
from crunchbase_crawler.config.settings import (
    BASE_API_URL, COMPANY_FIELDS, 
    DEFAULT_BATCH_SIZE
)
from bs4 import BeautifulSoup
from openai import OpenAI
from crunchbase_crawler.utils.sql_handler import SQLHandler

class CrunchbaseCrawler:
    def __init__(self, data_dir, crunchbase_api_key, openai_api_key):
        self.api_key = crunchbase_api_key
        self.data_dir = data_dir
        self.companies_data = []
        self.openai_client = OpenAI(
            api_key=openai_api_key
        )
        
    def get_organizations(self, after_id=None, limit=DEFAULT_BATCH_SIZE):
        """Fetch organizations from Crunchbase API"""
        try:
            logger.info(f"📊 Fetching first {limit} organizations...")
            
            payload = {
                "field_ids": COMPANY_FIELDS,
                "order": [{"field_id": "rank_org", "sort": "asc"}],
                "limit": limit,
                "after_id": after_id
            }

            headers = {
                'accept': 'application/json',   
                'Content-Type': 'application/json',
                'X-cb-user-key': self.api_key
            }

            response = self._make_api_request(
                method="POST",
                url=f"{BASE_API_URL}/searches/organizations",
                payload=payload,
                headers=headers
            )

            if not response:
                return []

            logger.info(f"🌐 Total companies available: {response.get('count', 0)}")
            return response.get('entities', [])

        except Exception as e:
            logger.error(f"💥 Failed to get organizations: {str(e)}")
            return []
        
    def get_company_details(self, uuid):
        """Get detailed company information"""
        try:
            logger.info(f"📋 Fetching company details for: {uuid}")

            headers = {
                'accept': 'application/json',   
                'X-cb-user-key': self.api_key
            }

            response = self._make_api_request(
                method="GET",
                url=f"{BASE_API_URL}/entities/organizations/{uuid}",
                headers=headers,
                params={"field_ids": ",".join(COMPANY_FIELDS)}
            )

            if not response:
                return None
            
            return response
        except Exception as e:
            logger.error(f"💥 Failed to get company details: {str(e)}")
            return None

    def _make_api_request(self, method, url, headers, payload=None, params=None):
        """Make API request with error handling"""
        try:
            request_kwargs = {
                'method': method,
                'url': url,
                'headers': headers,
            }
            
            if payload:
                request_kwargs['json'] = payload
            if params:
                request_kwargs['params'] = params

            # Use requests.request with only the specified arguments
            response = requests.request(**request_kwargs)
            
            if response.status_code != 200:
                logger.error(f"❌ API request failed: {response.status_code}")
                logger.error(f"❌ Response: {response.text}")
                return None

            return response.json()
            
        except Exception as e:
            logger.error(f"❌ API request failed: {str(e)}")
            return None

    def process_company(self, entity, uuid):
        """Process company data from API response"""
        try:
            logger.info(f"🔍 Processing company: {uuid}")
            properties= entity.get('properties', {})

            company_data = {
                'uuid': uuid,
                'rank_org': properties.get('rank_org'),
                'name': properties.get('name'),
                'description': properties.get('short_description'),
                'website': properties.get('website_url'),
                'created_at': properties.get('created_at'),
                'updated_at': properties.get('updated_at'),
                'entity_def_id': properties.get('entity_def_id'),
                'permalink': properties.get('permalink'),
                'image_id': properties.get('image_id'),
                'image_url': properties.get('image_url'),
                'facet_ids': properties.get('facet_ids', []),
                'locations': self._extract_locations(properties),
                'social_media': self._extract_social_media(properties)
            }

            if properties.get('website_url'):
                website_content = self.scrape_website_content(properties['website_url'])
                company_data['website_content'] = website_content
                if website_content and self.openai_client:
                    logger.info(f"💾 Analyzing website content for: {company_data['name']}")
                    company_data['gpt_analysis'] = self.analyze_website_with_gpt(website_content)
                    logger.info(f"💾 Saved GPT analysis for: {company_data['name']}")
                else:
                    logger.warning(f"❌ No website content or GPT client available for: {company_data['name']}")

            self.companies_data.append(company_data)
            return company_data

        except Exception as e:
            logger.error(f"❌ Failed to process company: {str(e)}")
            return None

    def _extract_locations(self, properties):
        """Extract location data from properties"""
        locations = []
        for loc in properties.get('location_identifiers', []):
            locations.append({
                'value': loc.get('value'),
                'type': loc.get('location_type'),
                'permalink': loc.get('permalink')
            })
        return locations

    def _extract_social_media(self, properties):
        """Extract social media links from properties"""
        return {
            'facebook': properties.get('facebook', {}).get('value'),
            'linkedin': properties.get('linkedin', {}).get('value'),
            'twitter': properties.get('twitter', {}).get('value')
        }

    def scrape_website_content(self, url):
        """Scrape content from company website"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()  
            soup = BeautifulSoup(response.text, 'lxml') 
            
            for script in soup(["script", "style", "header", "footer", "nav", "aside"]):
                script.decompose()
                
            text_elements = soup.find_all(['p', 'h1', 'h2', 'h3', 'li'])
            text = " ".join(elem.get_text(strip=True) for elem in text_elements)
            
            return text if text else None
        except Exception as e:
            logger.error(f"❌ Website scraping failed for {url}: {str(e)}")
            return None

    def analyze_website_with_gpt(self, website_content):
        """Analyze website content using GPT"""
        try:
            if not self.openai_client or not website_content:
                return None

            max_length = 4000  
            chunks = [website_content[i:i+max_length] for i in range(0, len(website_content), max_length)]

            summaries = []
            for chunk in chunks:
                response = self.openai_client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {
                            "role": "system", 
                            "content": (
                                "You are an expert business analyst. Analyze the provided website content "
                                "and generate a structured summary with these key sections:\n"
                                "1. **Company Overview** (Name, Industry, Founding Year, Location)\n"
                                "2. **Products & Services** (Main offerings and their features)\n"
                                "3. **Target Audience** (Who they serve, market segmentation)\n"
                                "4. **Unique Value Proposition** (What makes them different from competitors)\n"
                                "5. **Business Model** (How they generate revenue, pricing strategy)\n"
                                "6. **Key Achievements** (Awards, funding rounds, major partnerships)\n"
                                "7. **Technology & Innovation** (Tech stack, patents, innovation focus)\n"
                                "8. **Customer Testimonials & Case Studies** (If available)\n"
                                "9. **Recent News & Blog Highlights** (If mentioned on the website)\n"
                                "10. **Any Additional Insights or Observations from the Website**\n"
                            )
                        },
                        {
                            "role": "user", 
                            "content": f"Analyze this website content and provide a detailed structured summary of the company:\n\n{chunk}"
                        }
                    ]
                )
                summaries.append(response.choices[0].message.content)

            return "\n\n".join(summaries)
        except Exception as e:
            logger.error(f"❌ GPT analysis failed: {str(e)}")
            return None

    def save_to_sql(self):
        """Generate SQL file from companies data"""
        try:
            sql_file = os.path.join(self.data_dir, 'companies_data.sql')
            SQLHandler.generate_sql_file(self.companies_data, sql_file)
        except Exception as e:
            logger.error(f"❌ Failed to generate SQL file: {str(e)}") 