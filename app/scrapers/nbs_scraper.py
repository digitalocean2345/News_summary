from datetime import datetime
from typing import List, Dict
from bs4 import BeautifulSoup
import requests
from .base_scraper import BaseScraper
from app.services.translator import MicrosoftTranslator
import logging
from dotenv import load_dotenv
import os
import time

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NBSScraper(BaseScraper):
    def __init__(self, translate_immediately=False):
        super().__init__()
        self.translate_immediately = translate_immediately
        try:
            self.translator = MicrosoftTranslator() if translate_immediately else None
            logger.info("Microsoft Translator initialized successfully" if translate_immediately else "Translation disabled")
        except Exception as e:
            logger.error(f"Failed to initialize Microsoft Translator: {str(e)}")
            self.translator = None
            
        # Define selectors
        NBS_SELECTOR = 'a.pc1200'
        
        # NBS website configuration
        self.websites = {
            "NBS": {
                "NBS Data Release": "https://www.stats.gov.cn/sj/zxfb/",
                "NBS Data Interpretation": "https://www.stats.gov.cn/sj/sjjd/",
                "NBS Press Conference": "https://www.stats.gov.cn/sj/xwfbh/fbhwd/"
            }
        }
        
        # Selector mapping for NBS sections
        self.nbs_selectors = {
            "NBS Data Release": NBS_SELECTOR,
            "NBS Data Interpretation": NBS_SELECTOR,
            "NBS Press Conference": NBS_SELECTOR
        }
        
        self.source_id = 4

    def get_source_name(self) -> str:
        return "NBS"

    def scrape_page(self, url, selector=None):
        """Scrape a single page for articles"""
        articles = []
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            
            # Set encoding for Chinese government sites
            if "stats.gov.cn" in url:
                response.encoding = 'utf-8'
            
            if response.status_code != 200:
                logger.error(f"Failed to fetch page: {url} (Status: {response.status_code})")
                return articles
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Use provided selector or default NBS selector
            if not selector:
                selector = 'a.pc1200'
            
            links = soup.select(selector)
            logger.info(f"Found {len(links)} links using selector: {selector}")
            
            current_date = datetime.now().date()
            
            for link in links:
                title = link.get_text().strip()
                href = link.get('href', '')
                
                if href and title:
                    if not href.startswith('http'):
                        # Construct full URL for NBS
                        href = f"https://www.stats.gov.cn{href}"
                    
                    article = {
                        'title': title,
                        'source_url': href,
                        'collection_date': current_date
                    }
                    articles.append(article)
                    
        except Exception as e:
            logger.error(f"Error scraping page {url}: {str(e)}")
            
        return articles

    def fetch_news(self):
        all_articles = []
        for source_name, sections in self.websites.items():
            for section_name, section_url in sections.items():
                try:
                    logger.info(f"Scraping {source_name} - {section_name}: {section_url}")
                    
                    # Get the appropriate selector for this section
                    selector = self.nbs_selectors.get(section_name)
                    page_articles = self.scrape_page(section_url, selector)
                    
                    # Add source section information to each article
                    for article in page_articles:
                        article['source_section'] = f"{source_name} - {section_name}"
                    
                    all_articles.extend(page_articles)
                    logger.info(f"Found {len(page_articles)} articles from {section_name}")
                    time.sleep(1)
                except Exception as e:
                    logger.error(f"Error scraping {section_name}: {str(e)}")
                    continue
        
        return all_articles

    def fetch_news_by_date(self, target_date=None):
        """Fetch news for a specific date"""
        if target_date is None:
            target_date = datetime.now().date()
        
        all_articles = []
        
        for source_name, sections in self.websites.items():
            for section_name, section_url in sections.items():
                try:
                    logger.info(f"Scraping {source_name} - {section_name}: {section_url}")
                    
                    selector = self.nbs_selectors.get(section_name)
                    page_articles = self.scrape_page(section_url, selector)
                    
                    # Add source section information to each article
                    for article in page_articles:
                        article['source_section'] = f"{source_name} - {section_name}"
                        article['collection_date'] = target_date
                    
                    all_articles.extend(page_articles)
                    logger.info(f"Found {len(page_articles)} articles from {section_name}")
                    time.sleep(1)
                except Exception as e:
                    logger.error(f"Error scraping {section_name}: {str(e)}")
                    continue
        
        return all_articles

    async def get_news(self) -> List[Dict]:
        """Async method to get news with detailed logging"""
        all_news_items = []
        
        for source_name, sections in self.websites.items():
            for section_name, section_url in sections.items():
                try:
                    print(f"\n=== Starting news fetch from {source_name} - {section_name} ===")
                    
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                        'Accept-Encoding': 'gzip, deflate',
                        'Connection': 'keep-alive',
                    }
                    
                    response = requests.get(section_url, headers=headers)
                    response.encoding = 'utf-8'
                    print(f"Response status: {response.status_code}")
                    
                    if response.status_code != 200:
                        print(f"Failed to fetch page from {section_name}")
                        continue
                    
                    soup = BeautifulSoup(response.text, 'html.parser')
                    selector = self.nbs_selectors.get(section_name)
                    links = soup.select(selector)
                    
                    print(f"Found {len(links)} links using selector: {selector}")
                    
                    current_date = datetime.now()
                    
                    for link in links:
                        title = link.get_text().strip()
                        href = link.get('href', '')
                        
                        if href and title:
                            if not href.startswith('http'):
                                # Construct full URL for NBS
                                href = f"https://www.stats.gov.cn{href}"
                            
                            news_item = {
                                'title': title,
                                'source_url': href,
                                'source_section': f"{source_name} - {section_name}",
                                'collection_date': current_date.date(),
                                'scraped_at': current_date.isoformat()
                            }
                            
                            all_news_items.append(news_item)
                    
                    print(f"Successfully extracted {len(links)} news items from {section_name}")
                    
                except Exception as e:
                    print(f"Error fetching news from {section_name}: {str(e)}")
                    continue
        
        print(f"\n=== Total news items extracted: {len(all_news_items)} ===")
        return all_news_items 