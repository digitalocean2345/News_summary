from sqlalchemy.orm import Session
from ..models import models
from ..schemas import schemas
from ..scrapers.sina_scraper import SinaScraper
from ..scrapers.peoples_daily_scraper import PeoplesDailyScraper
import asyncio
from typing import List

class NewsService:
    def __init__(self, db: Session):
        self.db = db
        self.scrapers = [
            SinaScraper(),
            PeoplesDailyScraper()  # Add People's Daily scraper
        ]

    async def fetch_latest_news(self) -> List[models.News]:
        """Fetch news from all sources and save to database"""
        all_news = []
        duplicate_count = 0
        
        for scraper in self.scrapers:
            try:
                print(f"Fetching news from {scraper.get_source_name()}...")
                articles = await scraper.get_news()
                print(f"Found {len(articles)} articles from {scraper.get_source_name()}")
                
                for article in articles:
                    # Check if article already exists by URL only (across all dates)
                    existing_by_url = self.db.query(models.News).filter(
                        models.News.source_url == article['source_url']
                    ).first()
                    
                    if existing_by_url:
                        duplicate_count += 1
                        print(f"Skipping duplicate URL: {article['source_url']}")
                        continue
                    
                    try:
                        # Create new article
                        db_news = models.News(**article)
                        self.db.add(db_news)
                        self.db.flush()  # Check for constraint violations before commit
                        all_news.append(db_news)
                    except Exception as db_error:
                        print(f"Database constraint violation for article: {article['source_url']} - {str(db_error)}")
                        self.db.rollback()
                        duplicate_count += 1
                        continue
            
            except Exception as e:
                print(f"Error with {scraper.get_source_name()}: {str(e)}")
                continue
            finally:
                # Clean up session
                await scraper.close_session()
        
        if all_news:
            self.db.commit()
            print(f"Saved {len(all_news)} new articles to database")
        
        if duplicate_count > 0:
            print(f"Skipped {duplicate_count} duplicate articles")
        
        return all_news
