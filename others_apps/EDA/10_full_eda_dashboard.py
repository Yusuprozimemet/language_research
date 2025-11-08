# 10_full_eda_dashboard.py
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(SCRIPT_DIR, 'cleaned_language_apps.csv')

if not os.path.exists(csv_path):
    raise FileNotFoundError(
        f"Could not find cleaned CSV at {csv_path}. Run 01_load_clean.py first.")

df = pd.read_csv(csv_path)
df.replace('N/A', np.nan, inplace=True)
for col in ['Rating (Google)', 'Average Review Rating', 'Total Ratings (Google)', 'Review Count (Dataset)']:
    df[col] = pd.to_numeric(df[col], errors='coerce')

# Normalize Google Installs robustly
df['Google Installs'] = (
    df['Google Installs']
    .astype(str)
    .str.replace(',', '', regex=False)
    .str.replace('+', '', regex=False)
    .str.replace(r"[^0-9]", '', regex=True)
)
df['Google Installs'] = pd.to_numeric(
    df['Google Installs'], errors='coerce').fillna(0).astype(int)

# Language detection


def detect_lang(name):
    n = name.lower()
    if any(x in n for x in ['english', 'grammar', 'toefl', 'ielts']):
        return 'English'
    if any(x in n for x in ['spanish', 'español']):
        return 'Spanish'
    if any(x in n for x in ['german', 'deutsch']):
        return 'German'
    if any(x in n for x in ['french', 'français']):
        return 'French'
    if any(x in n for x in ['dutch', 'nederlands']):
        return 'Dutch'
    return 'Other'


df['Language'] = df['App Name'].apply(detect_lang)

# Dashboard
fig = plt.figure(figsize=(16, 12))

# 1. Rating Distribution
plt.subplot(2, 3, 1)
sns.histplot(df['Rating (Google)'].dropna(),
             bins=15, kde=True, color='skyblue')
plt.title('Rating Distribution')

# 2. Installs vs Rating
plt.subplot(2, 3, 2)
sns.scatterplot(data=df, x='Google Installs', y='Rating (Google)', alpha=0.6)
plt.xscale('log')
plt.title('Installs vs Rating')

# 3. Language Pie
plt.subplot(2, 3, 3)
df['Language'].value_counts().plot(kind='pie', autopct='%1.1f%%', ax=plt.gca())
plt.title('Target Language')
plt.ylabel('')

# 4. Genre Rating Boxplot
plt.subplot(2, 3, 4)
sns.boxplot(data=df, x='Genre', y='Rating (Google)')
plt.xticks(rotation=45)
plt.title('Rating by Genre')

# 5. Review Sentiment
plt.subplot(2, 3, 5)
reviewed = df[df['Review Count (Dataset)'] > 0]
sns.scatterplot(data=reviewed, x='Review Count (Dataset)',
                y='Average Review Rating', hue='Rating (Google)', palette='coolwarm')
plt.xscale('log')
plt.title('Review Count vs Avg Review Rating')

# 6. Top Apps Bar
plt.subplot(2, 3, 6)
top10 = df.nlargest(10, 'Google Installs')
sns.barplot(data=top10, y='App Name', x='Google Installs', palette='viridis')
plt.title('Top 10 by Installs')
plt.xlabel('Installs')

plt.tight_layout()
out_fig = os.path.join(SCRIPT_DIR, 'full_eda_dashboard.png')
plt.savefig(out_fig, dpi=150, bbox_inches='tight')
print(f"Full EDA Dashboard saved as '{out_fig}'")
plt.show()
