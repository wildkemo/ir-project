# Scraper Technical Documentation (`scraper.py`)

This document provides a detailed explanation of the `scraper.py` script, which serves as the **Data Collection** layer of the Web Intelligence Data Pipeline.

## Overview
The script is designed to collect data from GitHub by discovering repositories across various technical topics and extracting their descriptions. It aims to collect exactly 200 records to satisfy the project requirements.

## Dependencies
- `requests`: Handles HTTP requests to GitHub.
- `BeautifulSoup` (from `bs4`): Parses HTML content to extract specific data points.
- `json`: Manages structured data storage in `data.json`.
- `time`: Implements delays to respect GitHub's rate limits and `robots.txt` principles.
- `urllib.parse.urljoin`: Ensures absolute URLs are constructed correctly from relative paths.

## Component Breakdown

### 1. `get_repo_details(url, headers)`
This function is responsible for extracting the "content" (description) of a specific repository.
- **Logic**:
    - Fetches the repository's main page.
    - **Primary Source**: Looks for the `<meta name="description">` tag.
    - **Cleaning**: GitHub often appends boilerplate text like *"Contribute to ... development by creating an account"*. The script identifies and removes this to keep only the actual description.
    - **Secondary Source**: If the meta tag is missing, it searches for a `<p>` tag with the class `f4 my-3` (the "About" section in the GitHub UI).
    - **Fallback**: Returns `None` if no description is found, allowing the main loop to apply a default value.

### 2. `scrape_github_data()`
The main orchestrator of the scraping process, divided into two distinct phases.

#### Phase 1: Discovery (Link Gathering)
- **Topics**: Iterates through a list of topics (`open-source`, `machine-learning`, `data-science`, `web-development`, `python`).
- **Pagination**: Navigates through multiple pages per topic until 200 unique repository URLs are found.
- **Extraction**: Targets `<article>` tags and extracts the repository title and its absolute URL.

#### Phase 2: Scanning (Content Extraction)
- **Detail Retrieval**: Iterates through the 200 discovered URLs and calls `get_repo_details`.
- **Throttling**: Implements a **1.2-second delay** between requests to avoid being flagged as a bot and to minimize server load.
- **Data Persistence**:
    - Saves progress to `data.json` every 20 records. This ensures that if the script is interrupted, most data is preserved.
    - Performs a final save once all 200 records are processed.

## Detailed Execution Flow

1.  **Initialization**:
    - The script starts in the `__main__` block and calls `scrape_github_data()`.
    - It defines a `headers` dictionary with a `User-Agent` to simulate a real browser, reducing the likelihood of being blocked.
    - An empty list `repo_urls` is initialized to store the discovered links.

2.  **The Discovery Loop (Step 1)**:
    - The script enters a `while` loop that continues until it has 200 URLs or runs out of topics.
    - For each topic (e.g., 'machine-learning'), it constructs a URL: `https://github.com/topics/{topic}?page={page}`.
    - It uses `requests.get` to fetch the HTML. If the page fails to load or contains no repositories, it moves to the next topic and resets the page counter.
    - **Parsing**: It finds all `<article>` tags. Inside each article, it looks for the `<h3>` containing the repository links.
    - **Selection**: It specifically targets the *last* `<a>` tag in the `<h3>` (which is the repository name link, not the user/owner link).
    - **Uniqueness Check**: Before adding a URL, it checks if the URL is already in `repo_urls` to avoid duplicates across different topics or pages.
    - **Throttling**: It waits for **1 second** between page requests.

3.  **The Content Scanning Loop (Step 2)**:
    - Once 200 links are found, it iterates through each one.
    - For every link, it calls `get_repo_details(url)`.
    - **String Cleaning**: Inside `get_repo_details`, it fetches the page and extracts the meta description. It specifically checks for the string `". Contribute to"` and splits it, keeping only the part *before* it. This removes the generic GitHub "sign up to contribute" boilerplate.
    - **Defaulting**: If no description is found after trying both the meta tag and the 'About' paragraph, it creates a default description: `"Repository focusing on [Title]"`.
    - **Incremental Saving**: Every 20 repositories, it opens `data.json` and writes the current `final_data` list. This is a "fail-safe" mechanism against network interruptions or crashes.

4.  **Finalization**:
    - After processing all 200 repositories, it performs a final write to `data.json` to ensure all data is captured.
    - The script prints a summary message and exits.

## Data Schema
The output `data.json` follows a standardized schema:
```json
{
    "title": "Repository Name",
    "content": "Extracted description or fallback text",
    "url": "https://github.com/user/repo"
}
```

## Resilience Features
- **Timeouts**: All network requests have a 10-second timeout to prevent the script from hanging on slow connections.
- **Error Handling**: `try-except` blocks wrap both the discovery and scanning phases to handle network errors or unexpected HTML structure changes gracefully.
- **User-Agent**: Uses a standard browser User-Agent string to ensure GitHub serves the correct HTML content.
