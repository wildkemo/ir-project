# 🧠 AI-Powered Open Source Discovery Platform
### *Web Intelligence Data Pipeline & Personalized Search Engine*

This project is a high-performance **Web Intelligence Data Pipeline** developed for the **CS313x – Information Retrieval & Data Analysis** course. It implements a full-cycle system for collecting, processing, and analyzing open-source repository data from GitHub, featuring a **Personalized Discovery Engine** that tailors search results to user-specific profiles and goals.

---

## 🚀 System Overview

The platform transforms raw web data into actionable intelligence. It combines classical Information Retrieval (BM25) with a sophisticated personalization layer to help users discover repositories that match their skill level, goals, and technical preferences.

### **Core Data Pipeline**
1.  **Ethical Scraping:** Multi-page collection of repository metadata with full `robots.txt` compliance.
2.  **Advanced NLP Processing:** Text cleaning using Porter Stemming, WordNet Lemmatization, and field-weighted tokenization.
3.  **Personalized Discovery:** 
    - **User Profiling:** Captures technical preferences (Language, Project Type) and intent (Learning vs. Contribution).
    - **Hybrid Ranking:** Combines Query Relevance (BM25) with Profile Alignment to deliver personalized results.
4.  **Data Analytics:** Statistical exploration of vocabulary density, language distribution, and repository trends.

---

## 🛠️ Technical Stack

- **Core:** Python 3.x, JSON
- **NLP:** NLTK (Stemming, Lemmatization, Stopwords)
- **IR & Recommendation:** BM25 Ranking, Multi-dimensional Similarity Scoring
- **Scraping:** BeautifulSoup4, Requests, RobotParser

---

## 📂 Project Structure

```bash
ir-project/
├── scraper.py          # Data Collection: Ethical GitHub crawler (respects robots.txt)
├── data.json           # Raw Storage: 200+ raw repository records
├── process.py          # NLP Layer: Stemming, Lemmatization, & Field-Weighting
├── processed.json      # IR Storage: Tokenized & weighted document representation
├── smart_profile_recommender_v2.py # Intelligence Layer: Personalized Search & Discovery
├── analysis.py         # Analytics: Dataset statistics & keyword profiling
├── Pipeline.md         # Technical Specification: Detailed algorithmic flow
├── app_arch.md         # Architecture Roadmap: Future system expansion
└── SCRAPER_DOCUMENTATION.md # Scraper technical deep-dive
```

---

## ⚙️ Execution Flow

To run the complete pipeline from scratch:

1.  **Phase 1: Collection**
    ```bash
    python scraper.py
    ```
    *Extracts ~200 repository descriptions. Respects rate limits and robots.txt.*

2.  **Phase 2: Processing**
    ```bash
    python process.py
    ```
    *Performs tokenization, stemming, and lemmatization. Generates boost signals.*

3.  **Phase 3: Intelligence & Analytics**
    ```bash
    python analysis.py
    ```
    *Generates a statistical report on vocabulary and repository trends.*

4.  **Phase 4: Personalized Discovery**
    ```bash
    python smart_profile_recommender_v2.py
    ```
    *Builds your user profile and provides personalized recommendations and search.*

---

## 🔍 Key Intelligence Features

### **1. Multi-Dimensional User Profiling**
The engine doesn't just look for keywords; it understands who you are:
- **Intent Tracking:** Distinguishes between users wanting to *learn* (tutorials, guides) vs. those wanting to *contribute* (active issues, contribution guides).
- **Skill Alignment:** Matches repository complexity with the user's skill level.
- **Dynamic Options:** Profile options are generated directly from the dataset, ensuring recommendations are always grounded in available data.

### **2. Personalized Search & Ranking**
- **BM25 Integration:** Uses the industry-standard probabilistic model for core relevance.
- **Query Expansion:** Automatically expands domain-specific terms (e.g., "Web" -> "Frontend", "Backend", "React") to ensure high recall.
- **Reasoning Engine:** For every recommendation, the system provides a "Why" explanation (e.g., "Matches your selected project type").

### **3. Ethical & Robust Scraping**
- **Dynamic Compliance:** Real-time checking of `robots.txt` paths.
- **Fail-Safe Persistence:** Incremental saves ensure the corpus is protected during long crawls.

---

## 🎯 Academic Requirements Mapping

- [x] **Requirement 1:** Multi-page scraping (200 records) + `robots.txt` compliance.
- [x] **Requirement 2:** Structured JSON storage with consistent schema.
- [x] **Requirement 3:** NLP Processing (Tokenization, Stemming, Lemmatization).
- [x] **Requirement 4:** Data Understanding (Vocab density, Avg length, TF).
- [x] **Requirement 5:** Functional Product (Personalized Search Engine).
- [x] **Requirement 6:** AI Integration (Personalized Recommendation Logic).

---

*Developed for the Web Intelligence & Information Retrieval Course.*
