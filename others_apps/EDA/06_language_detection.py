# 06_language_detection.py
import os
import matplotlib.pyplot as plt
import pandas as pd
import re

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(SCRIPT_DIR, 'cleaned_language_apps.csv')

if not os.path.exists(csv_path):
    raise FileNotFoundError(
        f"Could not find cleaned CSV at {csv_path}. Run 01_load_clean.py first.")

df = pd.read_csv(csv_path)

# Common language keywords
lang_keywords = {
    'English': ['english', 'grammar', 'vocabulary', 'toefl', 'ielts'],
    'Spanish': ['spanish', 'español'],
    'German': ['german', 'deutsch'],
    'French': ['french', 'français', 'frantastique'],
    'Dutch': ['dutch', 'nederlands'],
    'Korean': ['korean'],
    'Other': []
}


def detect_language(app_name):
    name = app_name.lower()
    for lang, keywords in lang_keywords.items():
        if any(k in name for k in keywords):
            return lang
    return 'Other'


df['Detected Language'] = df['App Name'].apply(detect_language)

print("Detected Language Distribution:")
print(df['Detected Language'].value_counts())

# Plot
df['Detected Language'].value_counts().plot(
    kind='pie', autopct='%1.1f%%', figsize=(8, 8))
plt.title('Apps by Target Language')
plt.ylabel('')
out_fig = os.path.join(SCRIPT_DIR, 'language_pie.png')
plt.savefig(out_fig)
print(f"Saved language pie chart to: {out_fig}")
plt.show()
