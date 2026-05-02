# 📦 Project Architecture (Data Pipeline – Aligned with Course Requirements 1-4)

## 🧠 Overview

This project implements a **web intelligence data pipeline** that collects, processes, and analyzes textual data.

Pipeline:
Scraping → Storage → Processing → Analysis

---

## ⚠️ Design Philosophy (Important)

This implementation is intentionally **minimal**:

- Built only to satisfy course requirements 1-4
- No over-engineering or complex frameworks
- No unnecessary abstractions or boilerplate
- Focus on correctness and completeness of the data pipeline

---

# 🗂️ Folder Structure

project/
│
├── scraper.py
├── process.py
├── analysis.py
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

Run after processing to gain insights into the dataset.

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

---

# 🚀 How to Run (Full Flow)

1. Run scraper to collect data: `python scraper.py`
2. Run processor to clean data: `python process.py`
3. Run analysis for insights: `python analysis.py`

---

# 🎯 Final Note

This project satisfies all required layers for the data pipeline:

- Data collection
- Storage
- Processing
- Analysis

All implemented with the **simplest possible design** to meet course expectations for requirements 1-4.
