from app.database import get_db
from app.models.models import News
from sqlalchemy.orm import Session

# Get database session
db = next(get_db())

# Query recent State Council articles
sc_articles = db.query(News).filter(
    News.source_url.like('%gov.cn%')
).order_by(News.id.desc()).limit(10).all()

print("=== Recent State Council Articles in Database ===")
for article in sc_articles:
    print(f"ID: {article.id}")
    print(f"Title: {article.title[:60]}...")
    print(f"URL: {article.source_url}")
    print(f"Section: {article.source_section}")
    print(f"Date: {article.collection_date}")
    print("-" * 50)

# Check for any URLs that might have ".." pattern
problematic_urls = db.query(News).filter(
    News.source_url.like('%..%')
).all()

print(f"\n=== Articles with '..' in URL ({len(problematic_urls)} found) ===")
for article in problematic_urls:
    print(f"ID: {article.id}")
    print(f"Title: {article.title[:60]}...")
    print(f"URL: {article.source_url}")
    print(f"Section: {article.source_section}")
    print("-" * 50)

# Check all State Council Policy articles specifically
policy_articles = db.query(News).filter(
    News.source_section.like('%State Council Latest Policies%')
).order_by(News.id.desc()).limit(5).all()

print(f"\n=== State Council Latest Policies Articles ({len(policy_articles)} found) ===")
for article in policy_articles:
    print(f"ID: {article.id}")
    print(f"Title: {article.title[:60]}...")
    print(f"URL: {article.source_url}")
    print(f"Section: {article.source_section}")
    print("-" * 50)

# Check policy interpretation articles
interpretation_articles = db.query(News).filter(
    News.source_section.like('%Policy Interpretation%')
).order_by(News.id.desc()).limit(5).all()

print(f"\n=== State Council Policy Interpretation Articles ({len(interpretation_articles)} found) ===")
for article in interpretation_articles:
    print(f"ID: {article.id}")
    print(f"Title: {article.title[:60]}...")
    print(f"URL: {article.source_url}")
    print(f"Section: {article.source_section}")
    print("-" * 50)

db.close() 