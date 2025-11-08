# 08_genre_platform.py
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

plt.figure(figsize=(12, 5))

plt.subplot(1, 2, 1)
df['Genre'].value_counts().plot(kind='bar', color='teal')
plt.title('Apps by Genre')
plt.xticks(rotation=45)

plt.subplot(1, 2, 2)
sns.boxplot(data=df, x='Genre', y='Rating (Google)')
plt.title('Rating by Genre')
plt.xticks(rotation=45)

plt.tight_layout()
out_fig = os.path.join(SCRIPT_DIR, 'genre_analysis.png')
plt.savefig(out_fig)
print(f"Saved genre analysis figure to: {out_fig}")
plt.show()

print("Average Rating by Genre:")
avg_by_genre = df.groupby(
    'Genre')['Rating (Google)'].mean().sort_values(ascending=False)
print(avg_by_genre)

# Save average rating by genre to CSV
avg_genre_path = os.path.join(SCRIPT_DIR, 'average_rating_by_genre.csv')
avg_by_genre.reset_index().rename(
    columns={'Rating (Google)': 'Average Rating'}).to_csv(avg_genre_path, index=False)
print(f"Saved average rating by genre to: {avg_genre_path}")
