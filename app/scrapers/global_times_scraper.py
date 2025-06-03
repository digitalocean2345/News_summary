from datetime import datetime
from typing import List, Dict
from bs4 import BeautifulSoup
import requests
from .base_scraper import BaseScraper
import logging
from dotenv import load_dotenv
import os
import time

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GlobalTimesScraper(BaseScraper):
    def __init__(self, translate_immediately=False):
        super().__init__()
        # Global Times articles are already in English, so no translation needed
        self.translate_immediately = False
        self.translator = None
        logger.info("Global Times Scraper initialized - articles are already in English, no translation needed")
            
        # Define Global Times selector
        GT_SELECTOR = 'a.new_title_ms,div.common_title a,a.new_title_ml'
        
        # Global Times website configuration
        self.websites = {
            "Global Times": {
                "GT China Politics": "https://www.globaltimes.cn/china/politics/index.html",
                "GT China Society": "https://www.globaltimes.cn/china/society/index.html",
                "GT China Diplomacy": "https://www.globaltimes.cn/china/diplomacy/index.html",
                "GT China Military": "https://www.globaltimes.cn/china/military/index.html",
                "GT China Science": "https://www.globaltimes.cn/china/science/index.html",
                "GT Source Voice": "https://www.globaltimes.cn/source/gt-voice/index.html",
                "GT Source Insight": "https://www.globaltimes.cn/source/insight/index.html",
                "GT Source Economy": "https://www.globaltimes.cn/source/economy/index.html",
                "GT Source Comments": "https://www.globaltimes.cn/source/comments/index.html",
                "GT Opinion Editorial": "https://www.globaltimes.cn/opinion/editorial/index.html",
                "GT Opinion Observer": "https://www.globaltimes.cn/opinion/observer/index.html",
                "GT Opinion Asian Review": "https://www.globaltimes.cn/opinion/asian-review/index.html",
                "GT Opinion Toptalk": "https://www.globaltimes.cn/opinion/top-talk/index.html",
                "GT Opinion Viewpoint": "https://www.globaltimes.cn/opinion/viewpoint/index.html",
                "GT Indepth": "https://www.globaltimes.cn/In-depth/index.html",
            }
        }
        
        # Selector mapping for Global Times sections (all use the same selector)
        self.gt_selectors = {}
        for section_name in self.websites["Global Times"].keys():
            self.gt_selectors[section_name] = GT_SELECTOR
        
        self.source_id = 8  # Using a new source ID for Global Times

    def get_source_name(self) -> str:
        return "Global Times"

    def scrape_page(self, url, selector=None):
        """Scrape a single page for articles"""
        articles = []
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            response.encoding = 'utf-8'  # Global Times uses UTF-8
            
            if response.status_code != 200:
                logger.error(f"Failed to fetch page: {url} (Status: {response.status_code})")
                return articles
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Use provided selector or default Global Times selector
            if not selector:
                selector = 'a.new_title_ms,div.common_title a,a.new_title_ml'
            
            links = soup.select(selector)
            logger.info(f"Found {len(links)} links using selector: {selector}")
            
            current_date = datetime.now().date()
            
            for link in links:
                title = link.get_text().strip()
                href = link.get('href', '')
                
                if href and title:
                    if not href.startswith('http'):
                        # Construct full URL for Global Times
                        if href.startswith('/'):
                            href = f"https://www.globaltimes.cn{href}"
                        else:
                            href = f"https://www.globaltimes.cn/{href}"
                    
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
                    selector = self.gt_selectors.get(section_name)
                    page_articles = self.scrape_page(section_url, selector)
                    
                    # Add source section information to each article
                    for article in page_articles:
                        article['source_section'] = f"{source_name} - {section_name}"
                    
                    all_articles.extend(page_articles)
                    logger.info(f"Found {len(page_articles)} articles from {section_name}")
                    time.sleep(1)  # Be respectful to the server
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
                    
                    selector = self.gt_selectors.get(section_name)
                    page_articles = self.scrape_page(section_url, selector)
                    
                    # Add source section information to each article
                    for article in page_articles:
                        article['source_section'] = f"{source_name} - {section_name}"
                        article['collection_date'] = target_date
                    
                    all_articles.extend(page_articles)
                    logger.info(f"Found {len(page_articles)} articles from {section_name}")
                    time.sleep(1)  # Be respectful to the server
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
                        'Accept-Language': 'en-US,en;q=0.5',
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
                    selector = self.gt_selectors.get(section_name)
                    links = soup.select(selector)
                    
                    print(f"Found {len(links)} links using selector: {selector}")
                    
                    current_date = datetime.now()
                    
                    section_items = []
                    for link in links:
                        title = link.get_text().strip()
                        href = link.get('href', '')
                        
                        if href and title:
                            if not href.startswith('http'):
                                # Construct full URL for Global Times
                                if href.startswith('/'):
                                    href = f"https://www.globaltimes.cn{href}"
                                else:
                                    href = f"https://www.globaltimes.cn/{href}"
                            
                            # Global Times articles are already in English, so title_english = title
                            news_item = {
                                'title': title,
                                'title_english': title,  # Already in English, no translation needed
                                'source_url': href,
                                'source_section': f"{source_name} - {section_name}",
                                'collection_date': current_date.date(),
                                'created_at': current_date
                            }
                            section_items.append(news_item)
                            print(f"Found article: {title}")
                    
                    all_news_items.extend(section_items)
                    print(f"Total articles from {section_name}: {len(section_items)}")
                    
                except Exception as e:
                    print(f"Error scraping {section_name}: {str(e)}")
                    continue
        
        print(f"Total articles fetched from Global Times: {len(all_news_items)}")
        return all_news_items 