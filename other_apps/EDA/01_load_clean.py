# 01_load_clean.py
import os
import io
import pandas as pd
import numpy as np

# Load data (use path relative to this script so it works from any CWD)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(SCRIPT_DIR, 'language_learning_apps.csv')


def read_csv_with_fallback(path, encodings=None):
    """Try reading CSV with multiple encodings and fall back to replacement decoding."""
    if encodings is None:
        encodings = ['utf-8', 'utf-8-sig', 'cp1252', 'latin-1']

    for enc in encodings:
        try:
            print(f"Trying to read CSV with encoding: {enc}")
            return pd.read_csv(path, encoding=enc), enc
        except UnicodeDecodeError:
            print(f"  failed with encoding: {enc}")
        except Exception as e:
            # Other parsing errors - re-raise
            raise

    # Last resort: read as bytes and decode with 'utf-8' replacing invalid bytes
    print("Falling back to 'utf-8' with replacement for invalid bytes")
    with open(path, 'rb') as f:
        raw = f.read()
    text = raw.decode('utf-8', errors='replace')
    return pd.read_csv(io.StringIO(text)), 'utf-8-replace'


df, used_encoding = read_csv_with_fallback(csv_path)
print(f"Loaded CSV using encoding: {used_encoding}")

print("Original Shape:", df.shape)
print("\nFirst 5 rows:")
print(df.head())

# Replace N/A strings
df.replace('N/A', np.nan, inplace=True)

# Convert numeric columns
numeric_cols = ['Rating (Google)', 'Combined Rating', 'Total Ratings (Google)',
                'Total Ratings (All)', 'Review Count (Dataset)', 'Average Review Rating']
for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors='coerce')

# Clean Google Installs robustly (handle numeric and string values)
print("\nGoogle Installs - sample types and values:")
print(df['Google Installs'].head(8))

# Convert installs to string, remove commas, plus signs, and any non-digit characters,
# then coerce to numeric and fill NaN with 0
df['Google Installs'] = (
    df['Google Installs']
    .astype(str)
    .str.replace(',', '', regex=False)
    .str.replace('+', '', regex=False)
    .str.replace(r"[^0-9]", '', regex=True)
)
df['Google Installs'] = pd.to_numeric(
    df['Google Installs'], errors='coerce').fillna(0).astype(int)

print("\nCleaned Data Info:")
print(df.info())
print("\nMissing Values:")
print(df.isnull().sum())

out_path = os.path.join(SCRIPT_DIR, 'cleaned_language_apps.csv')
df.to_csv(out_path, index=False)
print(f"\nCleaned data saved to '{out_path}'")
