from app.database import get_db
from app.models.models import News
from sqlalchemy.orm import Session
from datetime import datetime

# Get database session
db = next(get_db())

# Check for the specific date
date_obj = datetime.strptime('2025-05-31', '%Y-%m-%d').date()
news_items = db.query(News).filter(News.collection_date == date_obj).all()

print(f"Total articles for 2025-05-31: {len(news_items)}")

# Group by domain
domains = {}
for item in news_items:
    url = item.source_url
    if '//' in url:
        domain = url.split('//')[1].split('/')[0]
    else:
        domain = 'unknown'
    
    if domain not in domains:
        domains[domain] = []
    domains[domain].append(url)

print("\nDomains and counts:")
for domain, urls in domains.items():
    print(f"  {domain}: {len(urls)} articles")

# Show sample People's Daily URLs
peoples_daily_urls = domains.get('world.people.com.cn', [])
print(f"\nSample world.people.com.cn URLs ({len(peoples_daily_urls)} total):")
for i, url in enumerate(peoples_daily_urls[:10]):
    print(f"  {i+1}. {url}") 