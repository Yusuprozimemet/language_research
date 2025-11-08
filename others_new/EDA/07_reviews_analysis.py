# 07_reviews_analysis.py
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

# Filter apps with reviews
reviewed = df[df['Review Count (Dataset)'] > 0].copy()

plt.figure(figsize=(10, 6))
sns.scatterplot(data=reviewed, x='Review Count (Dataset)', y='Average Review Rating',
                hue='Rating (Google)', palette='viridis', alpha=0.8)
plt.xscale('log')
plt.title('Review Count vs Average Review Rating')
plt.xlabel('Review Count (Dataset) - Log Scale')
plt.legend(title='Google Rating', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
out_fig = os.path.join(SCRIPT_DIR, 'reviews_vs_rating.png')
plt.savefig(out_fig)
print(f"Saved reviews vs rating figure to: {out_fig}")
plt.show()

corr_val = reviewed['Review Count (Dataset)'].corr(
    reviewed['Average Review Rating'])
print(f"Correlation (Review Count vs Avg Review Rating): {corr_val:.3f}")

# Save correlation
corr_path = os.path.join(SCRIPT_DIR, 'reviews_avg_rating_correlation.txt')
with open(corr_path, 'w', encoding='utf-8') as fh:
    fh.write(
        f"Correlation (Review Count vs Avg Review Rating): {corr_val:.3f}\n")
print(f"Saved correlation to: {corr_path}")
