# 📦 Project Architecture (Data Pipeline & Personalized Discovery)

## 🧠 Overview

This project implements a **web intelligence data pipeline** that collects, processes, and analyzes textual data, culminating in a **Personalized Discovery & Search Engine**.

Pipeline:
Scraping → Storage → Processing → Analysis → Personalization & Search

---

## ⚠️ Design Philosophy (Important)

This implementation is intentionally **minimal** yet **intelligent**:

- Built to satisfy course requirements 1-6.
- Focus on the integration of Information Retrieval (BM25) with a Personalization Layer.
- Clean, functional code with "Explainability" (Reasoning for recommendations).

---

# 🗂️ Folder Structure

project/
│
├── scraper.py          # Data Collection
├── process.py          # Data Processing (NLP)
├── analysis.py         # Data Understanding (Stats)
├── smart_profile_recommender_v2.py # Product Layer (Personalized Search)
├── data.json           # Raw Dataset
└── processed.json      # IR-ready Dataset

---

# ⚙️ File Responsibilities

## 1. scraper.py (Web Data Collection Layer)
- Performs multi-page scraping of GitHub repositories.
- Extracts Title, Description, README, and Metadata.
- Respects `robots.txt` and implements rate-limiting.

## 2. process.py (Data Processing Layer)
- Cleans and normalizes text.
- Applies **Porter Stemming** and **WordNet Lemmatization**.
- Generates field-weighted tokens for search optimization.

## 3. analysis.py (Data Understanding Layer)
- Computes dataset statistics (vocabulary size, avg document length).
- Identifies top keywords and trends in the corpus.

## 4. smart_profile_recommender_v2.py (Product Layer)
- Implements **User Profiling** through interactive questions.
- Provides **Cold-Start Recommendations** based on profile similarity.
- Provides **Personalized Search** using query expansion and BM25 ranking.

---

# 📊 Data Flow

scraper.py
↓
data.json
↓
process.py
↓
processed.json
↓
analysis.py
↓
smart_profile_recommender_v2.py

---

# ✅ Mapping to Course Requirements

### 1. Web Data Collection
- Multi-page scraping implemented; dataset size: 200 records; robots.txt respected.

### 2. Data Storage Layer
- JSON format with consistent schema.

### 3. Data Processing Layer
- Tokenization, normalization, stemming, lemmatization, and stopword removal.

### 4. Data Understanding Layer
- Keyword frequency and statistical analysis.

### 5. Product Layer (Search System)
- Functional personalized search engine.

### 6. AI Integration
- Personalized recommendation logic and reasoning engine.

---

# 🚀 How to Run (Full Flow)

1. Run scraper: `python scraper.py`
2. Run processor: `python process.py`
3. Run analysis: `python analysis.py`
4. Run discovery engine: `python smart_profile_recommender_v2.py`

---

# 🎯 Final Note

This project transforms raw web content into a meaningful, AI-enhanced discovery experience, meeting all course requirements through a streamlined and effective data pipeline.
