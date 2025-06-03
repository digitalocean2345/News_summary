import requests
import json

try:
    response = requests.get('http://localhost:8000/api/debug/date-urls/2025-05-31')
    if response.status_code == 200:
        data = response.json()
        print(f"Date: {data['date']}")
        print(f"Total articles: {data['total_articles']}")
        print("\nDomain counts:")
        for domain, count in data['domain_counts'].items():
            print(f"  {domain}: {count} articles")
        
        print("\nSample URLs by domain:")
        for domain, articles in data['domains'].items():
            print(f"\n{domain} ({len(articles)} articles):")
            for i, article in enumerate(articles[:5]):  # Show first 5 URLs
                print(f"  {i+1}. {article['url']}")
            if len(articles) > 5:
                print(f"  ... and {len(articles) - 5} more")
    else:
        print(f"Error: {response.status_code} - {response.text}")
except Exception as e:
    print(f"Error: {e}") 