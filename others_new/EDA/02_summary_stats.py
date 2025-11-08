# 02_summary_stats.py
import os
import pandas as pd

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(SCRIPT_DIR, 'cleaned_language_apps.csv')

if not os.path.exists(csv_path):
    raise FileNotFoundError(
        f"Could not find cleaned CSV at {csv_path}. Run 01_load_clean.py first.")

df = pd.read_csv(csv_path)

print("=== Numerical Summary ===")
numeric_summary = df.describe()
print(numeric_summary)

# Save numeric summary to CSV
numeric_csv_path = os.path.join(SCRIPT_DIR, 'summary_numeric.csv')
numeric_summary.to_csv(numeric_csv_path)
print(f"Saved numeric summary to: {numeric_csv_path}")

print("\n=== Categorical Summary ===")
print("Genre Distribution:")
genre_counts = df['Genre'].value_counts()
print(genre_counts)

# Save genre distribution
genre_csv_path = os.path.join(SCRIPT_DIR, 'genre_distribution.csv')
genre_counts.reset_index().rename(
    columns={'index': 'Genre', 'Genre': 'Count'}).to_csv(genre_csv_path, index=False)
print(f"Saved genre distribution to: {genre_csv_path}")
print("\nPlatform Distribution:")
platform_counts = df['Platform'].value_counts()
print(platform_counts)

# Save platform distribution
platform_csv_path = os.path.join(SCRIPT_DIR, 'platform_distribution.csv')
platform_counts.reset_index().rename(columns={
    'index': 'Platform', 'Platform': 'Count'}).to_csv(platform_csv_path, index=False)
print(f"Saved platform distribution to: {platform_csv_path}")

# Also create a short markdown report. Use to_markdown when available, otherwise fall back to plain text.
md_path = os.path.join(SCRIPT_DIR, 'summary.md')
with open(md_path, 'w', encoding='utf-8') as md:
    md.write('# Summary Statistics\n\n')
    md.write('## Numerical Summary\n\n')
    try:
        md.write(numeric_summary.to_markdown())
    except Exception:
        # pandas raises ImportError when tabulate is missing; fallback to plain text
        md.write(numeric_summary.to_string())
    md.write('\n\n')
    md.write('## Genre Distribution\n\n')
    try:
        md.write(genre_counts.to_frame('Count').to_markdown())
    except Exception:
        md.write(genre_counts.to_frame('Count').to_string())
    md.write('\n\n')
    md.write('## Platform Distribution\n\n')
    try:
        md.write(platform_counts.to_frame('Count').to_markdown())
    except Exception:
        md.write(platform_counts.to_frame('Count').to_string())

print(f"Saved markdown summary to: {md_path}")
