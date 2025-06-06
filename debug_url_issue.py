from app.scrapers.state_council_scraper import StateCouncilScraper
import requests
from bs4 import BeautifulSoup

scraper = StateCouncilScraper()

# Test URL that you mentioned
test_url = 'https://www.gov.cn/zhengce/zuixin/'

print('Testing URL processing for:', test_url)
print('Websites configuration:')
for name, sections in scraper.websites.items():
    print(f'  {name}:')
    for section_name, section_url in sections.items():
        print(f'    {section_name}: {section_url}')

# Test the scraping
articles = scraper.scrape_page(test_url)
print(f'\nFound {len(articles)} articles')
for i, article in enumerate(articles[:5]):  # Show first 5
    print(f'{i+1}. Title: {article["title"][:50]}...')
    print(f'   URL: {article["source_url"]}')
    print()

# Let's also directly test BeautifulSoup parsing to see what we get
print("\n=== Direct BeautifulSoup test ===")
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}
response = requests.get(test_url, headers=headers)
response.encoding = 'utf-8'
soup = BeautifulSoup(response.text, 'html.parser')

# Use the selector from the scraper
selector = 'div.news_box a'
links = soup.select(selector)
print(f"Found {len(links)} links using selector: {selector}")

for i, link in enumerate(links[:5]):
    title = link.get_text().strip()
    href = link.get('href', '')
    print(f'{i+1}. Title: {title[:50]}...')
    print(f'   Raw href: {href}')
    
    # Test URL construction logic
    if href and not href.startswith('http'):
        constructed_url = f"https://www.gov.cn{href}"
        print(f'   Constructed URL: {constructed_url}')
    else:
        print(f'   URL already absolute: {href}')
    print() 