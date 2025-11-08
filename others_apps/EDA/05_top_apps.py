# 05_top_apps.py
import os
import pandas as pd

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(SCRIPT_DIR, 'cleaned_language_apps.csv')

if not os.path.exists(csv_path):
    raise FileNotFoundError(
        f"Could not find cleaned CSV at {csv_path}. Run 01_load_clean.py first.")

df = pd.read_csv(csv_path)

# Top 10 by installs
top_installs = df.sort_values('Google Installs', ascending=False).head(10)
print("Top 10 Apps by Installs:")
print(top_installs[['App Name', 'Google Installs',
      'Rating (Google)']].to_string(index=False))

# Save top installs to CSV
top_installs_path = os.path.join(SCRIPT_DIR, 'top_10_by_installs.csv')
top_installs.to_csv(top_installs_path, index=False)
print(f"Saved top installs to: {top_installs_path}")

# Top 10 by rating (min 100k installs)
high_rated = df[df['Google Installs'] >= 100000].sort_values(
    'Rating (Google)', ascending=False).head(10)
print("\nTop 10 High-Rated Apps (100K+ Installs):")
print(high_rated[['App Name', 'Rating (Google)',
      'Google Installs']].to_string(index=False))

# Save high-rated to CSV
high_rated_path = os.path.join(
    SCRIPT_DIR, 'top_10_high_rated_100k_installs.csv')
high_rated.to_csv(high_rated_path, index=False)
print(f"Saved high-rated list to: {high_rated_path}")
