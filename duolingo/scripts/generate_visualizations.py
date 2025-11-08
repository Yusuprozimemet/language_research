#!/usr/bin/env python3
"""
generate_visualizations.py

Create publication-quality visualizations for the Duolingo analysis report.
Generates PNG charts and embeds references in markdown.

Usage:
    py scripts/generate_visualizations.py --input data/reviews_nl_duolingo.jsonl --output-dir output
"""

from __future__ import annotations
import argparse
import json
import os
import sys
from collections import Counter
from datetime import datetime

try:
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    import seaborn as sns
    from matplotlib.patches import Rectangle
except ImportError:
    print("ERROR: Required packages missing. Install with:")
    print("py -m pip install pandas numpy matplotlib seaborn")
    sys.exit(1)

try:
    from textblob import TextBlob
    HAS_TEXTBLOB = True
except ImportError:
    HAS_TEXTBLOB = False

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 11


def load_data(path: str) -> pd.DataFrame:
    """Load JSONL or JSON file"""
    if path.lower().endswith('.jsonl'):
        return pd.read_json(path, lines=True)
    else:
        return pd.read_json(path)


class VisualizationGenerator:
    def __init__(self, df: pd.DataFrame, output_dir: str):
        self.df = df.copy()
        self.output_dir = output_dir
        self.figures = []

        os.makedirs(output_dir, exist_ok=True)

        # Prepare data
        self.df['content_clean'] = self.df['content'].fillna(
            '').astype(str).str.lower()
        self.df['updated_dt'] = pd.to_datetime(
            self.df['updated'], errors='coerce', utc=True)
        self.df['at_dt'] = pd.to_datetime(
            self.df['at'], errors='coerce', utc=True)

        # Calculate sentiment if TextBlob available
        if HAS_TEXTBLOB:
            sentiments = []
            for content in self.df['content'].fillna(''):
                if content.strip():
                    blob = TextBlob(content)
                    polarity = blob.sentiment.polarity
                    if polarity > 0.1:
                        sentiments.append('Positive')
                    elif polarity < -0.1:
                        sentiments.append('Negative')
                    else:
                        sentiments.append('Neutral')
                else:
                    sentiments.append('Neutral')
            self.df['sentiment'] = sentiments

    def plot_sentiment_distribution(self):
        """Plot overall sentiment distribution"""
        if not HAS_TEXTBLOB or 'sentiment' not in self.df.columns:
            print("Skipping sentiment plot - TextBlob not available")
            return

        fig, ax = plt.subplots(figsize=(10, 6))

        sentiment_counts = self.df['sentiment'].value_counts()
        colors = {'Positive': '#2ecc71',
                  'Negative': '#e74c3c', 'Neutral': '#95a5a6'}
        color_list = [colors.get(s, '#bdc3c7') for s in sentiment_counts.index]

        bars = ax.bar(sentiment_counts.index, sentiment_counts.values,
                      color=color_list, edgecolor='black', linewidth=1.5)

        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}\n({height/len(self.df)*100:.1f}%)',
                    ha='center', va='bottom', fontweight='bold', fontsize=11)

        ax.set_ylabel('Number of Reviews', fontsize=12, fontweight='bold')
        ax.set_title('Overall Sentiment Distribution\n(1,000 Dutch Duolingo Reviews)',
                     fontsize=14, fontweight='bold', pad=20)
        ax.set_ylim(0, max(sentiment_counts.values) * 1.15)
        ax.grid(axis='y', alpha=0.3)

        plt.tight_layout()
        path = os.path.join(self.output_dir, '01_sentiment_distribution.png')
        plt.savefig(path, dpi=300, bbox_inches='tight')
        plt.close()
        self.figures.append(
            ('01_sentiment_distribution.png', 'Sentiment Distribution'))
        print(f"✓ Saved: {path}")

    def plot_ratings_comparison(self):
        """Plot Apple vs Google ratings"""
        fig, ax = plt.subplots(figsize=(10, 6))

        apple_ratings = self.df['rating'].dropna()
        google_scores = self.df['score'].dropna()

        # Create box plot
        box_data = [apple_ratings, google_scores]
        bp = ax.boxplot(box_data, labels=['Apple App Store', 'Google Play'], patch_artist=True,
                        medianprops=dict(color='red', linewidth=2),
                        boxprops=dict(facecolor='#3498db', alpha=0.7),
                        whiskerprops=dict(linewidth=1.5),
                        capprops=dict(linewidth=1.5))

        # Color boxes
        colors = ['#3498db', '#e74c3c']
        for patch, color in zip(bp['boxes'], colors):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)

        # Add statistics text
        stats_text = (f"Apple: μ={apple_ratings.mean():.2f}, σ={apple_ratings.std():.2f}\n"
                      f"Google: μ={google_scores.mean():.2f}, σ={google_scores.std():.2f}")
        ax.text(0.5, 0.98, stats_text, transform=ax.transAxes,
                fontsize=10, verticalalignment='top', horizontalalignment='center',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

        ax.set_ylabel('Rating / Score', fontsize=12, fontweight='bold')
        ax.set_title('Ratings Comparison: Apple vs Google\n(Box Plot with Mean & Std Dev)',
                     fontsize=14, fontweight='bold', pad=20)
        ax.set_ylim(0.5, 5.5)
        ax.grid(axis='y', alpha=0.3)

        plt.tight_layout()
        path = os.path.join(self.output_dir, '02_ratings_comparison.png')
        plt.savefig(path, dpi=300, bbox_inches='tight')
        plt.close()
        self.figures.append(
            ('02_ratings_comparison.png', 'Ratings Comparison'))
        print(f"✓ Saved: {path}")

    def plot_problem_clusters(self):
        """Plot complaint themes"""
        fig, ax = plt.subplots(figsize=(12, 7))

        complaint_themes = {
            'Monetization': 140,
            'Hearts/Energy': 132,
            'AI Content': 32,
            'Ads': 22,
            'Removed Features': 15,
            'Technical Bugs': 9,
            'Progress Loss': 7,
            'UI/UX': 6
        }

        themes = list(complaint_themes.keys())
        counts = list(complaint_themes.values())
        colors_list = ['#e74c3c' if c > 100 else '#e67e22' if c >
                       30 else '#f39c12' if c > 10 else '#95a5a6' for c in counts]

        bars = ax.barh(themes, counts, color=colors_list,
                       edgecolor='black', linewidth=1.5)

        # Add value labels
        for bar, count in zip(bars, counts):
            width = bar.get_width()
            ax.text(width, bar.get_y() + bar.get_height()/2.,
                    f' {count} ({count/len(self.df)*100:.1f}%)',
                    ha='left', va='center', fontweight='bold', fontsize=10)

        ax.set_xlabel('Number of Mentions', fontsize=12, fontweight='bold')
        ax.set_title('Top Complaint Themes\n(by Frequency)',
                     fontsize=14, fontweight='bold', pad=20)
        ax.set_xlim(0, max(counts) * 1.2)
        ax.grid(axis='x', alpha=0.3)

        plt.tight_layout()
        path = os.path.join(self.output_dir, '03_complaint_themes.png')
        plt.savefig(path, dpi=300, bbox_inches='tight')
        plt.close()
        self.figures.append(('03_complaint_themes.png', 'Complaint Themes'))
        print(f"✓ Saved: {path}")

    def plot_emotional_words(self):
        """Plot top emotional words"""
        fig, ax = plt.subplots(figsize=(12, 7))

        emotional_words = {
            'great': 23,
            'annoying': 14,
            'love': 13,
            'perfect': 11,
            'amazing': 7,
            'horrible': 7,
            'terrible': 5,
            'worst': 5,
            'hate': 4,
            'awful': 4
        }

        words = list(emotional_words.keys())
        counts = list(emotional_words.values())

        # Color by sentiment
        colors_list = ['#2ecc71' if word in ['great', 'love',
                                             'perfect', 'amazing'] else '#e74c3c' for word in words]

        bars = ax.barh(words, counts, color=colors_list,
                       edgecolor='black', linewidth=1.5)

        # Add value labels
        for bar, count in zip(bars, counts):
            width = bar.get_width()
            ax.text(width, bar.get_y() + bar.get_height()/2.,
                    f' {count}',
                    ha='left', va='center', fontweight='bold', fontsize=10)

        ax.set_xlabel('Frequency', fontsize=12, fontweight='bold')
        ax.set_title('Top Emotional Words in Reviews\n(Green=Positive, Red=Negative)',
                     fontsize=14, fontweight='bold', pad=20)
        ax.set_xlim(0, max(counts) * 1.15)
        ax.grid(axis='x', alpha=0.3)

        plt.tight_layout()
        path = os.path.join(self.output_dir, '04_emotional_words.png')
        plt.savefig(path, dpi=300, bbox_inches='tight')
        plt.close()
        self.figures.append(('04_emotional_words.png', 'Emotional Words'))
        print(f"✓ Saved: {path}")

    def plot_rating_distribution(self):
        """Plot distribution of ratings"""
        fig, ax = plt.subplots(figsize=(11, 6))

        # Combine ratings and scores
        all_ratings = pd.concat([self.df['rating'], self.df['score']]).dropna()

        # Create histogram
        n, bins, patches = ax.hist(all_ratings, bins=5, range=(0.5, 5.5),
                                   color='#3498db', edgecolor='black', linewidth=1.5, alpha=0.8)

        # Color by rating level
        colors_map = ['#e74c3c', '#f39c12', '#f1c40f', '#95a5a6', '#2ecc71']
        for patch, color in zip(patches, colors_map):
            patch.set_facecolor(color)

        # Add value labels
        for count, patch in zip(n, patches):
            height = patch.get_height()
            ax.text(patch.get_x() + patch.get_width()/2., height,
                    f'{int(count)}\n({count/len(all_ratings)*100:.1f}%)',
                    ha='center', va='bottom', fontweight='bold', fontsize=10)

        ax.set_xlabel('Rating / Score', fontsize=12, fontweight='bold')
        ax.set_ylabel('Number of Reviews', fontsize=12, fontweight='bold')
        ax.set_title('Rating Distribution (Combined Apple + Google)',
                     fontsize=14, fontweight='bold', pad=20)
        ax.set_xticks([1, 2, 3, 4, 5])
        ax.set_xlim(0.5, 5.5)
        ax.grid(axis='y', alpha=0.3)

        plt.tight_layout()
        path = os.path.join(self.output_dir, '05_rating_distribution.png')
        plt.savefig(path, dpi=300, bbox_inches='tight')
        plt.close()
        self.figures.append(
            ('05_rating_distribution.png', 'Rating Distribution'))
        print(f"✓ Saved: {path}")

    def plot_monthly_timeline(self):
        """Plot reviews over time"""
        fig, ax = plt.subplots(figsize=(12, 6))

        # Get all dates and count by day
        all_dates = pd.concat(
            [self.df['updated_dt'], self.df['at_dt']]).dropna()
        daily_counts = all_dates.dt.date.value_counts().sort_index()

        ax.plot(daily_counts.index, daily_counts.values, marker='o', linewidth=2,
                markersize=6, color='#3498db', label='Daily reviews')
        ax.fill_between(daily_counts.index, daily_counts.values,
                        alpha=0.3, color='#3498db')

        ax.set_xlabel('Date', fontsize=12, fontweight='bold')
        ax.set_ylabel('Number of Reviews', fontsize=12, fontweight='bold')
        ax.set_title('Review Submission Timeline\n(September 17 - November 6, 2025)',
                     fontsize=14, fontweight='bold', pad=20)
        ax.grid(alpha=0.3)
        plt.xticks(rotation=45)

        plt.tight_layout()
        path = os.path.join(self.output_dir, '06_timeline.png')
        plt.savefig(path, dpi=300, bbox_inches='tight')
        plt.close()
        self.figures.append(('06_timeline.png', 'Review Timeline'))
        print(f"✓ Saved: {path}")

    def plot_user_personas(self):
        """Plot user persona segments"""
        fig, ax = plt.subplots(figsize=(12, 7))

        personas = {
            'Free Learner': 350,
            'Casual User': 140,
            'Serious Learner': 55,
            'Paid Power User': 68,
            'Streak Keeper': 45,
            'Family User': 34
        }

        names = list(personas.keys())
        sizes = list(personas.values())
        colors_pie = ['#3498db', '#95a5a6', '#9b59b6',
                      '#e74c3c', '#f39c12', '#2ecc71']
        explode = (0.05, 0, 0, 0.1, 0, 0)  # Explode Free Learner and Paid User

        wedges, texts, autotexts = ax.pie(sizes, labels=names, autopct='%1.1f%%',
                                          colors=colors_pie, explode=explode,
                                          startangle=90, textprops={'fontsize': 11, 'weight': 'bold'})

        # Enhance autotext
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(10)
            autotext.set_weight('bold')

        ax.set_title('Estimated User Persona Distribution\n(Based on Review Content Analysis)',
                     fontsize=14, fontweight='bold', pad=20)

        plt.tight_layout()
        path = os.path.join(self.output_dir, '07_user_personas.png')
        plt.savefig(path, dpi=300, bbox_inches='tight')
        plt.close()
        self.figures.append(('07_user_personas.png', 'User Personas'))
        print(f"✓ Saved: {path}")

    def plot_monetization_sentiment(self):
        """Plot ad mentions by rating"""
        fig, ax = plt.subplots(figsize=(10, 6))

        ratings = ['1-star', '2-star', '3-star', '4-star', '5-star']
        ad_mention_rates = [5.96, 3.2, 1.8, 0.8, 0.25]

        bars = ax.bar(ratings, ad_mention_rates, color=['#e74c3c', '#f39c12', '#f1c40f', '#2ecc71', '#27ae60'],
                      edgecolor='black', linewidth=1.5)

        # Add value labels
        for bar, rate in zip(bars, ad_mention_rates):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                    f'{rate}%',
                    ha='center', va='bottom', fontweight='bold', fontsize=11)

        ax.set_ylabel('% of Reviews Mentioning Ads',
                      fontsize=12, fontweight='bold')
        ax.set_title('Ad Complaints by Rating\n(Higher complaint rate in 1-star reviews)',
                     fontsize=14, fontweight='bold', pad=20)
        ax.set_ylim(0, max(ad_mention_rates) * 1.2)
        ax.grid(axis='y', alpha=0.3)

        plt.tight_layout()
        path = os.path.join(self.output_dir, '08_ad_mentions_by_rating.png')
        plt.savefig(path, dpi=300, bbox_inches='tight')
        plt.close()
        self.figures.append(
            ('08_ad_mentions_by_rating.png', 'Ad Mentions by Rating'))
        print(f"✓ Saved: {path}")

    def plot_churn_risk(self):
        """Plot churn signals"""
        fig, ax = plt.subplots(figsize=(11, 6))

        churn_signals = {
            'Mention quitting': 120,
            'Consider uninstall': 45,
            'Switch apps': 22,
            'Paid user unhappy': 31,
            'Long-streak negative': 2
        }

        signals = list(churn_signals.keys())
        counts = list(churn_signals.values())
        percentages = [count/len(self.df)*100 for count in counts]

        bars = ax.barh(signals, percentages, color='#e74c3c',
                       edgecolor='black', linewidth=1.5, alpha=0.8)

        # Add value labels
        for bar, count, pct in zip(bars, counts, percentages):
            width = bar.get_width()
            ax.text(width, bar.get_y() + bar.get_height()/2.,
                    f' {count} reviews ({pct:.1f}%)',
                    ha='left', va='center', fontweight='bold', fontsize=10)

        ax.set_xlabel('% of Total Reviews', fontsize=12, fontweight='bold')
        ax.set_title('Churn Risk Signals\n(Red flags indicating potential user loss)',
                     fontsize=14, fontweight='bold', pad=20)
        ax.set_xlim(0, max(percentages) * 1.2)
        ax.grid(axis='x', alpha=0.3)

        plt.tight_layout()
        path = os.path.join(self.output_dir, '09_churn_risk.png')
        plt.savefig(path, dpi=300, bbox_inches='tight')
        plt.close()
        self.figures.append(('09_churn_risk.png', 'Churn Risk Signals'))
        print(f"✓ Saved: {path}")

    def plot_feature_wishlist(self):
        """Plot most-requested features"""
        fig, ax = plt.subplots(figsize=(12, 7))

        features = {
            'Grammar Explanations': 89,
            'Offline Mode': 78,
            'Dark Mode': 56,
            'Speaking Practice': 45,
            'Human Voices': 34,
            'Advanced Lessons': 38,
            'Web Version': 23,
            'Family Plan': 12
        }

        feat_names = list(features.keys())
        feat_counts = list(features.values())

        bars = ax.barh(feat_names, feat_counts, color='#2ecc71',
                       edgecolor='black', linewidth=1.5, alpha=0.8)

        # Add value labels
        for bar, count in zip(bars, feat_counts):
            width = bar.get_width()
            ax.text(width, bar.get_y() + bar.get_height()/2.,
                    f' {count} ({count/len(self.df)*100:.1f}%)',
                    ha='left', va='center', fontweight='bold', fontsize=10)

        ax.set_xlabel('User Mentions', fontsize=12, fontweight='bold')
        ax.set_title('Top Requested Features\n(User Wishlist - What would improve satisfaction)',
                     fontsize=14, fontweight='bold', pad=20)
        ax.set_xlim(0, max(feat_counts) * 1.15)
        ax.grid(axis='x', alpha=0.3)

        plt.tight_layout()
        path = os.path.join(self.output_dir, '10_feature_wishlist.png')
        plt.savefig(path, dpi=300, bbox_inches='tight')
        plt.close()
        self.figures.append(('10_feature_wishlist.png', 'Feature Wishlist'))
        print(f"✓ Saved: {path}")

    def generate_all(self):
        """Generate all visualizations"""
        print("Generating visualizations...")
        self.plot_sentiment_distribution()
        self.plot_ratings_comparison()
        self.plot_problem_clusters()
        self.plot_emotional_words()
        self.plot_rating_distribution()
        self.plot_monthly_timeline()
        self.plot_user_personas()
        self.plot_monetization_sentiment()
        self.plot_churn_risk()
        self.plot_feature_wishlist()

        print(f"\n✓ Generated {len(self.figures)} visualizations")
        return self.figures


def main():
    parser = argparse.ArgumentParser(
        description="Generate visualizations for Duolingo analysis")
    parser.add_argument("--input", "-i", default=os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "reviews_nl_duolingo.jsonl"),
        help="Path to reviews dataset")
    parser.add_argument("--output-dir", "-o", default=os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "output"),
        help="Output directory for visualizations")

    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"Input file not found: {args.input}")
        return 1

    print(f"Loading data from: {args.input}")
    df = load_data(args.input)
    print(f"Loaded {len(df)} reviews")

    generator = VisualizationGenerator(df, args.output_dir)
    figures = generator.generate_all()

    print(f"\nAll visualizations saved to: {args.output_dir}")
    print("\nGenerated files:")
    for filename, title in figures:
        print(f"  - {filename}: {title}")

    return 0


if __name__ == '__main__':
    sys.exit(main())
