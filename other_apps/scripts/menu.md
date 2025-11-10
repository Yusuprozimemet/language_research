# Language Learning Apps Analysis Suite  
**Menu & Usage Guide** (`menu.md`)

---

## Overview
This suite of **8 Python scripts** analyzes **146 language learning apps** using real Google Play & App Store data. It:

- Collects reviews  
- Splits data  
- Generates reports  
- Ranks apps scientifically  
- Creates visualizations & insights

All scripts are **modular**, **interoperable**, and **designed for automation**.

---

## Scripts & Purpose

| Script | Purpose | Input | Output |
|-------|--------|-------|--------|
| `collect_reviews_for_apps.py` | **Scrape** up to 300 reviews per app (Google + Apple fallback) | Hardcoded app list | `output/reviews_<app>.jsonl`, `reviews_combined.jsonl` |
| `seperate.py` | **Split** combined JSONL into individual app files | `data/apps_combined.jsonl` | `individual/*.jsonl` |
| `categorize.py` | **Categorize** apps: Excellent, Good, Poor, Niche, etc. | `individual/*.jsonl` | `output/categories.md` (full report) |
| `generate_csv.py` | **Export** all app metrics to CSV | `individual/*.jsonl` | `output/apps.csv` |
| `generate_md.py` | **Per-app deep dive**: analytics, word clouds, sentiment, charts | `individual/*.jsonl` | `individual_md/*.md` + `charts/` |
| `evaluation.py` | **Rank all 146 apps** using composite score (Rating 40%, Popularity 30%, Reviews 20%, Genre 10%) | Hardcoded app list (from reports) | `146_apps_ranked.png`, `.csv` |
| `extract_excellent_apps.py` | **Extract top N excellent apps** with descriptions | `evaluation.py` + `apps_combined.jsonl` | `output/excellent_apps.csv`, `.jsonl` |
| `list_excellent_names.py` | **List only names** of top N excellent apps | Uses `evaluation.py` logic | `output/excellent_names.txt`, `.json` |

---

## Workflow Pipeline (ASCII)

```text
MAIN PIPELINE (146 APPS ANALYSIS)
═════════════════════════════════════════════════════════════════════

┌─────────────────────────────────────┐
│ 1. collect_reviews_for_apps.py      │
│    → Scrape 300 reviews/app         │
└───────────────┬─────────────────────┘
                │
                ▼
┌─────────────────────────────────────┐
│ reviews_combined.jsonl              │
└───────────────┬─────────────────────┘
                │
                ▼
┌─────────────────────────────────────┐
│ 2. seperate.py                      │
│    → Split into individual files    │
└───────────────┬─────────────────────┘
                │
                ▼
┌─────────────────────────────────────┐
│ individual/*.jsonl (146 apps)       │
└───────┬───────────────────────┬─────┘
        │                       │
        ▼                       ▼
   ┌───────────────────┐   ┌────────────────────┐
   │ 3. categorize.py  │   │ 4. generate_csv.py │
   │ → categories.md   │   │ → apps.csv         │
   └───────┬───────────┘   └─────────┬──────────┘
           │                     │
           ▼                     ▼
   ┌───────────────────┐   ┌────────────────────┐
   │ 5. generate_md.py │   │ (Optional export)  │
   │                   │   │                    │
   │ → per-app MD +    │   └────────────────────┘
   │   charts          │
   └───────┬───────────┘
           │
           ▼
   ┌─────────────────────────────────────┐
   │ 6. evaluation.py                    │
   │ → 146_apps_ranked.png + .csv        │
   └───────────────┬─────────────────────┘
                   │
                   ▼
   ┌─────────────────────────────────────┐
   │ 7. extract_excellent_apps.py        │
   │ → excellent_apps.csv + .jsonl       │
   │   excellent_apps_description.md     │
   └───────────────┬─────────────────────┘
                   │
                   ▼
   ┌─────────────────────────────────────┐
   │ 8. list_excellent_names.py          │
   │ → excellent_names.txt + .json       │
   └───────────────┬─────────────────────┘


FOCUSED DEEP-DIVE (7 SELECTED APPS)
═════════════════════════════════════════════════════════════════════

                   │
                   ▼
   ┌─────────────────────────────────────┐
   │ Manual Testing & Selection          │
   │ → Select 7 best apps from 35        │
   │    excellent candidates             │
   └───────────────┬─────────────────────┘
                   │
                   ▼
   ┌─────────────────────────────────────┐
   │ 9. collect_reviews_for_apps.py      │
   │    (targeted for 7 apps)            │
   │ → Scrape ~200-300 reviews/app       │
   └───────────────┬─────────────────────┘
                   │
                   ▼
   ┌─────────────────────────────────────┐
   │ output/reviews_<app>.jsonl (7 files)│
   │                                     │
   └───────────────┬─────────────────────┘
                   │
                   ▼
   
```

