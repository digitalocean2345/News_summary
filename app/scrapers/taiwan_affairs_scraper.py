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

class TaiwanAffairsScraper(BaseScraper):
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
        TAO_SELECTOR = 'ul.scdList a'
        
        # Taiwan Affairs Office website configuration
        self.websites = {
            "Taiwan Affairs": {
                "Taiwan Affairs Office": "http://www.gwytb.gov.cn/xwdt/xwfb/wyly/",
                "Chinese Departments on Taiwan": "http://www.gwytb.gov.cn/bmst/"
            }
        }
        
        # Selector mapping for Taiwan Affairs sections
        self.tao_selectors = {
            "Taiwan Affairs Office": TAO_SELECTOR,
            "Chinese Departments on Taiwan": TAO_SELECTOR
        }
        
        self.source_id = 5

    def get_source_name(self) -> str:
        return "Taiwan Affairs"

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
            
            # Enhanced encoding handling for Taiwan Affairs sites
            if "gwytb.gov.cn" in url:
                # Try UTF-8 first, then GB2312 as fallback
                if response.encoding.lower() in ['iso-8859-1', 'windows-1252']:
                    response.encoding = 'utf-8'
                elif response.apparent_encoding:
                    response.encoding = response.apparent_encoding
                else:
                    response.encoding = 'gb2312'
            
            if response.status_code != 200:
                logger.error(f"Failed to fetch page: {url} (Status: {response.status_code})")
                return articles
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Use provided selector or default TAO selector
            if not selector:
                selector = 'ul.scdList a'
            
            links = soup.select(selector)
            logger.info(f"Found {len(links)} links using selector: {selector}")
            
            current_date = datetime.now().date()
            
            for link in links:
                title = link.get_text().strip()
                href = link.get('href', '')
                
                if href and title:
                    if not href.startswith('http'):
                        # Construct full URL for Taiwan Affairs Office
                        href = f"http://www.gwytb.gov.cn{href}"
                    
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
                    selector = self.tao_selectors.get(section_name)
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
                    
                    selector = self.tao_selectors.get(section_name)
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
                    
                    # Enhanced encoding handling for Taiwan Affairs sites
                    if "gwytb.gov.cn" in section_url:
                        # Try UTF-8 first, then GB2312 as fallback
                        if response.encoding.lower() in ['iso-8859-1', 'windows-1252']:
                            response.encoding = 'utf-8'
                        elif response.apparent_encoding:
                            response.encoding = response.apparent_encoding
                        else:
                            response.encoding = 'gb2312'
                    
                    print(f"Response status: {response.status_code}")
                    print(f"Response encoding: {response.encoding}")
                    
                    if response.status_code != 200:
                        print(f"Failed to fetch page from {section_name}")
                        continue
                    
                    soup = BeautifulSoup(response.text, 'html.parser')
                    selector = self.tao_selectors.get(section_name)
                    links = soup.select(selector)
                    
                    print(f"Found {len(links)} links using selector: {selector}")
                    
                    current_date = datetime.now()
                    
                    for link in links:
                        title = link.get_text().strip()
                        href = link.get('href', '')
                        
                        if href and title:
                            if not href.startswith('http'):
                                # Construct full URL for Taiwan Affairs Office
                                href = f"http://www.gwytb.gov.cn{href}"
                            
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