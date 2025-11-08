import numpy as np
from wordcloud import WordCloud
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import json
import os
import re
from collections import Counter
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Advanced analytics libraries

# NLP libraries
try:
    from textblob import TextBlob
    import nltk
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize
    from nltk.stem import WordNetLemmatizer
    # Download required NLTK data quietly
    try:
        nltk.data.find('tokenizers/punkt')
        nltk.data.find('corpora/stopwords')
        nltk.data.find('corpora/wordnet')
    except LookupError:
        print("Downloading NLTK data...")
        nltk.download('punkt', quiet=True)
        nltk.download('stopwords', quiet=True)
        nltk.download('wordnet', quiet=True)
        nltk.download('vader_lexicon', quiet=True)
    NLTK_AVAILABLE = True
except ImportError:
    print("NLTK/TextBlob not available - using basic text analysis")
    NLTK_AVAILABLE = False

try:
    from langdetect import detect, detect_langs
    LANGDETECT_AVAILABLE = True
except ImportError:
    print("langdetect not available - skipping language detection")
    LANGDETECT_AVAILABLE = False

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.cluster import KMeans
    SKLEARN_AVAILABLE = True
except ImportError:
    print("scikit-learn not available - skipping advanced clustering")
    SKLEARN_AVAILABLE = False

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
INPUT_DIR = os.path.join(PROJECT_DIR, "individual")
OUTPUT_DIR = os.path.join(PROJECT_DIR, "individual_md")
CHARTS_DIR = os.path.join(OUTPUT_DIR, "charts")

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(CHARTS_DIR, exist_ok=True)

# Configure matplotlib for better charts
plt.style.use('default')
sns.set_palette("husl")


def safe_filename(name):
    """Keep alphanum, '.', '_' and '-' ; replace others with '_'"""
    return re.sub(r"[^A-Za-z0-9. _-]", "_", name).strip().replace(' ', '_')


def detect_language(text):
    """Detect language of text"""
    if not LANGDETECT_AVAILABLE or not text or len(text.strip()) < 10:
        return "unknown"
    try:
        return detect(text)
    except:
        return "unknown"


def analyze_sentiment(text):
    """Analyze sentiment using TextBlob"""
    if not NLTK_AVAILABLE or not text:
        return 0.0, 0.0
    try:
        blob = TextBlob(text)
        return blob.sentiment.polarity, blob.sentiment.subjectivity
    except:
        return 0.0, 0.0


def extract_key_phrases(reviews_text, max_phrases=10):
    """Extract key phrases using TF-IDF"""
    if not SKLEARN_AVAILABLE or not reviews_text or len(reviews_text) < 3:
        return []

    try:
        vectorizer = TfidfVectorizer(
            max_features=100,
            ngram_range=(1, 3),
            stop_words='english',
            min_df=2
        )
        tfidf_matrix = vectorizer.fit_transform(reviews_text)
        feature_names = vectorizer.get_feature_names_out()

        # Get mean TF-IDF scores
        mean_scores = np.mean(tfidf_matrix.toarray(), axis=0)
        top_indices = np.argsort(mean_scores)[::-1][:max_phrases]

        return [(feature_names[i], mean_scores[i]) for i in top_indices]
    except:
        return []


def create_charts(app_name, reviews_df, charts_dir):
    """Create visualization charts for reviews"""
    charts_created = []

    if reviews_df.empty:
        return charts_created

    # Rating distribution chart
    try:
        plt.figure(figsize=(10, 6))
        rating_counts = reviews_df['rating'].value_counts().sort_index()

        plt.subplot(2, 2, 1)
        colors = ['#ff4444', '#ff8800', '#ffdd00', '#88dd00', '#44dd44']
        rating_counts.plot(kind='bar', color=colors[:len(rating_counts)])
        plt.title('Rating Distribution')
        plt.xlabel('Rating')
        plt.ylabel('Count')
        plt.xticks(rotation=0)

        # Sentiment over time (if dates available)
        if 'date' in reviews_df.columns and 'sentiment' in reviews_df.columns:
            plt.subplot(2, 2, 2)
            reviews_df_time = reviews_df.dropna(subset=['date', 'sentiment'])
            if not reviews_df_time.empty:
                reviews_df_time['date'] = pd.to_datetime(
                    reviews_df_time['date'], errors='coerce')
                reviews_df_time = reviews_df_time.dropna(subset=['date'])
                if not reviews_df_time.empty:
                    reviews_df_time.set_index(
                        'date')['sentiment'].resample('M').mean().plot()
                    plt.title('Sentiment Trend Over Time')
                    plt.ylabel('Sentiment Score')

        # Platform distribution
        if 'platform' in reviews_df.columns:
            plt.subplot(2, 2, 3)
            platform_counts = reviews_df['platform'].value_counts()
            plt.pie(platform_counts.values,
                    labels=platform_counts.index, autopct='%1.1f%%')
            plt.title('Reviews by Platform')

        # Language distribution
        if 'language' in reviews_df.columns:
            plt.subplot(2, 2, 4)
            lang_counts = reviews_df['language'].value_counts().head(10)
            lang_counts.plot(kind='bar')
            plt.title('Top Languages in Reviews')
            plt.xlabel('Language')
            plt.ylabel('Count')
            plt.xticks(rotation=45)

        plt.tight_layout()
        chart_path = os.path.join(
            charts_dir, f"{safe_filename(app_name)}_analytics.png")
        plt.savefig(chart_path, dpi=150, bbox_inches='tight')
        plt.close()
        charts_created.append(chart_path)
    except Exception as e:
        print(f"Error creating analytics chart: {e}")

    return charts_created


