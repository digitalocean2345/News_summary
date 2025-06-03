import requests
from bs4 import BeautifulSoup

def test_encoding():
    url = "http://world.people.com.cn/GB/157278/index.html"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    response = requests.get(url, headers=headers)
    
    print(f"Response status: {response.status_code}")
    print(f"Response encoding (auto-detected): {response.encoding}")
    print(f"Response apparent encoding: {response.apparent_encoding}")
    
    # Try using apparent encoding
    try:
        response.encoding = response.apparent_encoding
        soup = BeautifulSoup(response.text, 'html.parser')
        links = soup.select('div.ej_bor a[href*="/n1/"]')
        
        print(f"\n--- Testing apparent encoding: {response.apparent_encoding} ---")
        print(f"Found {len(links)} links")
        
        if links:
            for i, link in enumerate(links[:5]):  # Show first 5 titles
                title = link.get_text(strip=True)
                print(f"Title {i+1}: {title}")
    except Exception as e:
        print(f"Error with apparent encoding: {e}")
    
    # Also try getting raw bytes and decoding manually
    try:
        print(f"\n--- Testing manual UTF-8 decoding ---")
        raw_response = requests.get(url, headers=headers)
        content = raw_response.content.decode('utf-8', errors='ignore')
        soup = BeautifulSoup(content, 'html.parser')
        links = soup.select('div.ej_bor a[href*="/n1/"]')
        
        print(f"Found {len(links)} links")
        if links:
            for i, link in enumerate(links[:5]):
                title = link.get_text(strip=True)
                print(f"Title {i+1}: {title}")
    except Exception as e:
        print(f"Error with manual UTF-8: {e}")

if __name__ == "__main__":
    test_encoding() 