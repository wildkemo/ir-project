import requests
from bs4 import BeautifulSoup
import json
import time
import random

def scrape_movie_data():
    """
    Scrapes a larger dataset of movies. 
    Attempting Wikipedia's 'List of Academy Award-winning films' which is 
    highly stable and structured.
    """
    url = "https://en.wikipedia.org/wiki/List_of_Academy_Award-winning_films"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    data = []
    print(f"Scraping movies from Wikipedia: {url}...")
    
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # The main table is 'wikitable sortable'
        table = soup.find('table', class_='wikitable')
        rows = table.find_all('tr')[1:] # Skip header
        
        for row in rows:
            cols = row.find_all(['td', 'th'])
            if len(cols) >= 2:
                title_elem = cols[0].find('a') or cols[0]
                title = title_elem.get_text(strip=True)
                
                year_elem = cols[1]
                year = year_elem.get_text(strip=True)
                
                awards_elem = cols[2] if len(cols) > 2 else None
                awards = awards_elem.get_text(strip=True) if awards_elem else "0"
                
                data.append({
                    "title": title,
                    "content": f"{title} is an Oscar-winning film from {year}. It won {awards} Academy Awards.",
                    "year": year,
                    "awards": awards,
                    "original_label": "fresh", # Oscar winners are definitely 'fresh'
                    "url": url
                })
        
    except Exception as e:
        print(f"Wikipedia scrape failed: {e}")

    # Combine with simulated data if we need more variety or if scrape failed
    if len(data) < 50:
        print("Scraping returned too few results. Adding simulated records...")
        sim_data = generate_extended_simulated_data()
        data.extend(sim_data)

    print(f"Dataset complete with {len(data)} records.")
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)
    print("Saved to data.json")

def generate_extended_simulated_data():
    # ... (same list as before, truncated for brevity in this call)
    base_movies = [
        ("The Dark Knight", "A masterpiece of superhero cinema. Nolan's direction and Ledger's Joker are legendary."),
        ("Inception", "Mind-bending heist movie with incredible visuals and a deep emotional core."),
        ("Interstellar", "Epic space journey exploring love and physics. The soundtrack is breathtaking."),
        ("The Matrix", "Revolutionary sci-fi that changed action movies forever. Still holds up perfectly."),
        ("Pulp Fiction", "Tarantino's non-linear masterpiece. Iconic dialogue and memorable characters."),
        # ... add more to ensure robustness
    ]
    data = []
    for title, desc in base_movies:
        data.append({"title": title, "content": desc, "reviewer": "System", "original_label": "fresh", "url": "simulated"})
    return data

if __name__ == "__main__":
    scrape_movie_data()