### Execution Order
1. **Start** → `collect_reviews_for_apps.py`  
2. **Then** → `seperate.py`  
3. **Then** → Run **3, 4, 5** in **any order**  
4. **Then** → `evaluation.py`  
5. **Finally** → `extract_excellent_apps.py` → `list_excellent_names.py`

---

## How to Use (Step-by-Step)

### 1. **Collect Reviews**
```bash
python collect_reviews_for_apps.py --per-app 300
```
> Gets ~300 reviews per app. Outputs in `output/`

---

### 2. **Split Data**
```bash
python seperate.py
```
> Splits `apps_combined.jsonl` → `individual/*.jsonl`

---

### 3. **Generate Full Category Report**
```bash
python categorize.py
```
> Creates `output/categories.md` — **main analysis report**

---

### 4. **Export to CSV**
```bash
python generate_csv.py
```
> `output/apps.csv` — ready for Excel/Google Sheets

---

### 5. **Deep Per-App Analytics**
```bash
python generate_md.py
```
> Creates:
> - `individual_md/*.md` (sentiment, word clouds, charts)
> - `individual_md/charts/*.png`

---

### 6. **Rank All 146 Apps**
```bash
python evaluation.py
```
> Outputs:
> - `146_apps_ranked.png` (beautiful bar chart)
> - `146_apps_ranked_full.csv`

---

### 7. **Extract Top 35 Excellent Apps**
```bash
python extract_excellent_apps.py --top 35
```
> `output/excellent_apps.csv` + `.jsonl` with **descriptions**

---

### 8. **Get Just the Names**
```bash
python list_excellent_names.py --top 35
```
> `excellent_names.txt` — one name per line

---

## Key Outputs to Use

| File | Use Case |
|------|---------|
| `output/categories.md` | **Main report** – share with team, investors |
| `output/apps.csv` | **Data analysis** in Excel, BI tools |
| `individual_md/*.md` | **Blog posts**, **investor deck**, **product deep dives** |
| `146_apps_ranked.png` | **Visual summary** for presentations |
| `excellent_apps.csv` | **Top picks list** for users, marketing |
| `excellent_names.txt` | **Quick reference**, import into tools |

---

## Requirements
Install dependencies:
```bash
pip install pandas matplotlib seaborn wordcloud textblob nltk langdetect scikit-learn google-play-scraper itunespy
```

Run once (NLTK):
```python
import nltk
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('vader_lexicon')
```

---

## Tips
- Run `collect_reviews_for_apps.py` **first**
- All other scripts use `individual/*.jsonl`
- Update `evaluation.py` list if you add new apps
- Use `output/categories.md` as your **master report**
- `generate_md.py` is **optional but powerful** for per-app insights

---

## New Workflow: 7 Selected Apps Analysis

After initial analysis of 146 apps, a focused deep-dive was conducted on **7 selected apps** using the following workflow:

### Workflow Summary

1. **Collected excellent_names.txt** — List of top apps extracted from evaluation rankings
2. **Used Grok AI** → Generated `output/Excellent_apps_description.md` (AI-curated descriptions of top apps)
3. **Manual Testing** — Downloaded and tested each of the 35 excellent apps to validate quality
4. **Selected 7 Best Apps** — Chose the 7 most promising apps based on manual evaluation
5. **Collected Reviews** → Ran `collect_reviews_for_apps.py` to gather ~200–300 reviews per app


### The 7 Selected Apps

| App Name | Package ID | Output Files | Link |
|----------|-----------|-------------|------|
| **Duolingo** | `com.duolingo` | `com.duolingo.md`, charts | `individual_md/com.duolingo.md` |
| **Quizlet** | `com.quizlet.quizletandroid` | `com.quizlet.quizletandroid.md`, charts | `individual_md/com.quizlet.quizletandroid.md` |
| **Busuu** | `com.busuu.android.enc` | `com.busuu.android.enc.md`, charts | `individual_md/com.busuu.android.enc.md` |
| **Falou** | `com.moymer.falou` | `com.moymer.falou.md`, charts | `individual_md/com.moymer.falou.md` |
| **Babbel** | `com.babbel.mobile.android.en` | `com.babbel.mobile.android.en.md`, charts | `individual_md/com.babbel.mobile.android.en.md` |
| **Memrise** | `com.memrise.android.memrisecompanion` | `com.memrise.android.memrisecompanion.md`, charts | `individual_md/com.memrise.android.memrisecompanion.md` |
| **Rosetta Stone** | `air.com.rosettastone.mobile.CoursePlayer` | `air.com.rosettastone.mobile.CoursePlayer.md`, charts | `individual_md/air.com.rosettastone.mobile.CoursePlayer.md` |


**Done!** You now have:
- A full scientific analysis of 146 language apps (master reports in `output/categories.md`)
- Deep analytics on 7 hand-selected apps (individual reports + charts in `individual_md/`)
- Rigorous thematic analysis for customer research (summaries in `output/reviews_*.md`)

*Generated: November 09, 2025*  
*Updated: November 10, 2025 — Added 7-app deep-dive workflow documentation*