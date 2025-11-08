# 04_installs_vs_rating.py
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

plt.figure(figsize=(10, 6))
sns.scatterplot(data=df, x='Google Installs', y='Rating (Google)',
                hue='Genre', alpha=0.7, palette='deep')

plt.xscale('log')
plt.xlabel('Google Installs (Log Scale)')
plt.title('Installs vs Rating by Genre')
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')

plt.tight_layout()
out_fig = os.path.join(SCRIPT_DIR, 'installs_vs_rating.png')
plt.savefig(out_fig)
print(f"Saved installs vs rating figure to: {out_fig}")
plt.show()

# Correlation
corr = df['Google Installs'].corr(df['Rating (Google)'])
print(f"Correlation between Installs and Rating: {corr:.3f}")

# Save correlation result
corr_path = os.path.join(SCRIPT_DIR, 'installs_rating_correlation.txt')
with open(corr_path, 'w', encoding='utf-8') as fh:
    fh.write(
        f"Correlation between Google Installs and Google Rating: {corr:.3f}\n")
print(f"Saved correlation to: {corr_path}")
