# 🧠 AI-Powered Open Source Discovery Platform
### *Web Intelligence Data Pipeline & Personalized Recommendation Engine*

This platform is a sophisticated **Web Intelligence Pipeline** designed for the **CS313x – Information Retrieval & Data Analysis** course. It goes beyond simple search by integrating a **Personalized Discovery Engine** that understands user intent, skill levels, and technical goals to curate the perfect open-source journey.

---

## 🚀 The Discovery Experience

Unlike traditional search engines, this platform treats every user uniquely. By answering a few smart profile questions, the engine builds a multi-dimensional persona to guide your discovery.

### **1. Smart Profiling**
- **Intent-Based:** Are you looking to *learn* from code or *contribute* to a community?
- **Skill-Aligned:** Filter repositories by complexity levels (Beginner, Intermediate, Advanced).
- **Technical Fit:** Select your preferred stack (Web, AI, Data Science, etc.) and programming languages.

### **2. Hybrid Intelligent Search**
- **Lexical Precision:** Uses the **BM25 algorithm** for industry-standard keyword relevance.
- **Domain-Aware Expansion:** The engine understands technical context (e.g., searching for "AI" automatically looks for "Machine Learning" and "Deep Learning").
- **Personalized Ranking:** Search results are re-ranked based on your profile, ensuring the most relevant projects for *you* appear first.

### **3. Explainable Recommendations**
- **Transparent AI:** Every result comes with a "Why" section explaining the alignment (e.g., "Suitable for your goal: Learning").

---

## 🛠️ Technical Implementation

- **Data Pipeline:** Ethical multi-page scraper with `robots.txt` compliance and boilerplate cleaning.
- **NLP Layer:** Advanced text processing using **Stemming**, **Lemmatization**, and domain-specific stopword removal.
- **Intelligence:** A unified Discovery Engine (`smart_profile_recommender_v2.py`) that combines Information Retrieval with User Profiling.
- **Analytics:** Comprehensive statistical profiling of the repository ecosystem.

---

## 📂 Project Structure

```bash
ir-project/
├── scraper.py          # Data Collection: Ethical crawler (respects robots.txt)
├── data.json           # Raw Storage: 200+ raw repository records
├── process.py          # NLP Layer: Advanced cleaning & weighted tokenization
├── processed.json      # IR Storage: Search-optimized document representation
├── smart_profile_recommender_v2.py # Product Layer: Personalized Discovery & Search
├── analysis.py         # Analytics: Dataset statistics & trends
├── Pipeline.md         # Technical Specification: Algorithmic deep-dive
└── EXCUTION.md         # Operational Guide: Step-by-step execution flow
```

---

## ⚙️ Execution Flow

1.  **Phase 1: Collection**
    ```bash
    python scraper.py
    ```
2.  **Phase 2: Processing**
    ```bash
    python process.py
    ```
3.  **Phase 4: Discovery & Search**
    ```bash
    python smart_profile_recommender_v2.py
    ```
    *Build your profile and start discovering repositories tailored to your needs.*

---

## 🎯 Academic Requirements Alignment

- [x] **Web Data Collection:** Multi-page scraping (200 records) + `robots.txt` compliance.
- [x] **Data Storage:** Structured JSON with consistent schema.
- [x] **Data Processing:** Tokenization, Stemming, Lemmatization, and Noise Removal.
- [x] **Data Understanding:** Statistical analysis and keyword frequency.
- [x] **Product Interface:** Interactive Personalized Search & Recommendation System.
- [x] **AI Integration:** Personalized ranking logic with explainable reasoning.

---

*Developed for the Web Intelligence & Information Retrieval Course.*
