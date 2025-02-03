from ..utils.logger import logger

class SQLHandler:
    @staticmethod
    def generate_sql_file(companies_data, output_path):
        """Generate SQL file with CREATE TABLE and INSERT statements"""
        try:
            logger.info(f"📝 Generating SQL file: {output_path}")
            
            with open(output_path, 'w', encoding='utf-8') as f:
                # Write CREATE TABLE statements
                f.write("""-- Create tables
CREATE TABLE IF NOT EXISTS companies (
    uuid VARCHAR(255) PRIMARY KEY,
    rank_org INT,
    name VARCHAR(255),
    description TEXT,
    website VARCHAR(255),
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    entity_def_id VARCHAR(255),
    permalink VARCHAR(255),
    image_id VARCHAR(255),
    image_url TEXT,
    website_content TEXT,
    gpt_analysis TEXT
);

CREATE TABLE IF NOT EXISTS company_facets (
    id SERIAL PRIMARY KEY,
    company_uuid VARCHAR(255) REFERENCES companies(uuid),
    facet_id VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS company_locations (
    id SERIAL PRIMARY KEY,
    company_uuid VARCHAR(255) REFERENCES companies(uuid),
    location_value VARCHAR(255),
    location_type VARCHAR(50),
    location_permalink VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS company_social_media (
    company_uuid VARCHAR(255) PRIMARY KEY REFERENCES companies(uuid),
    facebook VARCHAR(255),
    linkedin VARCHAR(255),
    twitter VARCHAR(255)
);

-- Delete existing data
DELETE FROM company_facets;
DELETE FROM company_locations;
DELETE FROM company_social_media;
DELETE FROM companies;

""")
                
                # Write INSERT statements for each company
                for company in companies_data:
                    # Insert main company data
                    f.write(f"""
INSERT INTO companies (uuid, rank_org, name, description, website, created_at, updated_at, 
                      entity_def_id, permalink, image_id, image_url, website_content, gpt_analysis)
VALUES (
    '{company['uuid']}',
    {company['rank_org'] or 'NULL'},
    '{company['name'].replace("'", "''")}',
    '{company['description'].replace("'", "''") if company['description'] else ''}',
    '{company['website'] or ''}',
    '{company['created_at']}',
    '{company['updated_at']}',
    '{company['entity_def_id']}',
    '{company['permalink']}',
    '{company['image_id'] or ''}',
    '{company['image_url'] or ''}',
    '{company.get('website_content', '').replace("'", "''") if company.get('website_content') else ''}',
    '{company.get('gpt_analysis', '').replace("'", "''") if company.get('gpt_analysis') else ''}'
);
""")

                    # Insert facets
                    for facet in company['facet_ids']:
                        f.write(f"""
INSERT INTO company_facets (company_uuid, facet_id)
VALUES ('{company['uuid']}', '{facet}');
""")

                    # Insert locations
                    for location in company['locations']:
                        f.write(f"""
INSERT INTO company_locations (company_uuid, location_value, location_type, location_permalink)
VALUES (
    '{company['uuid']}',
    '{location['value'].replace("'", "''")}',
    '{location['type']}',
    '{location['permalink']}'
);
""")

                    # Insert social media
                    f.write(f"""
INSERT INTO company_social_media (company_uuid, facebook, linkedin, twitter)
VALUES (
    '{company['uuid']}',
    '{company['social_media']['facebook'] or ''}',
    '{company['social_media']['linkedin'] or ''}',
    '{company['social_media']['twitter'] or ''}'
);
""")

                logger.info(f"✅ Successfully generated SQL file with {len(companies_data)} companies")
                
        except Exception as e:
            logger.error(f"❌ Failed to generate SQL file: {str(e)}") 