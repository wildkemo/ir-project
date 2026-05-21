import os
import time
import json
import base64
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed


class FastGitHubScraper:
    def __init__(
        self,
        github_token=None,
        output_file="new_data.json",
        delay=0.5,
        max_workers=12,
        max_pages_per_topic=5
    ):
        self.base_url = "https://github.com"
        self.api_url = "https://api.github.com"

        self.output_file = output_file
        self.delay = delay
        self.max_workers = max_workers
        self.max_pages_per_topic = max_pages_per_topic

        self.github_token = github_token or os.getenv("GITHUB_TOKEN")

        self.session = requests.Session()
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=50,
            pool_maxsize=50
        )
        self.session.mount("https://", adapter)

        self.api_headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "FastScraper/3.0"
        }

        if self.github_token:
            self.api_headers["Authorization"] = f"Bearer {self.github_token}"

        self.cache = {}

    # ======================================================
    # SAFE REQUEST
    # ======================================================
    def get_html(self, url):
        try:
            r = self.session.get(url, timeout=15)

            if r.status_code == 200:
                return r.text

            if r.status_code in [403, 429]:
                print("[RATE LIMIT HTML]")
                time.sleep(2)
                return None

            return None
        except:
            return None

    def get_json(self, url):
        if url in self.cache:
            return self.cache[url]

        try:
            r = self.session.get(url, headers=self.api_headers, timeout=15)

            if r.status_code == 200:
                data = r.json()
                self.cache[url] = data
                return data

            if r.status_code == 403:
                print("[RATE LIMIT API]")
                time.sleep(60)

        except:
            return None

        return None

    # ======================================================
    # CRAWL TOPICS (RESTORED)
    # ======================================================
    def get_topics(self, max_topics=50):
        url = f"{self.base_url}/topics"
        html = self.get_html(url)

        if not html:
            return []

        soup = BeautifulSoup(html, "html.parser")

        topics = set()
        for a in soup.select("a[href^='/topics/']"):
            t = a.get("href", "").split("/topics/")[-1]
            if t:
                topics.add(t)

        return list(topics)[:max_topics]

    # ======================================================
    # EXTRACT REPOS FROM TOPIC PAGE
    # ======================================================
    def crawl_topic_repos(self, topic):
        repos = set()

        for page in range(1, self.max_pages_per_topic + 1):
            url = f"{self.base_url}/topics/{topic}?page={page}"
            html = self.get_html(url)

            if not html:
                break

            soup = BeautifulSoup(html, "html.parser")

            for a in soup.select("a[href]"):
                href = a.get("href", "")

                parts = href.strip("/").split("/")

                if len(parts) == 2:
                    owner, repo = parts

                    if owner and repo and owner not in ["topics", "explore"]:
                        repos.add(urljoin(self.base_url, href))

            time.sleep(self.delay)

        return repos

    # ======================================================
    # FULL CRAWLER
    # ======================================================
    def collect_repos(self):
        print("\n[CRAWLING TOPICS...]")

        topics = self.get_topics()
        all_repos = set()

        for t in topics:
            print(f"[TOPIC] {t}")
            repos = self.crawl_topic_repos(t)

            all_repos.update(repos)

            print(f"  -> {len(repos)} repos found")

            if len(all_repos) > 1000:
                break

        return list(all_repos)

    # ======================================================
    # API SCRAPER
    # ======================================================
    def scrape_repo(self, url):
        parts = urlparse(url).path.strip("/").split("/")
        if len(parts) != 2:
            return None

        owner, repo = parts

        base = f"{self.api_url}/repos/{owner}/{repo}"

        data = self.get_json(base)
        if not data:
            return None

        readme = ""
        r = self.get_json(f"{base}/readme")

        if r and r.get("content"):
            try:
                readme = base64.b64decode(r["content"]).decode("utf-8", errors="ignore")[:15000]
            except:
                pass

        return {
            "url": url,
            "name": data.get("name"),
            "full_name": data.get("full_name"),
            "description": data.get("description"),
            "stars": data.get("stargazers_count", 0),
            "forks": data.get("forks_count", 0),
            "language": data.get("language"),
            "topics": data.get("topics", []),
            "created_at": data.get("created_at"),
            "updated_at": data.get("updated_at"),
            "readme": readme,
            "readme_length": len(readme)
        }

    # ======================================================
    # PARALLEL SCRAPING
    # ======================================================
    def run(self):
        repos = self.collect_repos()

        print(f"\n[FOUND] {len(repos)} repositories\n")

        results = []
        seen = set()

        def worker(url):
            if url in seen:
                return None
            return self.scrape_repo(url)

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [executor.submit(worker, r) for r in repos]

            for i, f in enumerate(as_completed(futures), 1):
                data = f.result()

                if data:
                    results.append(data)
                    seen.add(data["url"])

                if i % 20 == 0:
                    self.save(results)
                    print(f"[AUTO-SAVE] {len(results)}")

        self.save(results)

        print(f"\nDONE → {len(results)} repos saved")

    # ======================================================
    # SAVE
    # ======================================================
    def save(self, data):
        with open(self.output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)


# ======================================================
# MAIN
# ======================================================
if __name__ == "__main__":
    scraper = FastGitHubScraper(
        max_workers=4,
        delay=0.1,
        max_pages_per_topic=5
    )

    scraper.run()