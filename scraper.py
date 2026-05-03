import requests
from bs4 import BeautifulSoup
import json
import time
from urllib.parse import urljoin

def get_repo_details(url, headers):
    """
    Visits an individual repository page to extract ONLY the description.
    """
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return None
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 1. Best source: The meta description tag (cleanest summary)
        meta_desc = soup.find('meta', {'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            content = meta_desc.get('content')
            # GitHub meta descriptions usually end with "- owner/repo: description"
            # or start with a specific format. Let's try to clean it if needed.
            # Usually: "A collective list of free APIs. Contribute to public-apis/public-apis development by creating an account on GitHub."
            if "Contribute to" in content and "development by creating an account" in content:
                content = content.split(". Contribute to")[0]
            return content

        # 2. Fallback: The specific <p> tag in the About section
        about_p = soup.find('p', class_='f4 my-3') # Common class for repo description
        if about_p:
            return about_p.get_text(strip=True)
            
        return None
    except Exception as e:
        print(f"  Error fetching details for {url}: {e}")
        return None

def scrape_github_data():
    """
    Scrapes GitHub repositories by:
    1. Finding 200 unique repository URLs from various topics.
    2. Visiting each URL to get detailed content.
    """
    topics = ["open-source", "machine-learning", "data-science", "web-development", "python"]
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    }
    
    repo_urls = []
    
    print("Step 1: Discovering 200 repository links...")
    
    topic_idx = 0
    page = 1
    
    while len(repo_urls) < 200 and topic_idx < len(topics):
        topic = topics[topic_idx]
        url = f"https://github.com/topics/{topic}?page={page}"
        print(f"  Searching topic '{topic}' (Page {page})...")
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code != 200:
                topic_idx += 1
                page = 1
                continue
            
            soup = BeautifulSoup(response.text, 'html.parser')
            articles = soup.find_all('article')
            
            if not articles:
                topic_idx += 1
                page = 1
                continue
                
            found_on_page = 0
            for article in articles:
                h3 = article.find('h3')
                if h3:
                    links = h3.find_all('a')
                    if len(links) >= 2:
                        repo_a = links[-1]
                        repo_url = urljoin("https://github.com", repo_a.get('href'))
                        title = repo_a.get_text(strip=True)
                        
                        if repo_url not in [r['url'] for r in repo_urls]:
                            repo_urls.append({"title": title, "url": repo_url})
                            found_on_page += 1
                
                if len(repo_urls) >= 200:
                    break
            
            print(f"    Added {found_on_page} links. Total found: {len(repo_urls)}")
            page += 1
            time.sleep(1) # Small delay between topic pages
            
        except Exception as e:
            print(f"    Error discovery phase: {e}")
            break

    print(f"\nStep 2: Scanning {len(repo_urls)} individual links for content...")
    
    final_data = []
    for i, repo in enumerate(repo_urls):
        url = repo['url']
        print(f"  [{i+1}/{len(repo_urls)}] Scanning: {url}")
        
        # Get deeper content
        details = get_repo_details(url, headers)
        
        # If deep scan fails, we still keep the record but with a placeholder or the snippet if we had it
        # Actually, let's just use what we found
        content = details if details else f"Repository focusing on {repo['title']}"
        
        final_data.append({
            "title": repo['title'],
            "content": content,
            "url": url
        })
        
        # Delay to be respectful to GitHub
        time.sleep(1.2) 
        
        # Periodic save just in case
        if (i + 1) % 20 == 0:
            with open('data.json', 'w', encoding='utf-8') as f:
                json.dump(final_data, f, indent=4)
            print(f"    (Progress saved to data.json)")

    # Final save
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(final_data, f, indent=4)
    
    print(f"\nScanning complete. {len(final_data)} records saved to data.json")

if __name__ == "__main__":
    scrape_github_data()