def create_wordcloud(text, app_name, charts_dir):
    """Create word cloud from review text"""
    if not text or len(text) < 50:
        return None

    try:
        # Create word cloud
        wordcloud = WordCloud(
            width=800,
            height=400,
            background_color='white',
            max_words=100,
            relative_scaling=0.5,
            colormap='viridis'
        ).generate(text)

        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.title(f'Word Cloud - {app_name}')

        chart_path = os.path.join(
            charts_dir, f"{safe_filename(app_name)}_wordcloud.png")
        plt.savefig(chart_path, dpi=150, bbox_inches='tight')
        plt.close()
        return chart_path
    except Exception as e:
        print(f"Error creating word cloud: {e}")
        return None


def comprehensive_review_analysis(reviews):
    """Perform comprehensive analysis of reviews"""
    if not reviews:
        return {
            'summary': "No reviews available for analysis.",
            'total_reviews': 0,
            'charts': [],
            'key_insights': []
        }

    # Convert to DataFrame for easier analysis
    reviews_data = []
    all_text = []

    for review in reviews:
        review_text = review.get('review') or review.get(
            'review_text') or review.get('text') or ''
        if review_text:
            all_text.append(review_text)

            # Analyze each review
            sentiment_pol, sentiment_sub = analyze_sentiment(review_text)
            language = detect_language(review_text)

            reviews_data.append({
                'rating': review.get('rating'),
                'text': review_text,
                'platform': review.get('platform'),
                'date': review.get('date') or review.get('review_date'),
                'sentiment': sentiment_pol,
                'subjectivity': sentiment_sub,
                'language': language,
                'text_length': len(review_text)
            })

    if not reviews_data:
        return {
            'summary': "No readable reviews found for analysis.",
            'total_reviews': len(reviews),
            'charts': [],
            'key_insights': []
        }

    df = pd.DataFrame(reviews_data)

    # Basic statistics
    total_reviews = len(reviews)
    readable_reviews = len(reviews_data)

    # Rating analysis
    ratings = df['rating'].dropna()
    if not ratings.empty:
        avg_rating = ratings.mean()
        rating_dist = ratings.value_counts().sort_index()
        positive_reviews = sum(ratings >= 4)
        negative_reviews = sum(ratings <= 2)
        neutral_reviews = sum(ratings == 3)
    else:
        avg_rating = 0
        rating_dist = pd.Series()
        positive_reviews = negative_reviews = neutral_reviews = 0

    # Sentiment analysis
    sentiments = df['sentiment'].dropna()
    avg_sentiment = sentiments.mean() if not sentiments.empty else 0

    # Language analysis
    languages = df['language'].value_counts()
    top_language = languages.index[0] if not languages.empty else 'unknown'

    # Platform analysis
    platforms = df['platform'].value_counts()

    # Key phrases extraction
    key_phrases = extract_key_phrases(all_text, max_phrases=8)

    # Generate insights
    insights = []
    if avg_rating > 0:
        insights.append(f"Average rating: {avg_rating:.1f}/5.0")
    if avg_sentiment != 0:
        sentiment_label = "positive" if avg_sentiment > 0.1 else "negative" if avg_sentiment < -0.1 else "neutral"
        insights.append(
            f"Overall sentiment: {sentiment_label} (score: {avg_sentiment:.2f})")
    if not languages.empty and len(languages) > 1:
        insights.append(
            f"Reviews in {len(languages)} languages, primarily {top_language} ({languages.iloc[0]} reviews)")
    if not platforms.empty:
        insights.append(
            f"Reviews from {len(platforms)} platform(s): {', '.join(platforms.index[:3].tolist())}")
    if key_phrases:
        top_themes = [phrase for phrase, score in key_phrases[:3]]
        insights.append(f"Key themes: {', '.join(top_themes)}")

    summary = f"""
**Total Reviews:** {total_reviews} ({readable_reviews} analyzed)
**Rating Distribution:** {positive_reviews} positive (4-5★), {neutral_reviews} neutral (3★), {negative_reviews} negative (1-2★)
**Average Sentiment:** {avg_sentiment:.2f} (-1=very negative, +1=very positive)
**Primary Language:** {top_language}
**Key Insights:** {' | '.join(insights)}
""".strip()

    return {
        'summary': summary,
        'total_reviews': total_reviews,
        'dataframe': df,
        'key_phrases': key_phrases,
        'key_insights': insights,
        'rating_distribution': rating_dist.to_dict() if not rating_dist.empty else {},
        'language_distribution': languages.head(5).to_dict(),
        'platform_distribution': platforms.to_dict(),
        'all_text': ' '.join(all_text)
    }


