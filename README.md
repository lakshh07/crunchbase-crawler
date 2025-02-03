# Crunchbase Crawler

A Python-based crawler for extracting and processing company data from Crunchbase, with additional features for website content analysis using GPT-4.

## ✨ Features

- **Data Collection**

  - Fetch company data from Crunchbase API
  - Configurable batch processing with rate limiting
  - Multi-threaded data collection for improved performance

- **Data Processing**

  - Extract company details including social media profiles and locations
  - Website content scraping
  - Intelligent content analysis using GPT-4
  - Structured data output in JSON format

- **Database Integration**

  - Automatic SQL statement generation
  - Normalized database schema
  - Support for PostgreSQL
  - Handles data relationships and foreign keys

- **Error Handling & Logging**
  - Comprehensive error logging
  - Progress tracking with timestamps
  - Resumable operations

## 🛠️ Prerequisites

- Python 3.8+
- Crunchbase API Key
- OpenAI API Key
- PostgreSQL (for database operations)

## 📦 Installation

1. Install dependencies:

```bash
pip install -e .
```

## ⚙️ Configuration

2. Create a `.env` file in the project root with the following variables:

```bash
CRUNCHBASE_API_KEY=your_crunchbase_api_key
OPENAI_API_KEY=your_openai_api_key
BASE_CB_API_URL=crunchbase_api_base_url
```

2. Adjust settings in `crunchbase_crawler/config/settings.py` if needed:

- `DEFAULT_BATCH_SIZE`: Number of companies to process per batch
- `MAX_WORKERS`: Number of concurrent threads
- `DELAY_MIN/MAX`: API request delay range

## 🚀 Usage

Run the crawler:

```bash
python -m crunchbase_crawler.main
```

The script will prompt you to:

1. Choose between fetching new data from Crunchbase API or processing existing CSV data
2. If using existing data, select or specify the CSV file location

## 📁 Output

The crawler generates the following outputs in timestamped directories under `crunchbase_data/`:

- `companies_data.json`: Raw company data including:
  - Basic company information (name, description, website)
  - Social media links
  - Location data
  - Website content (if available)
  - GPT-4 analysis of website content (if enabled)
- `companies_data.sql`: SQL statements for database import, creating tables for:
  - Companies
  - Company facets
  - Company locations
  - Social media links

## 🗄️ Database Schema

The SQL output creates the following tables:

- `companies`: Main company information including GPT analysis
- `company_facets`: Company categorization data
- `company_locations`: Geographic location information
- `company_social_media`: Social media profile links
