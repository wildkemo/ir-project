# GEMINI.md

## Project Overview
This project is a **Web Intelligence Product** developed for the **CS313x – Information Retrieval & Data Analysis** course. It implements a complete data pipeline designed to collect, process, and analyze web-based textual data, integrating AI-powered sentiment analysis into a functional search interface.

**Core Pipeline:**
1.  **Scraping:** Multi-page collection of 50–200 records (respecting `robots.txt`).
2.  **Storage:** Structured data storage in `data.json`.
3.  **Processing:** Tokenization, normalization, and stopword removal to produce `processed.json`.
4.  **Analysis:** Keyword frequency and statistical dataset exploration.
5.  **Search:** IR-style keyword-based retrieval.
6.  **AI Feature:** Sentiment analysis (Positive/Negative/Neutral classification).
7.  **Interface:** CLI-based user interaction.

## Building and Running
The implementation follows a sequential execution flow as defined in `EXCUTION.md`:

1.  **Scrape Data:** `python scraper.py`
2.  **Process Data:** `python process.py`
3.  **Run Analytics (Optional):** `python analysis.py`
4.  **Launch Interface:** `python cli.py` (Entry point for search and AI insights)

*Note: The project is currently in the architectural setup phase. Use `EXCUTION.md` as the primary implementation blueprint.*

## Development Conventions
- **Minimalism:** Adhere to a "no over-engineering" philosophy; focus on satisfying course requirements with clean, functional code.
- **Standardized Schema:** Ensure `data.json` and `processed.json` maintain consistent fields (e.g., `title`, `content`, `url`).
- **Data Integrity:** Implement robust handling for missing or noisy data during the processing layer.
- **AI Integration:** Use a straightforward sentiment analysis approach as the primary AI-powered feature.
