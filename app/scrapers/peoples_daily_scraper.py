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

class PeoplesDailyScraper(BaseScraper):
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
        PD_RENMIN_SELECTOR = 'div.fl a[href*="/n1/"]'
        PD_WORLD_SELECTOR = 'div.ej_bor a[href*="/n1/"]'
        PD_SOC_ECO_SELECTOR = 'div.ej_list_box a[href*="/n1/"]'
        
        # Complete website configuration organized by source
        self.websites = {
            "People's Daily": {
                "人民网人事频道": "http://renshi.people.com.cn/",
                "PD Anti Corruption": "http://fanfu.people.com.cn/",
                "PD International Breaking News": "http://world.people.com.cn/GB/157278/index.html",
                "PD International In-depth": "http://world.people.com.cn/GB/14549/index.html",
                "PD Society": "http://society.people.com.cn/GB/136657/index.html",
                "PD Economy": "http://finance.people.com.cn/GB/70846/index.html"
            }
        }
        
        # Selector mapping for People's Daily sections
        self.pd_selectors = {
            "人民网人事频道": PD_RENMIN_SELECTOR,
            "PD Anti Corruption": PD_RENMIN_SELECTOR,
            "PD International Breaking News": PD_WORLD_SELECTOR,
            "PD International In-depth": PD_WORLD_SELECTOR,
            "PD Society": PD_SOC_ECO_SELECTOR,
            "PD Economy": PD_SOC_ECO_SELECTOR
        }
        
        self.sources = {
            "PD International Breaking News": {
                "url": "http://world.people.com.cn/GB/157278/index.html",
                "selector": PD_WORLD_SELECTOR
            },
            "PD Society": {
                "url": "http://society.people.com.cn/GB/136657/index.html",
                "selector": PD_SOC_ECO_SELECTOR
            },
            "PD Economy": {
                "url": "http://finance.people.com.cn/GB/70846/index.html",
                "selector": PD_SOC_ECO_SELECTOR
            },
            "人民网人事频道": {
                "url": "http://renshi.people.com.cn/",
                "selector": PD_RENMIN_SELECTOR
            },
            "PD Anti Corruption": {
                "url": "http://fanfu.people.com.cn/",
                "selector": PD_RENMIN_SELECTOR
            },
            "PD International In-depth": {
                "url": "http://world.people.com.cn/GB/14549/index.html",
                "selector": PD_WORLD_SELECTOR
            }
        }
        self.source_id = 1

    def get_source_name(self) -> str:
        return "People's Daily"

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
            
            # FIXED: Use proper encoding detection for Chinese content
            if not response.encoding or response.encoding == 'ISO-8859-1':
                # Use apparent encoding (auto-detected) for Chinese content
                response.encoding = response.apparent_encoding or 'utf-8'
            
            # All People's Daily and The Paper sites now use UTF-8
            if "thepaper.cn" in url or "people.com.cn" in url:
                response.encoding = 'utf-8'
            
            if response.status_code != 200:
                logger.error(f"Failed to fetch page: {url} (Status: {response.status_code})")
                return articles
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Use provided selector or determine from URL
            if not selector:
                if "thepaper.cn" in url:
                    selector = 'div.small_toplink__GmZhY > a.index_inherit__A1ImK[target="_blank"]'
                elif "renshi.people.com.cn" in url or "fanfu.people.com.cn" in url:
                    selector = 'div.fl a[href*="/n1/"]'
                elif "world.people.com.cn" in url:
                    selector = 'div.ej_bor a[href*="/n1/"]'
                elif "society.people.com.cn" in url or "finance.people.com.cn" in url:
                    selector = 'div.ej_list_box a[href*="/n1/"]'
                else:
                    selector = 'a[href*="/n1/"]'  # fallback
            
            links = soup.select(selector)
            logger.info(f"Found {len(links)} links using selector: {selector}")
            
            current_date = datetime.now().date()
            
            for link in links:
                title = link.get_text().strip()
                href = link.get('href', '')
                
                if href and title:
                    if not href.startswith('http'):
                        # Construct full URL based on source domain
                        if "thepaper.cn" in url:
                            href = f"https://www.thepaper.cn{href}"
                        elif "society" in url:
                            href = f"http://society.people.com.cn{href}"
                        elif "finance" in url:
                            href = f"http://finance.people.com.cn{href}"
                        elif "world" in url:
                            href = f"http://world.people.com.cn{href}"
                        elif "renshi" in url:
                            href = f"http://renshi.people.com.cn{href}"
                        elif "fanfu" in url:
                            href = f"http://fanfu.people.com.cn{href}"
                        else:
                            href = f"http://people.com.cn{href}"
                    
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
                    selector = self.pd_selectors.get(section_name)
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
        """Fetch news for a specific date (mainly for People's Daily sections)"""
        if target_date is None:
            target_date = datetime.now().date()
        
        all_articles = []
        
        # Focus on People's Daily sections for date-based fetching
        pd_sections = {
            "人民网人事频道": {
                "url": "http://renshi.people.com.cn/",
                "selector": 'div.fl a[href*="/n1/"]'
            },
            "PD Anti Corruption": {
                "url": "http://fanfu.people.com.cn/",
                "selector": 'div.fl a[href*="/n1/"]'
            },
            "PD International Breaking News": {
                "url": "http://world.people.com.cn/GB/157278/index.html",
                "selector": 'div.ej_bor a[href*="/n1/"]'
            },
            "PD International In-depth": {
                "url": "http://world.people.com.cn/GB/14549/index.html",
                "selector": 'div.ej_bor a[href*="/n1/"]'
            },
            "PD Society": {
                "url": "http://society.people.com.cn/GB/136657/index.html",
                "selector": 'div.ej_list_box a[href*="/n1/"]'
            },
            "PD Economy": {
                "url": "http://finance.people.com.cn/GB/70846/index.html",
                "selector": 'div.ej_list_box a[href*="/n1/"]'
            }
        }
        
        for section_name, config in pd_sections.items():
            try:
                logger.info(f"Scraping {section_name}: {config['url']}")
                page_articles = self.scrape_page(config['url'], config['selector'])
                
                # Add source section information to each article
                for article in page_articles:
                    article['source_section'] = f"People's Daily - {section_name}"
                    article['collection_date'] = target_date
                
                all_articles.extend(page_articles)
                logger.info(f"Found {len(page_articles)} articles from {section_name}")
                time.sleep(1)
            except Exception as e:
                logger.error(f"Error scraping {section_name}: {str(e)}")
                continue
        
        return all_articles

    async def get_news(self) -> List[Dict]:
        all_news_items = []
        
        for source_name, source_config in self.sources.items():
            try:
                print(f"\n=== Starting news fetch from {source_name} ===")
                
                # Use the base scraper's fetch_page method with proper encoding handling
                content = await self.fetch_page(source_config["url"])
                
                if not content:
                    print(f"Failed to fetch page from {source_name}")
                    continue
                
                soup = BeautifulSoup(content, 'html.parser')
                links = soup.select(source_config["selector"])
                
                print(f"Found {len(links)} links using selector: {source_config['selector']}")
                
                current_date = datetime.now()
                
                for link in links:
                    title = link.get_text().strip()
                    href = link.get('href', '')
                    
                    if href and title:
                        if not href.startswith('http'):
                            # Handle different base URLs for different sections
                            if "society" in source_config["url"]:
                                href = f"http://society.people.com.cn{href}"
                            elif "finance" in source_config["url"]:
                                href = f"http://finance.people.com.cn{href}"
                            elif "world" in source_config["url"]:
                                href = f"http://world.people.com.cn{href}"
                            elif "renshi" in source_config["url"]:
                                href = f"http://renshi.people.com.cn{href}"
                            elif "fanfu" in source_config["url"]:
                                href = f"http://fanfu.people.com.cn{href}"
                            else:
                                href = f"http://people.com.cn{href}"
                        
                        print(f"Found article: {title[:50]}... at {href}")
                        
                        # Fetch the full article content to include in the news item
                        content_text = ""
                        try:
                            article_content = await self.fetch_page(href)
                            if article_content:
                                article_soup = BeautifulSoup(article_content, 'html.parser')
                                
                                # Try different content selectors for People's Daily articles
                                content_selectors = [
                                    '.show_text',  # Common People's Daily content class
                                    '.rm_txt_con',  # Another People's Daily content class
                                    '.article_text',
                                    '.content',
                                    '.main_text',
                                    'div[class*="content"]',
                                    'div[class*="text"]'
                                ]
                                
                                for selector in content_selectors:
                                    content_div = article_soup.select_one(selector)
                                    if content_div:
                                        # Extract text and clean it up
                                        content_text = content_div.get_text(strip=True)
                                        if len(content_text) > 100:  # Only use if substantial content
                                            break
                                
                                # If no content found with selectors, try to extract from paragraphs
                                if len(content_text) < 100:
                                    paragraphs = article_soup.find_all('p')
                                    if paragraphs:
                                        content_text = ' '.join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])
                        
                        except Exception as content_error:
                            print(f"Could not fetch content for {href}: {content_error}")
                        
                        news_item = {
                            'title': title,
                            'content': content_text,
                            'source_url': href,
                            'category': 'general',
                            'language': 'zh'
                        }
                        all_news_items.append(news_item)
                
                print(f"Articles found from {source_name}: {len([item for item in all_news_items if source_name in item.get('source_name', '')])}")
                
            except Exception as e:
                print(f"Error in get_news for {source_name}: {str(e)}")
                import traceback
                print(f"Traceback: {traceback.format_exc()}")
                continue
        
        print(f"\nTotal articles found from all sources: {len(all_news_items)}")
        return all_news_items