def create_comprehensive_md(app_data, charts_dir):
    """Create comprehensive markdown file with advanced analytics"""
    name = app_data.get('name') or app_data.get(
        'google_package') or 'Unknown App'
    google = app_data.get('google') or {}
    apple = app_data.get('apple') or {}

    # App metadata
    package_name = app_data.get('google_package', 'N/A')
    google_title = google.get('title', 'N/A')
    apple_title = apple.get('title', 'N/A') if apple else 'N/A'

    # Ratings and metadata
    google_rating = google.get('rating', 'N/A')
    google_total_ratings = google.get('ratings_total', 'N/A')
    google_installs = google.get('installs', 'N/A')
    google_genre = google.get('genre', 'N/A')

    apple_rating = apple.get('rating', 'N/A') if apple else 'N/A'
    apple_total_ratings = apple.get('ratings_total', 'N/A') if apple else 'N/A'

    # Description (keep intact as requested)
    description = google.get('description', apple.get(
        'description', 'No description available') if apple else 'No description available')

    # Reviews analysis
    reviews = app_data.get('reviews') or []
    analysis = comprehensive_review_analysis(reviews)

    # Create charts
    charts_created = []
    wordcloud_path = None

    if 'dataframe' in analysis and not analysis['dataframe'].empty:
        charts_created = create_charts(name, analysis['dataframe'], charts_dir)

    if 'all_text' in analysis and analysis['all_text']:
        wordcloud_path = create_wordcloud(
            analysis['all_text'], name, charts_dir)
        if wordcloud_path:
            charts_created.append(wordcloud_path)

    # Build markdown content
    md_content = f"""# {name}

## 📱 App Information

| **Attribute** | **Google Play** | **App Store** |
|---------------|-----------------|---------------|
| **Title** | {google_title} | {apple_title} |
| **Package/ID** | {package_name} | N/A |
| **Rating** | {google_rating} | {apple_rating} |
| **Total Ratings** | {google_total_ratings:,} | {apple_total_ratings} |
| **Installs** | {google_installs} | N/A |
| **Genre** | {google_genre} | N/A |

## 📝 Description

{description}

## 📊 Reviews Analytics

{analysis['summary']}

"""

    # Add key phrases if available
    if 'key_phrases' in analysis and analysis['key_phrases']:
        md_content += "\n### 🔑 Key Themes & Phrases\n\n"
        for phrase, score in analysis['key_phrases'][:10]:
            md_content += f"- **{phrase}** (relevance: {score:.3f})\n"
        md_content += "\n"

    # Add detailed breakdowns
    if 'rating_distribution' in analysis and analysis['rating_distribution']:
        md_content += "### ⭐ Rating Breakdown\n\n"
        for rating in sorted(analysis['rating_distribution'].keys(), reverse=True):
            count = analysis['rating_distribution'][rating]
            percentage = (count / analysis['total_reviews']) * 100
            stars = "★" * int(rating) + "☆" * (5 - int(rating))
            md_content += f"- **{rating} {stars}**: {count} reviews ({percentage:.1f}%)\n"
        md_content += "\n"

    if 'language_distribution' in analysis and analysis['language_distribution']:
        md_content += "### 🌍 Languages in Reviews\n\n"
        for lang, count in analysis['language_distribution'].items():
            md_content += f"- **{lang}**: {count} reviews\n"
        md_content += "\n"

    if 'platform_distribution' in analysis and analysis['platform_distribution']:
        md_content += "### 📱 Platform Distribution\n\n"
        for platform, count in analysis['platform_distribution'].items():
            md_content += f"- **{platform}**: {count} reviews\n"
        md_content += "\n"

    # Add charts if created
    if charts_created:
        md_content += "## 📈 Visualizations\n\n"
        for chart_path in charts_created:
            chart_name = os.path.basename(chart_path)
            relative_path = f"charts/{chart_name}"
            if "wordcloud" in chart_name.lower():
                md_content += f"### Word Cloud\n![Word Cloud]({relative_path})\n\n"
            else:
                md_content += f"### Analytics Charts\n![Analytics]({relative_path})\n\n"

    # Sample reviews section
    if reviews:
        md_content += "## 💬 Sample Reviews\n\n"
        # Show a few representative reviews
        sample_reviews = reviews[:5] if len(reviews) <= 5 else [
            reviews[0],  # First
            reviews[len(reviews)//4],  # Quarter
            reviews[len(reviews)//2],  # Middle
            reviews[3*len(reviews)//4],  # Three-quarter
            reviews[-1]  # Last
        ]

        for i, review in enumerate(sample_reviews, 1):
            rating = review.get('rating', 'N/A')
            text = review.get('review') or review.get(
                'review_text') or review.get('text', '')
            date = review.get('date') or review.get('review_date', 'N/A')
            platform = review.get('platform', 'N/A')

            # Truncate very long reviews
            if len(text) > 300:
                text = text[:300] + "..."

            stars = "★" * int(rating) if isinstance(rating,
                                                    (int, float)) else "N/A"
            md_content += f"**Review {i}** ({stars} - {platform} - {date})\n> {text}\n\n"

    # Raw data section
    md_content += f"""## 🔧 Raw JSON Data

<details>
<summary>Click to expand raw app data</summary>

```json
{json.dumps(app_data, ensure_ascii=False, indent=2)}
```

</details>

---
*Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} using advanced analytics*
"""

    return md_content


def main():
    """Main function to process all app files and generate comprehensive markdown reports"""
    print("🚀 Starting comprehensive app analysis...")
    print(f"📁 Input directory: {INPUT_DIR}")
    print(f"📁 Output directory: {OUTPUT_DIR}")
    print(f"📊 Charts directory: {CHARTS_DIR}")

    # Check available libraries
    print(f"\n🔧 Available libraries:")
    print(f"   - NLTK/TextBlob: {'✅' if NLTK_AVAILABLE else '❌'}")
    print(f"   - Language Detection: {'✅' if LANGDETECT_AVAILABLE else '❌'}")
    print(f"   - Scikit-learn: {'✅' if SKLEARN_AVAILABLE else '❌'}")
    print(f"   - Pandas/Matplotlib/Seaborn: ✅")
    print(f"   - WordCloud: ✅")

    files = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith(
        '.jsonl') or f.lower().endswith('.json')]
    if not files:
        print(f"❌ No JSON/JSONL files found in {INPUT_DIR}")
        return

    print(f"\n📚 Found {len(files)} app files to process...\n")

    processed = 0
    skipped = 0

    for i, fname in enumerate(files, 1):
        print(f"📱 [{i:3d}/{len(files)}] Processing: {fname}")
        in_path = os.path.join(INPUT_DIR, fname)

        try:
            with open(in_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            print(f"   ❌ Failed to load JSON: {e}")
            skipped += 1
            continue

        try:
            # Generate comprehensive markdown
            md_content = create_comprehensive_md(data, CHARTS_DIR)

            # Choose output filename
            base = data.get('google_package') or data.get(
                'name') or os.path.splitext(fname)[0]
            out_name = safe_filename(base) + '.md'
            out_path = os.path.join(OUTPUT_DIR, out_name)

            with open(out_path, 'w', encoding='utf-8') as out:
                out.write(md_content)

            app_name = data.get('name', base)
            review_count = len(data.get('reviews', []))
            print(
                f"   ✅ Generated: {out_name} ({review_count} reviews analyzed)")
            processed += 1

        except Exception as e:
            print(f"   ❌ Failed to process: {e}")
            skipped += 1

    print(f"\n🎉 Analysis complete!")
    print(f"   ✅ Successfully processed: {processed} apps")
    print(f"   ❌ Skipped due to errors: {skipped} apps")
    print(f"   📄 Markdown files saved to: {OUTPUT_DIR}")
    print(f"   📊 Charts saved to: {CHARTS_DIR}")


if __name__ == '__main__':
    main()
