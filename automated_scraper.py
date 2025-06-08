#!/usr/bin/env python3
"""
Automated News Scraper - Runs independently for cron jobs
This script scrapes news from all sources and saves to database
"""

import sys
import os
import logging
from datetime import datetime
import traceback

# Add the app directory to Python path
sys.path.append('/var/www/news_summary')
sys.path.append('/var/www/news_summary/app')

# Configure logging
log_file = '/var/www/news_summary/logs/scraper.log'
os.makedirs(os.path.dirname(log_file), exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def run_automated_scraping():
    """Run the automated scraping process"""
    try:
        logger.info("🤖 Starting automated news scraping...")
        logger.info(f"📅 Scraping run time: {datetime.now()}")
        
        # Import after setting up the path
        from app.database import SessionLocal
        from app.scrapers.peoples_daily_scraper import PeoplesDailyScraper
        from app.scrapers.paper_scraper import PaperScraper
        from app.scrapers.state_council_scraper import StateCouncilScraper
        from app.scrapers.nbs_scraper import NBSScraper
        from app.scrapers.taiwan_affairs_scraper import TaiwanAffairsScraper
        from app.scrapers.mnd_scraper import MNDScraper
        from app.scrapers.guancha_scraper import GuanchaScraper
        from app.scrapers.global_times_scraper import GlobalTimesScraper
        from app.models.models import News
        from app.services.translator import MicrosoftTranslator
        
        # Create database session
        db = SessionLocal()
        
        try:
            # Initialize all scrapers with translation enabled
            logger.info("🔧 Initializing scrapers...")
            pd_scraper = PeoplesDailyScraper(translate_immediately=True)
            paper_scraper = PaperScraper(translate_immediately=True)
            sc_scraper = StateCouncilScraper(translate_immediately=True)
            nbs_scraper = NBSScraper(translate_immediately=True)
            tao_scraper = TaiwanAffairsScraper(translate_immediately=True)
            mnd_scraper = MNDScraper(translate_immediately=True)
            guancha_scraper = GuanchaScraper(translate_immediately=True)
            gt_scraper = GlobalTimesScraper(translate_immediately=True)
            
            # Fetch articles from all sources
            logger.info("📰 Fetching articles from all sources...")
            pd_articles = pd_scraper.fetch_news()
            logger.info(f"  📰 People's Daily: {len(pd_articles)} articles")
            
            paper_articles = paper_scraper.fetch_news()
            logger.info(f"  📰 The Paper: {len(paper_articles)} articles")
            
            sc_articles = sc_scraper.fetch_news()
            logger.info(f"  📰 State Council: {len(sc_articles)} articles")
            
            nbs_articles = nbs_scraper.fetch_news()
            logger.info(f"  📰 NBS: {len(nbs_articles)} articles")
            
            tao_articles = tao_scraper.fetch_news()
            logger.info(f"  📰 Taiwan Affairs: {len(tao_articles)} articles")
            
            mnd_articles = mnd_scraper.fetch_news()
            logger.info(f"  📰 MND: {len(mnd_articles)} articles")
            
            guancha_articles = guancha_scraper.fetch_news()
            logger.info(f"  📰 Guancha: {len(guancha_articles)} articles")
            
            gt_articles = gt_scraper.fetch_news()
            logger.info(f"  📰 Global Times: {len(gt_articles)} articles")
            
            # Combine all articles
            all_articles = (pd_articles + paper_articles + sc_articles + 
                          nbs_articles + tao_articles + mnd_articles + 
                          guancha_articles + gt_articles)
            
            logger.info(f"📊 Total articles collected: {len(all_articles)}")
            
            # Process and save articles
            translator = MicrosoftTranslator()
            new_articles_count = 0
            duplicate_count = 0
            
            for article in all_articles:
                try:
                    # Check if article already exists by URL
                    existing_by_url = db.query(News).filter(News.source_url == article['source_url']).first()
                    
                    if existing_by_url:
                        duplicate_count += 1
                        continue
                    
                    # Translate title if needed
                    if article.get('source_section', '').startswith('Global Times'):
                        title_english = article['title']  # Already in English
                    else:
                        try:
                            title_english = translator.translate(article['title'])
                        except Exception as e:
                            logger.warning(f"Translation failed for: {article['title'][:50]}... Error: {str(e)}")
                            title_english = None
                    
                    # Create news item
                    news_item = News(
                        title=article['title'],
                        title_english=title_english,
                        source_url=article['source_url'],
                        source_section=article.get('source_section'),
                        collection_date=article['collection_date']
                    )
                    
                    db.add(news_item)
                    db.flush()
                    new_articles_count += 1
                    
                except Exception as article_error:
                    logger.warning(f"Failed to process article: {article.get('source_url', 'Unknown')} - {str(article_error)}")
                    db.rollback()
                    duplicate_count += 1
                    continue
            
            # Commit all changes
            db.commit()
            
            # Log results
            logger.info("✅ Automated scraping completed successfully!")
            logger.info(f"📊 Results:")
            logger.info(f"  ✅ New articles saved: {new_articles_count}")
            logger.info(f"  ⚠️  Duplicates skipped: {duplicate_count}")
            logger.info(f"  📈 Total processed: {len(all_articles)}")
            
            return {
                "success": True,
                "new_articles": new_articles_count,
                "duplicates": duplicate_count,
                "total_processed": len(all_articles)
            }
            
        except Exception as processing_error:
            db.rollback()
            logger.error(f"❌ Error during article processing: {str(processing_error)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise
            
        finally:
            db.close()
    
    except Exception as e:
        logger.error(f"❌ Automated scraping failed: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return {
            "success": False,
            "error": str(e)
        }

if __name__ == "__main__":
    logger.info("🚀 Starting automated news scraper...")
    result = run_automated_scraping()
    
    if result["success"]:
        logger.info("🎉 Automated scraping completed successfully!")
        sys.exit(0)
    else:
        logger.error("💥 Automated scraping failed!")
        sys.exit(1) 