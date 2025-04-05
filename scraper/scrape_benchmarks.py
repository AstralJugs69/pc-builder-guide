#!/usr/bin/env python
"""
PC Component Benchmark Scraper

This script scrapes benchmark data for PC components (CPUs, GPUs, etc.) from various
sources and stores the results in a PostgreSQL database.

Usage:
    python scrape_benchmarks.py [component_type]

Where component_type is optional and can be 'cpu', 'gpu', etc.
If not specified, the script will scrape all component types.
"""

import os
import sys
import time
import logging
import random
import requests
from typing import Dict, List, Optional, Union, Any
from bs4 import BeautifulSoup
import psycopg2
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Database connection parameters from environment variables
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')

# User agent list to rotate through to avoid being blocked
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'
]

class BenchmarkScraper:
    """Base class for benchmark scrapers"""
    
    def __init__(self):
        """Initialize the scraper"""
        self.session = requests.Session()
        self.db_conn = None
        self.db_cursor = None
    
    def connect_to_db(self) -> bool:
        """Connect to the PostgreSQL database"""
        try:
            self.db_conn = psycopg2.connect(
                dbname=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD,
                host=DB_HOST,
                port=DB_PORT
            )
            self.db_cursor = self.db_conn.cursor()
            logger.info("Connected to database successfully")
            return True
        except Exception as e:
            logger.error(f"Error connecting to database: {e}")
            return False
    
    def close_db_connection(self):
        """Close the database connection"""
        if self.db_cursor:
            self.db_cursor.close()
        if self.db_conn:
            self.db_conn.close()
        logger.info("Database connection closed")
    
    def get_random_user_agent(self) -> str:
        """Get a random user agent from the list"""
        return random.choice(USER_AGENTS)
    
    def make_request(self, url: str, headers: Optional[Dict] = None) -> Optional[requests.Response]:
        """Make an HTTP request with error handling and retries"""
        if headers is None:
            headers = {'User-Agent': self.get_random_user_agent()}
        
        max_retries = 3
        retry_delay = 2  # seconds
        
        for attempt in range(max_retries):
            try:
                response = self.session.get(url, headers=headers, timeout=10)
                response.raise_for_status()
                # Add delay to be respectful to the server
                time.sleep(random.uniform(1.0, 3.0))
                return response
            except requests.exceptions.RequestException as e:
                logger.error(f"Request failed (attempt {attempt+1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    logger.info(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    logger.error(f"Failed to retrieve {url} after {max_retries} attempts")
                    return None
    
    def parse_html(self, response: requests.Response) -> Optional[BeautifulSoup]:
        """Parse HTML response into BeautifulSoup object"""
        try:
            return BeautifulSoup(response.text, 'html.parser')
        except Exception as e:
            logger.error(f"Error parsing HTML: {e}")
            return None
    
    def store_benchmark(self, component_type: str, data: Dict[str, Any]) -> bool:
        """Store benchmark data in the database"""
        # This method should be implemented by subclasses
        raise NotImplementedError("This method should be implemented by subclasses")
    
    def scrape(self) -> bool:
        """Main scraping method"""
        # This method should be implemented by subclasses
        raise NotImplementedError("This method should be implemented by subclasses")


class CPUBenchmarkScraper(BenchmarkScraper):
    """Scraper for CPU benchmarks"""
    
    def __init__(self):
        super().__init__()
        self.base_url = "https://www.cpubenchmark.net"
    
    def scrape(self) -> bool:
        """Scrape CPU benchmarks"""
        logger.info("Starting CPU benchmark scraping")
        
        # Connect to database
        if not self.connect_to_db():
            return False
        
        try:
            # High-end CPUs
            high_end_url = f"{self.base_url}/high_end_cpus.html"
            self._scrape_cpu_page(high_end_url, "high_end")
            
            # Mid-range CPUs
            mid_range_url = f"{self.base_url}/mid_range_cpus.html"
            self._scrape_cpu_page(mid_range_url, "mid_range")
            
            # Low-end CPUs
            low_end_url = f"{self.base_url}/low_end_cpus.html"
            self._scrape_cpu_page(low_end_url, "low_end")
            
            logger.info("CPU benchmark scraping completed successfully")
            return True
        except Exception as e:
            logger.error(f"Error during CPU benchmark scraping: {e}")
            return False
        finally:
            self.close_db_connection()
    
    def _scrape_cpu_page(self, url: str, category: str):
        """Scrape a CPU benchmark page"""
        logger.info(f"Scraping {category} CPUs from {url}")
        
        response = self.make_request(url)
        if not response:
            logger.error(f"Failed to retrieve {url}")
            return
        
        soup = self.parse_html(response)
        if not soup:
            return
        
        # Example: Parse the CPU benchmark table
        # This is a placeholder - actual implementation will depend on website structure
        cpu_table = soup.find('table', {'id': 'cputable'})
        if not cpu_table:
            logger.warning(f"CPU table not found on {url}")
            return
        
        for row in cpu_table.find_all('tr')[1:]:  # Skip header row
            try:
                cols = row.find_all('td')
                if len(cols) >= 3:
                    cpu_data = {
                        'name': cols[0].text.strip(),
                        'score': int(cols[1].text.strip().replace(',', '')),
                        'price': cols[2].text.strip(),
                        'category': category
                    }
                    self.store_benchmark('cpu', cpu_data)
            except Exception as e:
                logger.error(f"Error processing CPU row: {e}")
    
    def store_benchmark(self, component_type: str, data: Dict[str, Any]) -> bool:
        """Store CPU benchmark data in the database"""
        try:
            # Example SQL - adjust based on actual database schema
            sql = """
            INSERT INTO cpu_benchmarks (name, score, price, category)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (name) DO UPDATE
            SET score = %s, price = %s, category = %s
            """
            
            self.db_cursor.execute(sql, (
                data['name'],
                data['score'],
                data['price'],
                data['category'],
                data['score'],
                data['price'],
                data['category']
            ))
            
            self.db_conn.commit()
            logger.debug(f"Stored CPU benchmark: {data['name']}")
            return True
        except Exception as e:
            self.db_conn.rollback()
            logger.error(f"Error storing CPU benchmark: {e}")
            return False


class GPUBenchmarkScraper(BenchmarkScraper):
    """Scraper for GPU benchmarks"""
    
    def __init__(self):
        super().__init__()
        self.base_url = "https://www.videocardbenchmark.net"
    
    def scrape(self) -> bool:
        """Scrape GPU benchmarks"""
        logger.info("Starting GPU benchmark scraping")
        
        # Connect to database
        if not self.connect_to_db():
            return False
        
        try:
            # High-end GPUs
            high_end_url = f"{self.base_url}/high_end_gpus.html"
            self._scrape_gpu_page(high_end_url, "high_end")
            
            # Mid-range GPUs
            mid_range_url = f"{self.base_url}/mid_range_gpus.html"
            self._scrape_gpu_page(mid_range_url, "mid_range")
            
            # Low-end GPUs
            low_end_url = f"{self.base_url}/low_end_gpus.html"
            self._scrape_gpu_page(low_end_url, "low_end")
            
            logger.info("GPU benchmark scraping completed successfully")
            return True
        except Exception as e:
            logger.error(f"Error during GPU benchmark scraping: {e}")
            return False
        finally:
            self.close_db_connection()
    
    def _scrape_gpu_page(self, url: str, category: str):
        """Scrape a GPU benchmark page"""
        logger.info(f"Scraping {category} GPUs from {url}")
        
        response = self.make_request(url)
        if not response:
            logger.error(f"Failed to retrieve {url}")
            return
        
        soup = self.parse_html(response)
        if not soup:
            return
        
        # Example: Parse the GPU benchmark table
        # This is a placeholder - actual implementation will depend on website structure
        gpu_table = soup.find('table', {'id': 'gputable'})
        if not gpu_table:
            logger.warning(f"GPU table not found on {url}")
            return
        
        for row in gpu_table.find_all('tr')[1:]:  # Skip header row
            try:
                cols = row.find_all('td')
                if len(cols) >= 3:
                    gpu_data = {
                        'name': cols[0].text.strip(),
                        'score': int(cols[1].text.strip().replace(',', '')),
                        'price': cols[2].text.strip(),
                        'category': category
                    }
                    self.store_benchmark('gpu', gpu_data)
            except Exception as e:
                logger.error(f"Error processing GPU row: {e}")
    
    def store_benchmark(self, component_type: str, data: Dict[str, Any]) -> bool:
        """Store GPU benchmark data in the database"""
        try:
            # Example SQL - adjust based on actual database schema
            sql = """
            INSERT INTO gpu_benchmarks (name, score, price, category)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (name) DO UPDATE
            SET score = %s, price = %s, category = %s
            """
            
            self.db_cursor.execute(sql, (
                data['name'],
                data['score'],
                data['price'],
                data['category'],
                data['score'],
                data['price'],
                data['category']
            ))
            
            self.db_conn.commit()
            logger.debug(f"Stored GPU benchmark: {data['name']}")
            return True
        except Exception as e:
            self.db_conn.rollback()
            logger.error(f"Error storing GPU benchmark: {e}")
            return False


def main():
    """Main entry point for the scraper"""
    logger.info("Starting benchmark scraper")
    
    # Parse command line arguments
    component_type = sys.argv[1].lower() if len(sys.argv) > 1 else None
    
    if component_type == 'cpu' or component_type is None:
        cpu_scraper = CPUBenchmarkScraper()
        cpu_result = cpu_scraper.scrape()
        logger.info(f"CPU scraping {'successful' if cpu_result else 'failed'}")
    
    if component_type == 'gpu' or component_type is None:
        gpu_scraper = GPUBenchmarkScraper()
        gpu_result = gpu_scraper.scrape()
        logger.info(f"GPU scraping {'successful' if gpu_result else 'failed'}")
    
    logger.info("Benchmark scraping completed")


if __name__ == "__main__":
    main()