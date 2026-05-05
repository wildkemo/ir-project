import requests
from bs4 import BeautifulSoup
import json
import time
from urllib.parse import urljoin
from urllib.robotparser import RobotFileParser

def get_robot_parser(url="https://github.com/robots.txt"):
    """Fetches and parses the robots.txt file for the given URL."""
    rp = RobotFileParser()
    try:
        rp.set_url(url)
        rp.read()
        return rp
    except Exception as e:
        print(f"Warning: Could not fetch robots.txt: {e}")
        return None

def get_repo_details(url, headers, rp=None):
    if rp and not rp.can_fetch("*", url):
        print(f"  [Skipped] Robots.txt disallows: {url}")
        return None
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return None
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 1. Get Meta Description
        description = ""
        meta_desc = soup.find('meta', {'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            description = meta_desc.get('content')
            if 'Contribute to' in description and 'development by creating an account' in description:
                description = description.split('. Contribute to')[0]
        
        # 2. Get "About" section if description is short or empty
        if len(description) < 50:
            about_p = soup.find('p', class_='f4 my-3')
            if about_p:
                description = about_p.get_text(strip=True)

        # 3. Get README content (rendered on the main page)
        readme_text = ""
        readme_section = soup.find('div', id='readme')
        if readme_section:
            markdown_body = readme_section.find('article', class_='markdown-body')
            if markdown_body:
                # Get the first 1000 characters of the README to avoid massive files
                readme_text = markdown_body.get_text(separator=' ', strip=True)[:1000]
        
        # Combine the data
        full_content = f"{description} {readme_text}".strip()
        return full_content if full_content else None
    except Exception as e:
        print(f'  Error fetching details for {url}: {e}')
        return None

def scrape_github_data():
    topics = ['open-source', 'machine-learning', 'data-science', 'web-development', 'python']
    # Updated to a more modern Chrome User-Agent
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
    
    print('Step 0: Checking robots.txt...')
    rp = get_robot_parser()
    
    repo_urls = []
    print('Step 1: Discovering 200 repository links...')
    topic_idx = 0
    page = 1
    while len(repo_urls) < 200 and topic_idx < len(topics):
        topic = topics[topic_idx]
        url = f'https://github.com/topics/{topic}?page={page}'
        
        if rp and not rp.can_fetch("*", url):
            print(f"  [Skipped] Robots.txt disallows topic page: {url}")
            topic_idx += 1
            page = 1
            continue

        print(f"  Searching topic '{topic}' (Page {page})...")
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 429:
                print("  [Error] Rate limited by GitHub (429). Please wait a few minutes before retrying.")
                break
            if response.status_code != 200:
                print(f"  [Warning] Received status {response.status_code} for topic {topic}. Skipping.")
                topic_idx += 1
                page = 1
                continue
            
            soup = BeautifulSoup(response.text, 'html.parser')
            articles = soup.find_all('article')
            if not articles:
                # Check if it's an empty page or a blocked page
                if "Too many requests" in response.text:
                    print("  [Error] GitHub blocked the request (Too many requests).")
                    break
                print(f"  [Info] No more repositories found for topic '{topic}'.")
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
                        repo_url = urljoin('https://github.com', repo_a.get('href'))
                        title = repo_a.get_text(strip=True)
                        if repo_url not in [r['url'] for r in repo_urls]:
                            repo_urls.append({'title': title, 'url': repo_url})
                            found_on_page += 1
                if len(repo_urls) >= 200:
                    break
            print(f'    Added {found_on_page} links. Total found: {len(repo_urls)}')
            page += 1
            time.sleep(1)
        except Exception as e:
            print(f'    Error discovery phase: {e}')
            break
    print(f'\nStep 2: Scanning {len(repo_urls)} individual links for content...')
    final_data = []
    for i, repo in enumerate(repo_urls):
        url = repo['url']
        print(f'  [{i + 1}/{len(repo_urls)}] Scanning: {url}')
        details = get_repo_details(url, headers, rp)
        content = details if details else f"Repository focusing on {repo['title']}"
        final_data.append({'title': repo['title'], 'content': content, 'url': url})
        time.sleep(1.2)
        if (i + 1) % 20 == 0:
            with open('data.json', 'w', encoding='utf-8') as f:
                json.dump(final_data, f, indent=4)
            print(f'    (Progress saved to data.json)')
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(final_data, f, indent=4)
    print(f'\nScanning complete. {len(final_data)} records saved to data.json')
if __name__ == '__main__':
    scrape_github_data()
