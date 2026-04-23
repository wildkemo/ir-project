# 📦 Project Architecture (Minimal Version – Aligned with Course Requirements)

## 🧠 Overview

This project implements a **complete web intelligence pipeline** that collects, processes, analyzes, and retrieves textual data, while integrating a simple AI feature.

Pipeline:
Scraping → Storage → Processing → Analysis → Search → AI → Interface

---

## ⚠️ Design Philosophy (Important)

This implementation is intentionally **minimal**:

- Built only to satisfy course requirements
- No over-engineering or complex frameworks
- No unnecessary abstractions or boilerplate
- Focus on correctness and completeness, not scale

---

# 🗂️ Folder Structure

project/
│
├── scraper.py
├── process.py
├── analysis.py
├── search.py
├── sentiment.py
├── cli.py
├── data.json
├── processed.json

---

# ⚙️ File Responsibilities

## 1. scraper.py (Web Data Collection Layer)

### 🎯 Purpose

Collect real-world textual data from the web.

### 🔧 What it does

- Performs multi-page scraping
- Extracts structured fields (e.g., title, content)
- Ensures consistent schema for all records
- Produces at least 50–200 records
- Respects robots.txt rules

### ▶️ Execution

Run first to generate dataset.

---

## 2. process.py (Data Processing Layer)

### 🎯 Purpose

Clean and preprocess textual data.

### 🔧 What it does

- Loads raw data
- Applies:
  - Tokenization
  - Normalization (lowercasing)
  - Stopword removal

- Handles missing or noisy data
- Outputs cleaned dataset

### ▶️ Execution

Run after scraping.

---

## 3. analysis.py (Data Understanding Layer)

### 🎯 Purpose

Perform basic dataset analysis.

### 🔧 What it does

- Computes keyword frequency
- Generates simple statistics (e.g., word counts)
- Provides basic dataset exploration

### ▶️ Execution

Can be run independently or integrated into CLI.

---

## 4. search.py (Information Retrieval Layer)

### 🎯 Purpose

Provide IR-style search functionality.

### 🔧 What it does

- Loads processed data
- Implements keyword-based retrieval
- Returns relevant documents based on query

### ▶️ Execution

Used by the interface.

---

## 5. sentiment.py (AI Integration Layer)

### 🎯 Purpose

Provide AI-powered feature.

### 🔧 What it does

- Performs sentiment analysis on text
- Classifies content as positive, negative, or neutral

### ▶️ Execution

Used during result display.

---

## 6. cli.py (Product Layer / Interface)

### 🎯 Purpose

Provide a functional user interface.

### 🔧 What it does

- Accepts user queries
- Displays search results
- Shows sentiment for each result
- Optionally displays basic analysis results

### ▶️ Execution

Main entry point for the user.

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
search.py + sentiment.py
↓
cli.py

---

# ✅ Mapping to Course Requirements

### 1. Web Data Collection

- Multi-page scraping implemented
- Dataset size: 50–200 records
- robots.txt respected

### 2. Data Storage Layer

- JSON format used
- Consistent schema across all records

### 3. Data Processing Layer

- Tokenization, normalization, stopword removal
- Handles noisy data

### 4. Data Understanding Layer

- Keyword frequency analysis
- Basic statistics

### 5. Product Layer

- CLI-based search system (IR-style retrieval)

### 6. AI Integration Layer

- Sentiment analysis feature

---

# 🚀 How to Run (Full Flow)

1. Run scraper to collect data
2. Run processor to clean data
3. (Optional) Run analysis for insights
4. Run CLI to search and view results

---

# 🎯 Final Note

This project satisfies all required layers:

- Data collection
- Storage
- Processing
- Analysis
- Information retrieval
- AI integration
- Functional product interface

All implemented with the **simplest possible design** to meet course expectations without unnecessary complexity.
