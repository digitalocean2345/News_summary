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

class PaperScraper(BaseScraper):
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
        PAPER_SELECTOR = 'div.small_toplink__GmZhY > a.index_inherit__A1ImK[target="_blank"]'
        
        # The Paper website configuration
        self.websites = {
            "The Paper": {
                "Paper China Government": "https://www.thepaper.cn/list_25462",
                "Paper Personnel Trends": "https://www.thepaper.cn/list_25423",
                "Paper Tiger Hunt": "https://www.thepaper.cn/list_25490",
                "Paper Project No1": "https://www.thepaper.cn/list_25424",
                "Paper Zhongnanhai": "https://www.thepaper.cn/list_25488",
                "Paper Live on the scene": "https://www.thepaper.cn/list_25428",
                "Paper exclusive reports": "https://www.thepaper.cn/list_25427",
                "Paper public opinion": "https://www.thepaper.cn/list_25489"
            }
        }
        
        # Selector mapping for The Paper sections
        self.paper_selectors = {
            "Paper China Government": PAPER_SELECTOR,
            "Paper Personnel Trends": PAPER_SELECTOR,
            "Paper Tiger Hunt": PAPER_SELECTOR,
            "Paper Project No1": PAPER_SELECTOR,
            "Paper Zhongnanhai": PAPER_SELECTOR,
            "Paper Live on the scene": PAPER_SELECTOR,
            "Paper exclusive reports": PAPER_SELECTOR,
            "Paper public opinion": PAPER_SELECTOR,
        }
        
        self.source_id = 2

    def get_source_name(self) -> str:
        return "The Paper"

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
            response.encoding = 'utf-8'  # The Paper uses UTF-8
            
            if response.status_code != 200:
                logger.error(f"Failed to fetch page: {url} (Status: {response.status_code})")
                return articles
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Use provided selector or default Paper selector
            if not selector:
                selector = 'div.small_toplink__GmZhY > a.index_inherit__A1ImK[target="_blank"]'
            
            links = soup.select(selector)
            logger.info(f"Found {len(links)} links using selector: {selector}")
            
            current_date = datetime.now().date()
            
            for link in links:
                title = link.get_text().strip()
                href = link.get('href', '')
                
                if href and title:
                    if not href.startswith('http'):
                        # Construct full URL for The Paper
                        href = f"https://www.thepaper.cn{href}"
                    
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
                    selector = self.paper_selectors.get(section_name)
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
                    
                    selector = self.paper_selectors.get(section_name)
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
                    selector = self.paper_selectors.get(section_name)
                    links = soup.select(selector)
                    
                    print(f"Found {len(links)} links using selector: {selector}")
                    
                    current_date = datetime.now()
                    
                    for link in links:
                        title = link.get_text().strip()
                        href = link.get('href', '')
                        
                        if href and title:
                            if not href.startswith('http'):
                                href = f"https://www.thepaper.cn{href}"
                            
                            print(f"Found article: {title[:50]}... at {href}")
                            
                            news_item = {
                                'title': title,
                                'source_url': href,
                                'source_name': f"{self.get_source_name()} - {section_name}",
                                'collection_date': current_date
                            }
                            
                            if self.translator:
                                try:
                                    news_item['title_english'] = self.translator.translate(title)
                                except Exception as e:
                                    print(f"Translation failed for '{title}': {str(e)}")
                                    news_item['title_english'] = None
                            
                            all_news_items.append(news_item)
                    
                    time.sleep(1)  # Be respectful to the server
                    
                except Exception as e:
                    print(f"Error fetching from {section_name}: {str(e)}")
                    continue
        
        return all_news_items 