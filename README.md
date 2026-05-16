# 🧠 AI Fact-Checking System for Data Visualizations

A computer vision + AI-powered system that detects misleading charts in news articles and assigns an **Integrity Score** based on visual structure, statistical cues, and semantic classification.

---

## 🚀 Live Demo
https://your-streamlit-app-link-here

---

## 📌 Problem Statement
News articles often use manipulated charts (truncated axes, cherry-picked timelines, misleading scaling). Manual detection is slow and unreliable.

This project automates detection using AI.

---

## ⚙️ Features

- 🔍 Web scraping of news articles
- 📊 Automatic chart extraction from images
- 🧠 AI-based chart classification (CLIP model)
- 🧾 OCR-based text density detection (Tesseract)
- 📉 OpenCV structural analysis
- ⚖️ Integrity scoring system (0–100)
- 📄 Auto-generated PDF report
- 🎨 Interactive Streamlit dashboard

---

## 🏗️ System Architecture

Article URL  
→ Scraper (BeautifulSoup)  
→ Image Extractor  
→ AI Filter Layer (CLIP + OCR + CV)  
→ Chart Analyzer (OpenCV heuristic model)  
→ Integrity Scoring Engine  
→ Streamlit Dashboard  
→ PDF Report Generator  

---

## 🧠 AI Techniques Used

- CLIP Vision-Language Model (image classification)
- Tesseract OCR (text detection in images)
- OpenCV (edge detection + structure analysis)

---

## 📊 Output Example

- Chart Type Detection
- Misleading Indicators
- Integrity Score (0–100)
- Visual Report per chart

---

## 🧰 Tech Stack

Python, Streamlit, OpenCV, PyTorch, Transformers, Tesseract OCR, Plotly, BeautifulSoup

---

## 📦 How to Run Locally

```bash
git clone https://github.com/your-username/ai-fact-checking-system
cd ai-fact-checking-system
pip install -r requirements.txt
streamlit run app.py
