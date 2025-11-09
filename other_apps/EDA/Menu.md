# Language Learning Apps – EDA Pipeline

A concise, modular **Exploratory Data Analysis (EDA)** pipeline for analyzing language learning apps from a CSV dataset.  
Runs 10 sequential Python scripts to **clean, summarize, visualize, and report** key insights.

---

## Overview

| Step | Script | Purpose |
|------|--------|--------|
| 1 | `01_load_clean.py` | Load & clean raw CSV |
| 2 | `02_summary_stats.py` | Basic stats + distributions |
| 3 | `03_rating_analysis.py` | Rating distribution & stats |
| 4 | `04_installs_vs_rating.py` | Installs vs rating scatter |
| 5 | `05_top_apps.py` | Top apps by installs & rating |
| 6 | `06_language_detection.py` | Detect target language from name |
| 7 | `07_reviews_analysis.py` | Reviews vs average rating |
| 8 | `08_genre_platform.py` | Genre breakdown & ratings |
| 9 | `09_correlation_heatmap.py` | Correlation matrix |
| 10 | `10_full_eda_dashboard.py` | All-in-one dashboard |

---

## 1. Data Loading & Cleaning  
**`01_load_clean.py`**

- Robust CSV loading with **encoding fallbacks** (`utf-8`, `cp1252`, etc.)
- Handles `N/A`, commas, `+` in install counts
- Converts columns to proper types (`int`, `float`)
- **Output**: `cleaned_language_apps.csv`

---

## 2. Summary Statistics  
**`02_summary_stats.py`**

- Numerical summary (`describe()`)
- Genre & Platform counts
- Saves:
  - `summary_numeric.csv`
  - `genre_distribution.csv`
  - `platform_distribution.csv`
  - `summary.md` (Markdown report)

---

## 3. Rating Analysis  
**`03_rating_analysis.py`**

- Histogram + KDE of **Google Ratings**
- Boxplot for outliers
- Prints mean, median, top 5 apps
- **Output**: `rating_distribution.png`

---

## 4. Installs vs Rating  
**`04_installs_vs_rating.py`**

- Scatter plot: **Installs (log scale)** vs **Rating**
- Color-coded by **Genre**
- Computes **Pearson correlation**
- **Outputs**:
  - `installs_vs_rating.png`
  - `installs_rating_correlation.txt`

---

## 5. Top Apps  
**`05_top_apps.py`**

Two leaderboards:

1. **Top 10 by Installs**
2. **Top 10 by Rating** (with ≥100K installs)

- **Outputs**:
  - `top_10_by_installs.csv`
  - `top_10_high_rated_100k_installs.csv`

---

## 6. Language Detection  
**`06_language_detection.py`**

- Rule-based detection from **app name**  
  (e.g., "Spanish", "Deutsch", "TOEFL" → English)
- Pie chart of detected languages
- **Output**: `language_pie.png`

---

## 7. Reviews Analysis  
**`07_reviews_analysis.py`**

- Scatter: **Review Count (log)** vs **Avg Review Rating**
- Hue: Google Rating
- Correlation coefficient
- **Outputs**:
  - `reviews_vs_rating.png`
  - `reviews_avg_rating_correlation.txt`

---

## 8. Genre & Platform  
**`08_genre_platform.py`**

- Bar chart: Apps per **Genre**
- Boxplot: **Rating by Genre**
- Average rating per genre
- **Outputs**:
  - `genre_analysis.png`
  - `average_rating_by_genre.csv`

---

## 9. Correlation Heatmap  
**`09_correlation_heatmap.py`**

- Heatmap of numeric features:
  - Rating, Installs, Reviews, etc.
- Annotated with correlation values
- **Output**: `correlation_heatmap.png`

---

## 10. Full EDA Dashboard  
**`10_full_eda_dashboard.py`**

**6-panel figure** combining key visuals:

1. Rating Distribution  
2. Installs vs Rating  
3. Language Pie Chart  
4. Rating by Genre (Boxplot)  
5. Reviews vs Avg Rating  
6. Top 10 Apps by Installs (Bar)

- **Output**: `full_eda_dashboard.png` (150 DPI)

---

## How to Run

```bash
python 01_load_clean.py
python 02_summary_stats.py
# ... run all in order
python 10_full_eda_dashboard.py