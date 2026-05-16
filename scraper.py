import requests
from bs4 import BeautifulSoup
import json
import time
from urllib.parse import urljoin
from urllib.robotparser import RobotFileParser


class GitHubScraper:

    def __init__(self):

        self.base_url = "https://github.com"

        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (X11; Linux x86_64) "
                "AppleWebKit/537.36 "
                "(KHTML, like Gecko) "
                "Chrome/120.0 Safari/537.36"
            )
        }

        self.rp = self.load_robots()

    # =========================
    # ROBOTS
    # =========================
    def load_robots(self):

        rp = RobotFileParser()

        try:
            rp.set_url(f"{self.base_url}/robots.txt")
            rp.read()
            return rp
        except:
            return None

    # =========================
    # SAFE REQUEST
    # =========================
    def fetch(self, url):

        try:

            if self.rp and not self.rp.can_fetch("*", url):
                print(f"[BLOCKED] {url}")
                return None

            r = requests.get(url, headers=self.headers, timeout=15)

            if r.status_code == 200:
                return r.text

            if r.status_code == 429:
                print("[RATE LIMIT] sleeping 60s...")
                time.sleep(60)
                return None

            return None

        except Exception as e:
            print(f"[ERROR] {url} -> {e}")
            return None

    # =========================
    # ALL TOPICS
    # =========================
    def get_all_topics(self):

        url = f"{self.base_url}/topics"

        html = self.fetch(url)

        if not html:
            return []

        soup = BeautifulSoup(html, "html.parser")

        topics = set()

        for link in soup.select("a[href^='/topics/']"):

            href = link.get("href")

            if not href:
                continue

            topic = href.split("/topics/")[-1].split("?")[0]

            if topic:
                topics.add(topic)

        return list(topics)

    # =========================
    # REPO COLLECTION
    # =========================
    def collect_repos(self, topics, max_repos=5000):

        repo_urls = set()

        print("\nCollecting repositories...\n")

        for topic in topics:

            print(f"\n[TOPIC] {topic}")

            page = 1

            while True:

                url = f"{self.base_url}/topics/{topic}?page={page}"

                html = self.fetch(url)

                if not html:
                    break

                soup = BeautifulSoup(html, "html.parser")

                articles = soup.find_all("article")

                if not articles:
                    break

                for article in articles:

                    for link in article.select("h3 a"):

                        href = link.get("href")

                        if href and href.count("/") == 2:

                            full = urljoin(self.base_url, href)
                            repo_urls.add(full)

                print(f"  page {page} -> {len(repo_urls)} repos")

                page += 1

                time.sleep(1)

                if len(repo_urls) >= max_repos:
                    return list(repo_urls)

        return list(repo_urls)

    # =========================
    # NUMBER PARSER
    # =========================
    def parse_number(self, text):

        if not text:
            return 0

        text = text.lower().replace(",", "").strip()

        try:
            if "k" in text:
                return int(float(text.replace("k", "")) * 1000)

            if "m" in text:
                return int(float(text.replace("m", "")) * 1000000)

            return int(text)

        except:
            return 0

    # =========================
    # LANGUAGE EXTRACTION (FIXED)
    # =========================
    def extract_languages(self, soup):

        languages = {}

        # METHOD 1: modern GitHub UI
        blocks = soup.select("li.d-inline")

        for b in blocks:

            lang = b.select_one("span.color-fg-default")

            if lang:

                name = lang.get_text(strip=True)

                if name:
                    languages[name] = 1

        # METHOD 2: fallback scan
        if not languages:

            known = [
                "Python", "JavaScript", "TypeScript",
                "Java", "C++", "C", "Go",
                "Rust", "PHP", "C#"
            ]

            text = soup.get_text(" ", strip=True)

            for k in known:

                if k in text:
                    languages[k] = 1

        return languages

    # =========================
    # SCRAPE SINGLE REPO
    # =========================
    def scrape_repo(self, url):

        html = self.fetch(url)

        if not html:
            return None

        soup = BeautifulSoup(html, "html.parser")

        data = {
            "url": url,
            "title": "",
            "description": "",
            "stars": 0,
            "forks": 0,
            "watchers": 0,
            "issues": 0,
            "language": None,
            "languages": {},
            "topics": [],
            "readme": ""
        }

        # =====================
        # TITLE
        # =====================
        title = soup.select_one("strong.mr-2.flex-self-stretch a")

        if title:
            data["title"] = title.get_text(strip=True)

        if not data["title"]:
            t = soup.find("title")
            if t:
                data["title"] = t.get_text(strip=True).split(":")[0]

        # =====================
        # DESCRIPTION
        # =====================
        meta = soup.find("meta", {"name": "description"})
        if meta:
            data["description"] = meta.get("content", "").strip()

        # =====================
        # STATS
        # =====================
        for a in soup.find_all("a"):

            href = a.get("href", "")
            text = a.get_text(strip=True)

            if "/stargazers" in href:
                data["stars"] = self.parse_number(text)

            elif "/forks" in href:
                data["forks"] = self.parse_number(text)

            elif "/watchers" in href:
                data["watchers"] = self.parse_number(text)

            elif "/issues" in href:
                data["issues"] = self.parse_number(text)

        # =====================
        # LANGUAGES (FIXED)
        # =====================
        data["languages"] = self.extract_languages(soup)

        if data["languages"]:
            data["language"] = list(data["languages"].keys())[0]

        # =====================
        # TOPICS (FIXED)
        # =====================
        topics = soup.select("a[href*='/topics/']")

        data["topics"] = list(set(
            t.get_text(strip=True)
            for t in topics
            if t.get_text(strip=True)
        ))

        # =====================
        # README
        # =====================
        readme = soup.find("article")

        if readme:
            data["readme"] = readme.get_text(" ", strip=True)[:2000]

        return data

    # =========================
    # RUN
    # =========================
    def run(self, max_repos=5000):

        topics = self.get_all_topics()

        print(f"\nFound {len(topics)} topics\n")

        repos = self.collect_repos(topics, max_repos)

        print(f"\nCollected {len(repos)} repos\n")

        results = []

        for i, repo in enumerate(repos):

            print(f"[{i+1}/{len(repos)}] {repo}")

            data = self.scrape_repo(repo)

            if data:
                results.append(data)

            # auto-save
            if (i + 1) % 20 == 0:

                with open("data.json", "w", encoding="utf-8") as f:
                    json.dump(results, f, indent=4, ensure_ascii=False)

                print("[AUTO-SAVED]")

            time.sleep(1.2)

        with open("data.json", "w", encoding="utf-8") as f:
            json.dump(results, f, indent=4, ensure_ascii=False)

        print(f"\nDONE: {len(results)} repositories saved")


# =========================
# EXECUTE
# =========================
if __name__ == "__main__":

    scraper = GitHubScraper()
    scraper.run(max_repos=5000)