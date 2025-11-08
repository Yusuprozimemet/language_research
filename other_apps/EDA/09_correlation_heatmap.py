# 09_correlation_heatmap.py
import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(SCRIPT_DIR, 'cleaned_language_apps.csv')

if not os.path.exists(csv_path):
    raise FileNotFoundError(
        f"Could not find cleaned CSV at {csv_path}. Run 01_load_clean.py first.")

df = pd.read_csv(csv_path)

# Select numeric columns
num_cols = ['Rating (Google)', 'Total Ratings (Google)', 'Google Installs',
            'Review Count (Dataset)', 'Average Review Rating']
corr = df[num_cols].corr()

plt.figure(figsize=(8, 6))
sns.heatmap(corr, annot=True, cmap='coolwarm', center=0, square=True)
plt.title('Correlation Matrix of Numeric Features')
plt.tight_layout()
out_fig = os.path.join(SCRIPT_DIR, 'correlation_heatmap.png')
plt.savefig(out_fig)
print(f"Saved correlation heatmap to: {out_fig}")
plt.show()
