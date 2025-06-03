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

class GuanchaScraper(BaseScraper):
    def __init__(self, translate_immediately=False):
        super().__init__()
        self.translate_immediately = translate_immediately
        try:
            self.translator = MicrosoftTranslator() if translate_immediately else None
            logger.info("Microsoft Translator initialized successfully" if translate_immediately else "Translation disabled")
        except Exception as e:
            logger.error(f"Failed to initialize Microsoft Translator: {str(e)}")
            self.translator = None
            
        # Complete website configuration organized by source
        self.websites = {
            "Guancha": {
                "Guancha International": "https://www.guancha.cn/GuoJi%C2%B7ZhanLue/list_1.shtml",
                "Guancha Chinese Diplomacy": "https://www.guancha.cn/ZhongGuoWaiJiao/list_1.shtml"
            }
        }
        
        # Selector for Guancha sections
        self.guancha_selector = 'h4.module-title a'
        
        self.sources = {
            "Guancha International": {
                "url": "https://www.guancha.cn/GuoJi%C2%B7ZhanLue/list_1.shtml",
                "selector": self.guancha_selector
            },
            "Guancha Chinese Diplomacy": {
                "url": "https://www.guancha.cn/ZhongGuoWaiJiao/list_1.shtml",
                "selector": self.guancha_selector
            }
        }
        self.source_id = 7  # Unique ID for Guancha

    def get_source_name(self) -> str:
        return "Guancha"

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
            response.encoding = 'utf-8'  # Guancha uses UTF-8
            
            if response.status_code != 200:
                logger.error(f"Failed to fetch page: {url} (Status: {response.status_code})")
                return articles
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Use provided selector or the default Guancha selector
            if not selector:
                selector = self.guancha_selector
            
            links = soup.select(selector)
            logger.info(f"Found {len(links)} links using selector: {selector}")
            
            current_date = datetime.now().date()
            
            for link in links:
                title = link.get_text().strip()
                href = link.get('href', '')
                
                if href and title:
                    if not href.startswith('http'):
                        # Construct full URL for Guancha
                        href = f"https://www.guancha.cn{href}"
                    
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
                    selector = self.guancha_selector
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
        
        # Guancha sections for date-based fetching
        guancha_sections = {
            "Guancha International": {
                "url": "https://www.guancha.cn/GuoJi%C2%B7ZhanLue/list_1.shtml",
                "selector": self.guancha_selector
            },
            "Guancha Chinese Diplomacy": {
                "url": "https://www.guancha.cn/ZhongGuoWaiJiao/list_1.shtml",
                "selector": self.guancha_selector
            }
        }
        
        for section_name, section_info in guancha_sections.items():
            try:
                logger.info(f"Scraping Guancha - {section_name} for date {target_date}: {section_info['url']}")
                
                page_articles = self.scrape_page(section_info['url'], section_info['selector'])
                
                # Update collection date and add source section
                for article in page_articles:
                    article['collection_date'] = target_date
                    article['source_section'] = f"Guancha - {section_name}"
                
                all_articles.extend(page_articles)
                logger.info(f"Found {len(page_articles)} articles from {section_name}")
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Error scraping {section_name}: {str(e)}")
                continue
        
        return all_articles

    async def get_news(self) -> List[Dict]:
        """Get news articles from Guancha"""
        return self.fetch_news() 