# 03_rating_analysis.py
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(SCRIPT_DIR, 'cleaned_language_apps.csv')

if not os.path.exists(csv_path):
    raise FileNotFoundError(
        f"Could not find cleaned CSV at {csv_path}. Run 01_load_clean.py first.")

df = pd.read_csv(csv_path)
sns.set_style("whitegrid")

plt.figure(figsize=(12, 5))

plt.subplot(1, 2, 1)
sns.histplot(df['Rating (Google)'].dropna(),
             bins=20, kde=True, color='skyblue')
plt.title('Distribution of Google Ratings')
plt.xlabel('Rating (Google)')

plt.subplot(1, 2, 2)
sns.boxplot(y=df['Rating (Google)'], color='lightcoral')
plt.title('Boxplot of Google Ratings')

plt.tight_layout()
out_fig = os.path.join(SCRIPT_DIR, 'rating_distribution.png')
plt.savefig(out_fig)
print(f"Saved rating distribution figure to: {out_fig}")
plt.show()

print(f"Mean Rating: {df['Rating (Google)'].mean():.3f}")
print(f"Median Rating: {df['Rating (Google)'].median():.3f}")
print(f"Top 5 Highest Rated Apps:")
print(df[['App Name', 'Rating (Google)']].sort_values(
    'Rating (Google)', ascending=False).head())
