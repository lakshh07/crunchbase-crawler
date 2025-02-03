from setuptools import setup, find_packages

setup(
    name="crunchbase_crawler",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'requests==2.31.0',
        'beautifulsoup4==4.12.3',
        'lxml==5.1.0',
        'pandas==2.1.4',
        'numpy==1.26.3',
        'openai==1.60.2',
        'psycopg2-binary==2.9.9',
        'python-dotenv==1.0.1',
        'tqdm==4.66.1',
    ],
) 