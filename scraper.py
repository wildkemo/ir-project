import os
import time
import json
import base64
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv

load_dotenv()

# Discovery limits (3× previous defaults: 50 topics × 5 pages, cap 2000 repos)
MAX_TOPICS = 150
MAX_PAGES_PER_TOPIC = 15
MAX_REPOS_COLLECTED = 6000

# Additional raw files merged into the dataset (never overwritten, only extended)
LEGACY_MERGE_FILES = ("data.json",)


def _normalize_repo_url(url: str | None) -> str | None:
    if not url:
        return None
    return url.strip().rstrip("/").lower()


def _repo_record_key(record: dict) -> str | None:
    url = _normalize_repo_url(record.get("url"))
    if url:
        return url
    full_name = (record.get("full_name") or "").strip().lower()
    if full_name and "/" in full_name:
        return f"https://github.com/{full_name}"
    owner = (record.get("owner") or "").strip()
    repo = (record.get("repo") or record.get("name") or "").strip()
    if owner and repo:
        return f"https://github.com/{owner}/{repo}".lower()
    return None


class FastGitHubScraper:
    def __init__(
        self,
        github_token=None,
        output_file="new_data.json",
        delay=0.5,
        max_workers=12,
        max_pages_per_topic=MAX_PAGES_PER_TOPIC,
        max_topics=MAX_TOPICS,
        max_repos_collected=MAX_REPOS_COLLECTED,
        legacy_merge_files=LEGACY_MERGE_FILES,
    ):
        self.base_url = "https://github.com"
        self.api_url = "https://api.github.com"

        self.output_file = output_file
        self.delay = delay
        self.max_workers = max_workers
        self.max_pages_per_topic = max_pages_per_topic
        self.max_topics = max_topics
        self.max_repos_collected = max_repos_collected
        self.legacy_merge_files = legacy_merge_files

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
        self._api_failures = 0
        self._api_rate_limits = 0
        self._auth_failed = False

    def reset_api_stats(self):
        self._api_failures = 0
        self._api_rate_limits = 0
        self._auth_failed = False

    # ======================================================
    # LOAD / MERGE EXISTING DATA
    # ======================================================
    def _load_json_list(self, path: str) -> list:
        if not os.path.isfile(path):
            return []
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data if isinstance(data, list) else []
        except (OSError, json.JSONDecodeError):
            print(f"[WARN] Could not read {path}, skipping.")
            return []

    def _load_processed_skip_urls(self) -> set[str]:
        """URLs already in processed.json — skip re-scraping them."""
        skip: set[str] = set()
        for record in self._load_json_list("processed.json"):
            key = _repo_record_key(record)
            if key:
                skip.add(key)
        return skip

    def load_existing_records(self) -> dict[str, dict]:
        """Merge prior raw scrapes; keyed by normalized repo URL."""
        merged: dict[str, dict] = {}

        for path in (self.output_file, *self.legacy_merge_files):
            for record in self._load_json_list(path):
                if not isinstance(record, dict):
                    continue
                key = _repo_record_key(record)
                if key:
                    merged[key] = record

        return merged

    def known_repo_urls(self, existing: dict[str, dict] | None = None) -> set[str]:
        existing = existing if existing is not None else self.load_existing_records()
        known = set(existing.keys())
        known.update(self._load_processed_skip_urls())
        return known

    def merge_records(self, existing: dict[str, dict], new_records: list[dict]) -> list[dict]:
        for record in new_records:
            key = _repo_record_key(record)
            if key:
                existing[key] = record
        return list(existing.values())

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

            if r.status_code == 401:
                if not self._auth_failed:
                    self._auth_failed = True
                    print(
                        "\n[ERROR] GitHub API rejected your token (401 Bad credentials).\n"
                        "        Update GITHUB_TOKEN in .env with a valid Personal Access Token.\n"
                        "        Create one at: https://github.com/settings/tokens\n"
                    )
                self._api_failures += 1
                return None

            if r.status_code in (403, 429):
                self._api_rate_limits += 1
                if self._api_rate_limits == 1 or self._api_rate_limits % 25 == 0:
                    print(f"[RATE LIMIT API] ({self._api_rate_limits} hits) — waiting 60s…")
                time.sleep(60)

            else:
                self._api_failures += 1

        except Exception:
            self._api_failures += 1
            return None

        return None

    # ======================================================
    # CRAWL TOPICS (RESTORED)
    # ======================================================
    def get_topics(self, max_topics=None):
        max_topics = max_topics if max_topics is not None else self.max_topics
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
    def collect_repos(self, known_urls: set[str] | None = None):
        print("\n[CRAWLING TOPICS...]")

        known_urls = known_urls or set()
        topics = self.get_topics()
        all_repos: set[str] = set()
        new_repos: set[str] = set()

        for t in topics:
            print(f"[TOPIC] {t}")
            repos = self.crawl_topic_repos(t)

            all_repos.update(repos)
            for repo_url in repos:
                normalized = _normalize_repo_url(repo_url)
                if normalized and normalized not in known_urls:
                    new_repos.add(repo_url)

            print(f"  -> {len(repos)} repos on page(s), {len(new_repos)} new (not in dataset)")

            if len(new_repos) >= self.max_repos_collected:
                print(f"  -> reached new-repo cap ({self.max_repos_collected})")
                break

        return list(new_repos)

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
        self.reset_api_stats()
        existing = self.load_existing_records()
        known_urls = self.known_repo_urls(existing)

        if self.github_token:
            print("[AUTH] GitHub token found in .env")
        else:
            print(
                "[WARN] No GITHUB_TOKEN in .env — API limit is ~60 requests/hour.\n"
                "       Add a token: https://github.com/settings/tokens"
            )

        print(f"\n[EXISTING] {len(existing)} repos already in dataset")
        print(f"[SKIP]     {len(known_urls)} URLs will not be re-scraped\n")

        repos = self.collect_repos(known_urls)

        print(f"\n[FOUND] {len(repos)} new repositories to scrape\n")

        if not repos:
            print("No new repositories discovered. Saving merged dataset as-is.")
            self.save(list(existing.values()))
            return

        new_results: list[dict] = []
        seen_this_run: set[str] = set()
        failed_scrapes = 0

        def worker(url):
            nonlocal failed_scrapes
            if self._auth_failed:
                return None
            normalized = _normalize_repo_url(url)
            if not normalized or normalized in seen_this_run:
                return None
            seen_this_run.add(normalized)
            data = self.scrape_repo(url)
            if data is None:
                failed_scrapes += 1
            return data

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [executor.submit(worker, r) for r in repos]

            for i, f in enumerate(as_completed(futures), 1):
                if self._auth_failed and not new_results:
                    for pending in futures:
                        pending.cancel()
                    break

                data = f.result()

                if data:
                    new_results.append(data)

                if i % 20 == 0:
                    merged = self.merge_records(dict(existing), new_results)
                    self.save(merged)
                    print(
                        f"[AUTO-SAVE] {len(merged)} total "
                        f"({len(new_results)} new, {failed_scrapes} failed)"
                    )

        merged = self.merge_records(dict(existing), new_results)
        self.save(merged)

        if self._auth_failed:
            print(
                "\n[ABORT] Scraping stopped — fix GITHUB_TOKEN in .env and re-run.\n"
                f"        Discovered {len(repos)} URLs but saved 0 new repos."
            )
        elif failed_scrapes and not new_results:
            print(
                f"\n[WARN] All {failed_scrapes} API requests failed. "
                "Check your token or rate limit."
            )

        print(
            f"\nDONE → {len(merged)} repos total "
            f"({len(new_results)} added/updated this run, {failed_scrapes} failed)"
        )

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
        max_pages_per_topic=MAX_PAGES_PER_TOPIC,
        max_topics=MAX_TOPICS,
        max_repos_collected=MAX_REPOS_COLLECTED,
    )

    scraper.run()