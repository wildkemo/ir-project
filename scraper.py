import os
import re
import json
import time
import base64
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser


class GitHubScraper:
    """
    Hybrid GitHub repository scraper.

    Strategy:
    1. Use GitHub REST API for stable repository data.
    2. Use GitHub HTML page scraping as fallback.
    3. Extract README using API first, rendered HTML second.
    """

    def __init__(
        self,
        github_token=None,
        output_file="data.json",
        delay=1.0,
        max_readme_chars=20000
    ):
        self.base_url = "https://github.com"
        self.api_url = "https://api.github.com"

        self.output_file = output_file
        self.delay = delay
        self.max_readme_chars = max_readme_chars

        self.github_token = github_token or os.getenv("GITHUB_TOKEN")

        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (X11; Linux x86_64) "
                "AppleWebKit/537.36 "
                "(KHTML, like Gecko) "
                "Chrome/120.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }

        self.api_headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "OpenSourceProjectAnalyzer/1.0",
        }

        if self.github_token:
            self.api_headers["Authorization"] = f"Bearer {self.github_token}"

        self.rp = self.load_robots()

    # ======================================================
    # ROBOTS
    # ======================================================
    def load_robots(self):
        rp = RobotFileParser()
        try:
            rp.set_url(f"{self.base_url}/robots.txt")
            rp.read()
            return rp
        except Exception:
            return None

    # ======================================================
    # SAFE HTML REQUEST
    # ======================================================
    def fetch_html(self, url):
        try:
            if self.rp and not self.rp.can_fetch("*", url):
                print(f"[ROBOTS BLOCKED] {url}")
                return None

            response = requests.get(
                url,
                headers=self.headers,
                timeout=20
            )

            if response.status_code == 200:
                return response.text

            if response.status_code in [403, 429]:
                print(f"[HTML RATE LIMITED] {url}")
                time.sleep(60)
                return None

            print(f"[HTML ERROR] {response.status_code} -> {url}")
            return None

        except Exception as e:
            print(f"[HTML EXCEPTION] {url} -> {e}")
            return None

    # ======================================================
    # SAFE API REQUEST
    # ======================================================
    def fetch_api_json(self, url):
        try:
            response = requests.get(
                url,
                headers=self.api_headers,
                timeout=20
            )

            remaining = response.headers.get("x-ratelimit-remaining")
            reset = response.headers.get("x-ratelimit-reset")

            if remaining == "0" and reset:
                sleep_for = max(int(reset) - int(time.time()) + 5, 5)
                print(f"[API RATE LIMIT] sleeping {sleep_for}s")
                time.sleep(sleep_for)

            if response.status_code == 200:
                return response.json()

            if response.status_code == 404:
                return None

            if response.status_code in [403, 429]:
                print(f"[API LIMITED] {response.status_code} -> {url}")
                time.sleep(60)
                return None

            print(f"[API ERROR] {response.status_code} -> {url}")
            return None

        except Exception as e:
            print(f"[API EXCEPTION] {url} -> {e}")
            return None

    # ======================================================
    # PARSE REPO URL
    # ======================================================
    def parse_repo_url(self, url):
        """
        Converts:
        https://github.com/owner/repo
        into:
        owner, repo
        """
        parsed = urlparse(url)
        parts = parsed.path.strip("/").split("/")

        if len(parts) < 2:
            return None, None

        owner = parts[0]
        repo = parts[1].replace(".git", "")

        invalid_paths = {
            "topics", "explore", "marketplace", "features",
            "enterprise", "settings", "login", "signup"
        }

        if owner in invalid_paths:
            return None, None

        return owner, repo

    # ======================================================
    # NUMBER PARSER
    # ======================================================
    def parse_number(self, text):
        if not text:
            return 0

        text = text.lower()
        text = text.replace(",", "").strip()
        text = re.sub(r"[^0-9.km]", "", text)

        try:
            if text.endswith("k"):
                return int(float(text[:-1]) * 1_000)
            if text.endswith("m"):
                return int(float(text[:-1]) * 1_000_000)
            return int(float(text))
        except Exception:
            return 0

    # ======================================================
    # CLEAN TEXT
    # ======================================================
    def clean_text(self, text):
        if not text:
            return ""

        text = re.sub(r"\s+", " ", text)
        return text.strip()

    # ======================================================
    # GET TOPICS FROM /topics
    # ======================================================
    def get_all_topics(self, max_topics=100):
        url = f"{self.base_url}/topics"
        html = self.fetch_html(url)

        if not html:
            return []

        soup = BeautifulSoup(html, "html.parser")
        topics = set()

        for link in soup.select("a[href^='/topics/']"):
            href = link.get("href", "")
            topic = href.split("/topics/")[-1].split("?")[0].strip()

            if topic and "/" not in topic:
                topics.add(topic)

        topics = sorted(topics)

        if max_topics:
            topics = topics[:max_topics]

        return topics

    # ======================================================
    # COLLECT REPOSITORY URLS FROM TOPIC PAGES
    # ======================================================
    def collect_repos(self, topics, max_repos=5000, max_pages_per_topic=10):
        repo_urls = set()

        print("\nCollecting repositories...\n")

        for topic in topics:
            print(f"[TOPIC] {topic}")

            for page in range(1, max_pages_per_topic + 1):
                url = f"{self.base_url}/topics/{topic}?page={page}"
                html = self.fetch_html(url)

                if not html:
                    break

                soup = BeautifulSoup(html, "html.parser")

                # Current GitHub topic pages usually expose repos as /owner/repo links.
                for link in soup.select("a[href^='/']"):
                    href = link.get("href", "").strip()

                    if not href:
                        continue

                    parts = href.strip("/").split("/")

                    if len(parts) == 2:
                        owner, repo = parts

                        if self.is_probable_repo_path(owner, repo):
                            full_url = urljoin(self.base_url, href)
                            repo_urls.add(full_url)

                print(f"  page {page} -> {len(repo_urls)} repos")

                if len(repo_urls) >= max_repos:
                    return list(repo_urls)[:max_repos]

                time.sleep(self.delay)

        return list(repo_urls)[:max_repos]

    def is_probable_repo_path(self, owner, repo):
        invalid = {
            "features", "topics", "collections", "events",
            "marketplace", "pricing", "login", "signup",
            "settings", "notifications", "new"
        }

        if owner in invalid:
            return False

        if repo in invalid:
            return False

        if repo.endswith(".git"):
            repo = repo[:-4]

        return bool(owner and repo)

    # ======================================================
    # API: REPOSITORY METADATA
    # ======================================================
    def get_repo_api_data(self, owner, repo):
        url = f"{self.api_url}/repos/{owner}/{repo}"
        data = self.fetch_api_json(url)

        if not data:
            return {}

        return {
            "id": data.get("id"),
            "node_id": data.get("node_id"),
            "owner": owner,
            "name": data.get("name"),
            "full_name": data.get("full_name"),
            "url": data.get("html_url"),
            "api_url": data.get("url"),
            "description": data.get("description") or "",
            "homepage": data.get("homepage") or "",
            "language": data.get("language"),
            "stars": data.get("stargazers_count", 0),
            "forks": data.get("forks_count", 0),
            "watchers": data.get("watchers_count", 0),
            "open_issues": data.get("open_issues_count", 0),
            "size": data.get("size", 0),
            "default_branch": data.get("default_branch"),
            "license": (
                data.get("license", {}).get("spdx_id")
                if data.get("license")
                else None
            ),
            "topics": data.get("topics", []),
            "created_at": data.get("created_at"),
            "updated_at": data.get("updated_at"),
            "pushed_at": data.get("pushed_at"),
            "clone_url": data.get("clone_url"),
            "ssh_url": data.get("ssh_url"),
            "visibility": data.get("visibility"),
            "is_fork": data.get("fork", False),
            "is_archived": data.get("archived", False),
            "is_disabled": data.get("disabled", False),
            "network_count": data.get("network_count"),
            "subscribers_count": data.get("subscribers_count"),
        }

    # ======================================================
    # API: LANGUAGES
    # ======================================================
    def get_repo_languages(self, owner, repo):
        url = f"{self.api_url}/repos/{owner}/{repo}/languages"
        data = self.fetch_api_json(url)

        if not data:
            return {}

        return data

    # ======================================================
    # API: README
    # ======================================================
    def get_repo_readme(self, owner, repo):
        url = f"{self.api_url}/repos/{owner}/{repo}/readme"
        data = self.fetch_api_json(url)

        if not data:
            return ""

        content = data.get("content")

        if not content:
            return ""

        try:
            decoded = base64.b64decode(content).decode("utf-8", errors="ignore")
            return decoded[:self.max_readme_chars]
        except Exception:
            return ""

    # ======================================================
    # HTML FALLBACK: SCRAPE REPO PAGE
    # ======================================================
    def scrape_repo_html_fallback(self, repo_url):
        html = self.fetch_html(repo_url)

        if not html:
            return {}

        soup = BeautifulSoup(html, "html.parser")

        data = {
            "html_title": "",
            "html_description": "",
            "html_topics": [],
            "html_stars": 0,
            "html_forks": 0,
            "html_watchers": 0,
            "html_issues": 0,
            "html_language": None,
            "html_languages": {},
            "html_readme": "",
        }

        # -------------------------
        # Title fallback
        # -------------------------
        og_title = soup.find("meta", property="og:title")
        if og_title:
            data["html_title"] = self.clean_text(og_title.get("content", ""))

        if not data["html_title"]:
            title = soup.find("title")
            if title:
                data["html_title"] = self.clean_text(title.get_text()).split(":")[0]

        # -------------------------
        # Description fallback
        # -------------------------
        meta_desc = soup.find("meta", attrs={"name": "description"})
        if meta_desc:
            data["html_description"] = self.clean_text(meta_desc.get("content", ""))

        if not data["html_description"]:
            about = soup.select_one("p.f4.my-3")
            if about:
                data["html_description"] = self.clean_text(about.get_text(" "))

        # -------------------------
        # Stats fallback
        # Current GitHub often uses links ending in stargazers/forks/watchers/issues.
        # This avoids depending on exact class names.
        # -------------------------
        for a in soup.find_all("a"):
            href = a.get("href", "")
            text = self.clean_text(a.get_text(" "))

            if href.endswith("/stargazers") or "/stargazers" in href:
                value = self.parse_number(text)
                if value:
                    data["html_stars"] = value

            elif href.endswith("/forks") or "/forks" in href:
                value = self.parse_number(text)
                if value:
                    data["html_forks"] = value

            elif href.endswith("/watchers") or "/watchers" in href:
                value = self.parse_number(text)
                if value:
                    data["html_watchers"] = value

            elif href.endswith("/issues") or "/issues" in href:
                value = self.parse_number(text)
                if value:
                    data["html_issues"] = value

        # -------------------------
        # Topics fallback
        # -------------------------
        topic_values = set()

        for topic_link in soup.select("a[href*='/topics/']"):
            topic_text = self.clean_text(topic_link.get_text(" "))
            href = topic_link.get("href", "")

            if topic_text and "/topics/" in href:
                topic_values.add(topic_text.lower())

        data["html_topics"] = sorted(topic_values)

        # -------------------------
        # Languages fallback
        # Tries several GitHub layout patterns.
        # -------------------------
        languages = {}

        language_selectors = [
            "li.d-inline span.color-fg-default",
            "a[href*='/search?l='] span",
            "[data-ga-click*='Repository, language stats search click'] span",
        ]

        for selector in language_selectors:
            for item in soup.select(selector):
                name = self.clean_text(item.get_text(" "))
                if name and len(name) <= 30:
                    languages[name] = languages.get(name, 0) + 1

        data["html_languages"] = languages

        if languages:
            data["html_language"] = list(languages.keys())[0]

        # -------------------------
        # README fallback
        # Current GitHub rendered README is usually inside article.markdown-body.
        # -------------------------
        readme_candidates = [
            "article.markdown-body",
            "div.markdown-body",
            "article",
        ]

        for selector in readme_candidates:
            readme = soup.select_one(selector)
            if readme:
                readme_text = self.clean_text(readme.get_text(" "))
                if len(readme_text) > len(data["html_readme"]):
                    data["html_readme"] = readme_text[:self.max_readme_chars]

        return data

    # ======================================================
    # MERGE API + HTML FALLBACK
    # ======================================================
    def scrape_repo(self, repo_url):
        owner, repo = self.parse_repo_url(repo_url)

        if not owner or not repo:
            return None

        print(f"[SCRAPING] {owner}/{repo}")

        api_data = self.get_repo_api_data(owner, repo)
        languages = self.get_repo_languages(owner, repo)
        readme = self.get_repo_readme(owner, repo)
        html_data = self.scrape_repo_html_fallback(repo_url)

        result = {
            "owner": owner,
            "repo": repo,
            "full_name": f"{owner}/{repo}",
            "url": repo_url,

            # Main stable data
            **api_data,

            # Extra stable data
            "languages": languages,
            "readme": readme,
            "readme_length": len(readme),
            "has_readme": bool(readme),

            # Keep HTML fallback for debugging and missing values
            "html_fallback": html_data,
        }

        # Fill missing fields from HTML fallback
        if not result.get("description"):
            result["description"] = html_data.get("html_description", "")

        if not result.get("topics"):
            result["topics"] = html_data.get("html_topics", [])

        if not result.get("language"):
            result["language"] = html_data.get("html_language")

        if not result.get("languages"):
            result["languages"] = html_data.get("html_languages", {})

        if not result.get("stars"):
            result["stars"] = html_data.get("html_stars", 0)

        if not result.get("forks"):
            result["forks"] = html_data.get("html_forks", 0)

        if not result.get("watchers"):
            result["watchers"] = html_data.get("html_watchers", 0)

        if not result.get("open_issues"):
            result["open_issues"] = html_data.get("html_issues", 0)

        if not result.get("readme"):
            result["readme"] = html_data.get("html_readme", "")
            result["readme_length"] = len(result["readme"])
            result["has_readme"] = bool(result["readme"])

        # Create searchable text for your IR system
        result["search_text"] = self.build_search_text(result)

        return result

    # ======================================================
    # BUILD SEARCHABLE DOCUMENT TEXT
    # ======================================================
    def build_search_text(self, repo):
        parts = [
            repo.get("full_name", ""),
            repo.get("name", ""),
            repo.get("description", ""),
            repo.get("language", "") or "",
            " ".join(repo.get("topics", []) or []),
            " ".join((repo.get("languages", {}) or {}).keys()),
            repo.get("license", "") or "",
            repo.get("readme", "") or "",
        ]

        return self.clean_text(" ".join(parts))

    # ======================================================
    # LOAD EXISTING DATA
    # ======================================================
    def load_existing_results(self):
        if not os.path.exists(self.output_file):
            return []

        try:
            with open(self.output_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    # ======================================================
    # SAVE DATA
    # ======================================================
    def save_results(self, results):
        with open(self.output_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=4, ensure_ascii=False)

    # ======================================================
    # RUN
    # ======================================================
    def run(
        self,
        max_repos=5000,
        max_topics=100,
        max_pages_per_topic=10,
        custom_topics=None
    ):
        if custom_topics:
            topics = custom_topics
        else:
            topics = self.get_all_topics(max_topics=max_topics)

        print(f"\nFound {len(topics)} topics\n")

        repos = self.collect_repos(
            topics=topics,
            max_repos=max_repos,
            max_pages_per_topic=max_pages_per_topic
        )

        print(f"\nCollected {len(repos)} repository URLs\n")

        results = self.load_existing_results()
        existing_urls = {r.get("url") for r in results}

        for i, repo_url in enumerate(repos, start=1):
            if repo_url in existing_urls:
                print(f"[SKIP] already scraped: {repo_url}")
                continue

            print(f"\n[{i}/{len(repos)}] {repo_url}")

            data = self.scrape_repo(repo_url)

            if data:
                results.append(data)
                existing_urls.add(repo_url)

            if len(results) % 20 == 0:
                self.save_results(results)
                print("[AUTO-SAVED]")

            time.sleep(self.delay)

        self.save_results(results)

        print(f"\nDONE: {len(results)} repositories saved to {self.output_file}")


# ======================================================
# EXECUTE
# ======================================================
if __name__ == "__main__":
    scraper = GitHubScraper(
        output_file="data.json",
        delay=1.0,
        max_readme_chars=20000
    )

    scraper.run(
        max_repos=10,
        max_topics=1,
        max_pages_per_topic=5,

        # For more controlled scraping, you can use this instead:
        # custom_topics=[
        #     "python",
        #     "machine-learning",
        #     "javascript",
        #     "react",
        #     "api",
        #     "nlp",
        #     "data-science"
        # ]
    )