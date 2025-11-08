import json
import pandas as pd
from collections import Counter
import re
from textblob import TextBlob
from langdetect import detect
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
from pathlib import Path

# Download NLTK data
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)


class LightweightReviewAnalyzer:
    """
    Analyzes reviews using only lightweight libraries
    Works with: pandas, textblob, nltk, scikit-learn
    """

    def __init__(self, reviews_path, output_dir=None):
        """reviews_path: path to concise_duolingo.json (JSON array)
        output_dir: directory where analysis outputs (images, csv) will be written
        """
        self.reviews_path = Path(reviews_path)
        if not self.reviews_path.exists():
            raise FileNotFoundError(
                f"Reviews file not found: {self.reviews_path}")

        with self.reviews_path.open('r', encoding='utf-8') as f:
            self.reviews = json.load(f)

        self.df = pd.DataFrame(self.reviews)

        # Output directory
        if output_dir is None:
            # default to repository relative duolingo/output/sentiment_results
            self.output_dir = Path(__file__).resolve(
            ).parents[1] / 'output' / 'sentiment_results'
        else:
            self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Dutch stopwords
        self.dutch_stopwords = set([
            'de', 'het', 'een', 'en', 'van', 'te', 'dat', 'die', 'in', 'op',
            'is', 'voor', 'met', 'niet', 'aan', 'zijn', 'er', 'maar', 'om',
            'hij', 'ze', 'ook', 'kan', 'meer', 'dan', 'je', 'wel', 'was',
            'mijn', 'heeft', 'zijn', 'worden', 'door', 'deze', 'bij', 'nog',
            'wordt', 'hebben', 'als', 'naar', 'dit', 'uit', 'worden', 'zou'
        ])

        # Category keywords (manually defined)
        self.category_keywords = {
            'battery_issues': ['batterij', 'accu', 'snel op', 'leeg', 'energie'],
            'language_availability': ['taal', 'talen', 'engels', 'pools', 'japans',
                                      'nederlands', 'chinees', 'spaans', 'frans'],
            'app_performance': ['langzaam', 'laden', 'uploaden', 'crash', 'bug',
                                'traag', 'wacht', 'loading'],
            'pricing': ['gratis', 'betaal', 'abonnement', 'geld', 'premium',
                        'kosten', 'noppes'],
            'learning_effectiveness': ['leren', 'goed', 'help', 'nuttig', 'leerzaam',
                                       'vooruitgang', 'niveau'],
            'lessons_content': ['les', 'lessen', 'oefening', 'opgave', 'vragen'],
            'user_experience': ['leuk', 'fijn', 'plezier', 'makkelijk', 'moeilijk',
                                'app', 'interface'],
            'gamification': ['punten', 'streak', 'duo', 'motivatie', 'dagelijks']
        }

    def detect_language(self):
        """Detect language of each review"""
        languages = []
        for content in self.df['content']:
            try:
                lang = detect(content)
                languages.append(lang)
            except:
                languages.append('unknown')

        self.df['language'] = languages
        return self.df

    def simple_sentiment_analysis(self):
        """
        Simple sentiment using TextBlob
        Note: Works better with English, but gives rough estimate for Dutch
        """
        polarities = []
        sentiments = []

        for content in self.df['content']:
            # TextBlob can work with Dutch but not perfectly
            blob = TextBlob(content)
            polarity = blob.sentiment.polarity
            polarities.append(polarity)

            # Classify
            if polarity > 0.1:
                sentiments.append('positive')
            elif polarity < -0.1:
                sentiments.append('negative')
            else:
                sentiments.append('neutral')

        self.df['polarity'] = polarities
        self.df['sentiment'] = sentiments
        return self.df

    def keyword_based_sentiment(self):
        """
        More accurate: Use Dutch positive/negative keywords
        """
        positive_words = [
            'goed', 'leuk', 'fijn', 'geweldig', 'super', 'mooi', 'perfect',
            'uitstekend', 'fantastisch', 'prachtig', 'help', 'handig', 'blij'
        ]

        negative_words = [
            'slecht', 'traag', 'langzaam', 'bug', 'crash', 'niet', 'geen',
            'probleem', 'vervelend', 'irritant', 'lastig', 'jammer', 'teleurgesteld'
        ]

        sentiments = []
        scores = []

        for content in self.df['content']:
            content_lower = content.lower()

            # Count positive and negative words
            pos_count = sum(
                1 for word in positive_words if word in content_lower)
            neg_count = sum(
                1 for word in negative_words if word in content_lower)

            # Calculate score
            score = pos_count - neg_count
            scores.append(score)

            # Classify
            if score > 0:
                sentiments.append('positive')
            elif score < 0:
                sentiments.append('negative')
            else:
                sentiments.append('neutral')

        self.df['keyword_sentiment'] = sentiments
        self.df['keyword_score'] = scores
        return self.df

    def extract_categories(self):
        """Categorize reviews based on keyword matching"""
        review_categories = []

        for content in self.df['content']:
            content_lower = content.lower()
            matched = []

            for category, keywords in self.category_keywords.items():
                if any(keyword in content_lower for keyword in keywords):
                    matched.append(category)

            review_categories.append(matched if matched else ['general'])

        self.df['categories'] = review_categories
        return self.df

    def extract_key_phrases(self, min_length=2):
        """Extract important n-grams using TF-IDF"""
        # Combine all text
        texts = self.df['content'].tolist()

        # TF-IDF vectorizer for bigrams and trigrams
        vectorizer = TfidfVectorizer(
            ngram_range=(min_length, 3),
            max_features=50,
            stop_words=list(self.dutch_stopwords)
        )

        try:
            tfidf_matrix = vectorizer.fit_transform(texts)
            feature_names = vectorizer.get_feature_names_out()

            # Get top terms
            top_terms = []
            for idx in tfidf_matrix.sum(axis=0).A1.argsort()[-20:][::-1]:
                top_terms.append(feature_names[idx])

            return top_terms
        except:
            return []

    def cluster_reviews(self, n_clusters=5):
        """Group similar reviews together"""
        texts = self.df['content'].tolist()

        # Vectorize
        vectorizer = TfidfVectorizer(
            max_features=100,
            stop_words=list(self.dutch_stopwords)
        )

        X = vectorizer.fit_transform(texts)

        # K-means clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        clusters = kmeans.fit_predict(X)

        self.df['cluster'] = clusters

        # Get top terms per cluster
        feature_names = vectorizer.get_feature_names_out()
        cluster_terms = {}

        for i in range(n_clusters):
            center = kmeans.cluster_centers_[i]
            top_indices = center.argsort()[-5:][::-1]
            cluster_terms[i] = [feature_names[idx] for idx in top_indices]

        return cluster_terms

    def visualize_sentiment_distribution(self):
        """Create sentiment distribution chart"""
        plt.figure(figsize=(10, 6))

        sentiment_counts = self.df['keyword_sentiment'].value_counts()
        colors = {'positive': '#2ecc71',
                  'negative': '#e74c3c', 'neutral': '#95a5a6'}

        bars = plt.bar(sentiment_counts.index, sentiment_counts.values,
                       color=[colors[s] for s in sentiment_counts.index])

        plt.title('Sentiment Distribution of Duolingo Reviews',
                  fontsize=16, fontweight='bold')
        plt.xlabel('Sentiment', fontsize=12)
        plt.ylabel('Number of Reviews', fontsize=12)

        # Add counts on bars
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                     f'{int(height)}',
                     ha='center', va='bottom', fontsize=12)

        plt.tight_layout()
        outpath = self.output_dir / 'sentiment_distribution.png'
        plt.savefig(outpath, dpi=300, bbox_inches='tight')
        print(f"✅ Saved: {outpath}")

    def visualize_categories(self):
        """Visualize category frequency"""
        # Flatten categories
        all_categories = []
        for cats in self.df['categories']:
            all_categories.extend(cats)

        category_counts = Counter(all_categories)

        plt.figure(figsize=(12, 6))
        categories = list(category_counts.keys())
        counts = list(category_counts.values())

        plt.barh(categories, counts, color='#3498db')
        plt.xlabel('Number of Mentions', fontsize=12)
        plt.title('Topics Mentioned in Reviews',
                  fontsize=16, fontweight='bold')
        plt.tight_layout()
        outpath = self.output_dir / 'category_distribution.png'
        plt.savefig(outpath, dpi=300, bbox_inches='tight')
        print(f"✅ Saved: {outpath}")

    def create_wordcloud(self, sentiment_filter=None):
        """Generate word cloud"""
        if sentiment_filter:
            text = ' '.join(
                self.df[self.df['keyword_sentiment'] == sentiment_filter]['content'])
            filename = f'wordcloud_{sentiment_filter}.png'
        else:
            text = ' '.join(self.df['content'])
            filename = 'wordcloud_all.png'

        wordcloud = WordCloud(
            width=1600,
            height=800,
            background_color='white',
            stopwords=self.dutch_stopwords,
            colormap='viridis',
            max_words=100
        ).generate(text)

        plt.figure(figsize=(16, 8))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.title(f'Word Cloud - {sentiment_filter or "All Reviews"}',
                  fontsize=20, fontweight='bold')
        plt.tight_layout()
        outpath = self.output_dir / filename
        plt.savefig(outpath, dpi=300, bbox_inches='tight')
        print(f"✅ Saved: {outpath}")

    def analyze_by_category(self):
        """Sentiment breakdown per category"""
        category_sentiment = {}

        for idx, row in self.df.iterrows():
            sentiment = row['keyword_sentiment']
            for category in row['categories']:
                if category not in category_sentiment:
                    category_sentiment[category] = {
                        'positive': 0, 'negative': 0, 'neutral': 0}
                category_sentiment[category][sentiment] += 1

        return category_sentiment

    def generate_report(self):
        """Comprehensive analysis report"""
        print("\n" + "="*70)
        print("📊 DUOLINGO REVIEW ANALYSIS REPORT")
        print("="*70)

        # Basic stats
        print(f"\n📈 Dataset Overview:")
        print(f"   Total reviews: {len(self.df)}")
        print(f"   Date range: {self.df['author'].nunique()} unique authors")

        # Sentiment breakdown
        print(f"\n💭 Sentiment Analysis (Keyword-based):")
        sentiment_counts = self.df['keyword_sentiment'].value_counts()
        for sentiment, count in sentiment_counts.items():
            pct = count / len(self.df) * 100
            emoji = '😊' if sentiment == 'positive' else '😞' if sentiment == 'negative' else '😐'
            print(f"   {emoji} {sentiment.capitalize()}: {count} ({pct:.1f}%)")

        # Category analysis
        print(f"\n📂 Topic Analysis:")
        category_sentiment = self.analyze_by_category()
        for category, sentiments in sorted(category_sentiment.items()):
            total = sum(sentiments.values())
            pos_pct = sentiments['positive'] / total * 100 if total > 0 else 0
            neg_pct = sentiments['negative'] / total * 100 if total > 0 else 0
            print(f"   • {category.replace('_', ' ').title()}: "
                  f"{pos_pct:.0f}% 👍 | {neg_pct:.0f}% 👎 (n={total})")

        # Key phrases
        print(f"\n🔑 Most Important Phrases:")
        key_phrases = self.extract_key_phrases()
        for i, phrase in enumerate(key_phrases[:10], 1):
            print(f"   {i}. {phrase}")

        # Clustering insights
        print(f"\n🎯 Review Clusters (Main Themes):")
        cluster_terms = self.cluster_reviews(n_clusters=5)
        for cluster_id, terms in cluster_terms.items():
            print(f"   Cluster {cluster_id + 1}: {', '.join(terms)}")

        # Sample reviews
        print(f"\n💚 Top Positive Reviews:")
        positive = self.df[self.df['keyword_sentiment']
                           == 'positive'].nlargest(2, 'keyword_score')
        for idx, row in positive.iterrows():
            print(f"   → {row['content'][:120]}...")

        print(f"\n💔 Top Negative Reviews:")
        negative = self.df[self.df['keyword_sentiment']
                           == 'negative'].nsmallest(2, 'keyword_score')
        for idx, row in negative.iterrows():
            print(f"   → {row['content'][:120]}...")

        print("\n" + "="*70)

    def run_full_analysis(self):
        """Execute complete analysis pipeline"""
        print("🚀 Starting analysis...\n")

        # Run all analyses
        self.detect_language()
        self.simple_sentiment_analysis()
        self.keyword_based_sentiment()
        self.extract_categories()

        # Generate visualizations
        print("📊 Generating visualizations...")
        self.visualize_sentiment_distribution()
        self.visualize_categories()
        self.create_wordcloud()
        self.create_wordcloud('positive')
        self.create_wordcloud('negative')

        # Generate report
        self.generate_report()

        # Export results into output directory
        out_csv = self.output_dir / 'analyzed_reviews.csv'
        self.df.to_csv(out_csv, index=False)
        print(f"\n✅ Results exported to '{out_csv}'")

        return self.df


# Usage
if __name__ == "__main__":
    # Default input: duolingo/data/concise_duolingo.json (relative to repo)
    default_input = Path(__file__).resolve(
    ).parents[1] / 'data' / 'concise_duolingo.json'
    default_output = Path(__file__).resolve(
    ).parents[1] / 'output' / 'sentiment_results'

    analyzer = LightweightReviewAnalyzer(
        default_input, output_dir=default_output)
    results = analyzer.run_full_analysis()
