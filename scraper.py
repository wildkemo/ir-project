import requests
from bs4 import BeautifulSoup
import json
import time
from urllib.parse import urljoin

def scrape_github_topics():
    """
    Scrapes open-source projects from GitHub Topics (github.com/topics/open-source).
    Fetches between 50 and 200 records using pagination.
    """
    base_url = "https://github.com/topics/open-source"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
    }
    
    data = []
    page = 1
    
    print("Scraping GitHub open-source projects...")
    
    while len(data) < 200:
        # Some GitHub topic pages use ?page=X, others might not. 
        # Let's try to fetch and see if we get unique results.
        url = f"{base_url}?page={page}"
        print(f"Fetching page {page}: {url}...")
        
        try:
            response = requests.get(url, headers=headers)
            if response.status_code != 200:
                print(f"Failed to fetch page {page}. Status: {response.status_code}")
                break
            
            soup = BeautifulSoup(response.text, 'html.parser')
            # Try a broader selector for articles
            articles = soup.find_all('article')
            print(f"Found {len(articles)} articles on page {page}.")
            
            if not articles:
                print("No more repositories found.")
                break
                
            new_found = 0
            for article in articles:
                # Structure: <h3> <a href="/owner">owner</a> / <a href="/owner/repo">repo</a> </h3>
                h3 = article.find('h3')
                if h3:
                    links = h3.find_all('a')
                    if len(links) >= 2:
                        repo_a = links[-1] # Usually the second one, but take the last to be safe
                        title = repo_a.get_text(strip=True)
                        repo_url = urljoin("https://github.com", repo_a.get('href'))
                        
                        # Avoid duplicates if pagination doesn't work and we keep seeing page 1
                        if any(d['url'] == repo_url for d in data):
                            continue
                        
                        # Get the description
                        # Description is usually in a <p> or a <div> with specific classes
                        desc_p = article.find('p') or article.find('div', class_='color-fg-muted')
                        content = desc_p.get_text(strip=True) if desc_p else f"Open-source repository: {title}"
                        
                        data.append({
                            "title": title,
                            "content": content,
                            "url": repo_url
                        })
                        new_found += 1
                        
                if len(data) >= 200:
                    break
            
            print(f"Added {new_found} new repositories. Total: {len(data)}")
            
            if new_found == 0:
                print("No new repositories found on this page. Stopping.")
                break
                
            page += 1
            time.sleep(1.5) # Be slightly slower
            
        except Exception as e:
            print(f"Error during scraping page {page}: {e}")
            break
            
    print(f"Dataset complete with {len(data)} records.")
    
    # Save to JSON
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)
    print("Saved to data.json")

if __name__ == "__main__":
    scrape_github_topics()
