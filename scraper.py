import requests
from bs4 import BeautifulSoup
import json
import time
from urllib.parse import urljoin
from urllib.robotparser import RobotFileParser


# =========================
# ROBOTS.TXT
# =========================
def get_robot_parser(url="https://github.com/robots.txt"):
    rp = RobotFileParser()
    try:
        rp.set_url(url)
        rp.read()
        return rp
    except:
        return None


# =========================
# SAFE REQUEST
# =========================
def fetch(url, headers):
    try:
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            return r.text
        return None
    except:
        return None


# =========================
# NUMBER PARSER
# =========================
def parse_number(text):
    if not text:
        return 0
    text = text.strip().lower().replace(",", "")

    try:
        if "k" in text:
            return int(float(text.replace("k", "")) * 1000)
        if "m" in text:
            return int(float(text.replace("m", "")) * 1000000)
        return int(text)
    except:
        return 0


# =========================
# REPO SCRAPER
# =========================
def get_repo_details(repo_url, headers, rp=None):

    if rp and not rp.can_fetch("*", repo_url):
        return None

    html = fetch(repo_url, headers)
    if not html:
        return None

    soup = BeautifulSoup(html, "html.parser")

    data = {
        "url": repo_url,
        "title": "",
        "description": "",
        "stars": 0,
        "forks": 0,
        "watchers": 0,
        "issues": 0,
        "language": None,
        "languages": {},
        "license": None,
        "topics": [],
        "contributors": [],
        "readme": "",
        "last_commit": None,
        "releases": [],
        "packages": []
    }

    # =========================
    # TITLE
    # =========================
    h1 = soup.find("strong", itemprop="name")
    if h1:
        data["title"] = h1.get_text(strip=True)

    # =========================
    # DESCRIPTION
    # =========================
    desc = soup.find("p", class_="f4 my-3")
    if desc:
        data["description"] = desc.get_text(strip=True)

    if not data["description"]:
        meta = soup.find("meta", {"name": "description"})
        if meta:
            data["description"] = meta.get("content", "")

    # =========================
    # STARS / FORKS / ISSUES
    # =========================
    counters = soup.find_all("a", class_="Link--muted")

    for c in counters:
        href = c.get("href", "")
        text = c.get_text(strip=True)

        if "/stargazers" in href:
            data["stars"] = parse_number(text)
        elif "/forks" in href:
            data["forks"] = parse_number(text)
        elif "/watchers" in href:
            data["watchers"] = parse_number(text)
        elif "/issues" in href:
            data["issues"] = parse_number(text)

    # =========================
    # LANGUAGE
    # =========================
    lang_items = soup.select("ul.list-style-none li")

    for li in lang_items:
        lang_name = li.find("span", class_="color-fg-default")
        if lang_name:
            name = lang_name.get_text(strip=True)
            data["languages"][name] = 1

    if data["languages"]:
        data["language"] = list(data["languages"].keys())[0]

    # =========================
    # TOPICS
    # =========================
    data["topics"] = [
        t.get_text(strip=True)
        for t in soup.select("a.topic-tag")
    ]

    # =========================
    # LICENSE
    # =========================
    license_tag = soup.find("a", href=lambda x: x and "LICENSE" in x)
    if license_tag:
        data["license"] = license_tag.get_text(strip=True)

    # =========================
    # README
    # =========================
    readme = soup.find("div", id="readme")
    if readme:
        data["readme"] = readme.get_text(" ", strip=True)[:1500]

    # =========================
    # CONTRIBUTORS
    # =========================
    contrib_html = fetch(repo_url + "/graphs/contributors", headers)
    if contrib_html:
        c_soup = BeautifulSoup(contrib_html, "html.parser")
        users = c_soup.select("h3 a")
        data["contributors"] = list(set(
            u.get_text(strip=True) for u in users if u.get_text(strip=True)
        ))[:20]

    # =========================
    # RELEASES
    # =========================
    rel_html = fetch(repo_url + "/releases", headers)
    if rel_html:
        r_soup = BeautifulSoup(rel_html, "html.parser")
        data["releases"] = [
            t.get_text(strip=True)
            for t in r_soup.select("a.Link--primary")[:5]
        ]

    # =========================
    # LAST ACTIVITY
    # =========================
    commit = soup.find("relative-time")
    if commit:
        data["last_commit"] = commit.get("datetime")

    return data


# =========================
# SCRAPE 200+ REPOS
# =========================
def scrape_github_data():

    topics = [
        "machine-learning",
        "python",
        "data-science",
        "web-development",
        "artificial-intelligence",
        "deep-learning",
        "computer-vision"
    ]

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    rp = get_robot_parser()

    repo_urls = set()

    print("Collecting repository URLs...")

    # =========================
    # MULTI-PAGE SCRAPING
    # =========================
    for topic in topics:
        for page in range(1, 6):  # 5 pages per topic
            url = f"https://github.com/topics/{topic}?page={page}"

            html = fetch(url, headers)
            if not html:
                continue

            soup = BeautifulSoup(html, "html.parser")
            articles = soup.find_all("article")

            if not articles:
                break

            for a in articles:
                link = a.find("a")
                if link and link.get("href"):
                    full = urljoin("https://github.com", link["href"])
                    repo_urls.add(full)

            time.sleep(1)

            if len(repo_urls) >= 250:
                break

        if len(repo_urls) >= 250:
            break

    repo_urls = list(repo_urls)[:220]

    print(f"Collected {len(repo_urls)} repositories")

    results = []

    # =========================
    # SCRAPE DETAILS
    # =========================
    for i, url in enumerate(repo_urls):

        print(f"[{i+1}/{len(repo_urls)}] {url}")

        data = get_repo_details(url, headers, rp)

        if data:
            results.append(data)

        time.sleep(1.2)

        # auto-save
        if i % 20 == 0:
            with open("data.json", "w", encoding="utf-8") as f:
                json.dump(results, f, indent=4)

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4)

    print(f"Done. Total repos: {len(results)}")


if __name__ == "__main__":
    scrape_github_data()