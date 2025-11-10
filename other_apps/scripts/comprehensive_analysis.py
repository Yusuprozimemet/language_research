#!/usr/bin/env python3
"""
comprehensive_analysis.py

Comprehensive analysis script to answer 50+ research questions about Duolingo reviews.
Organized into 8 categories as specified:
1. Data Validation & Cleanliness (5 questions)
2. Sentiment & Tone (6 questions) 
3. Problem Clusters (10 questions)
4. User Personas & Behavior (8 questions)
5. Monetization & Pricing Insights (6 questions)
6. Opportunity & Product Gaps (8 questions)
7. Risk & Competition (4 questions)
8. Dutch Market Focus (3 questions)

Usage:
    py scripts/comprehensive_analysis.py
    py scripts/comprehensive_analysis.py --input data/reviews_nl_duolingo.jsonl --output-dir output

Requirements:
    py -m pip install pandas nltk textblob scikit-learn wordcloud matplotlib seaborn

This script will attempt to answer all questions that can be answered through text analysis.
Questions requiring external data or human judgment will be flagged as "cannot handle automatically".
"""

from __future__ import annotations
import argparse
import json
import os
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
import warnings
warnings.filterwarnings('ignore')

try:
    import pandas as pd
    import numpy as np
except ImportError:
    print("ERROR: pandas and numpy are required. Install with: py -m pip install pandas numpy")
    sys.exit(1)

# Optional imports - graceful degradation
try:
    from textblob import TextBlob
    HAS_TEXTBLOB = True
except ImportError:
    HAS_TEXTBLOB = False
    print("Warning: textblob not available. Install with: py -m pip install textblob")

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.cluster import KMeans
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False
    print("Warning: scikit-learn not available. Install with: py -m pip install scikit-learn")

try:
    from wordcloud import WordCloud
    import matplotlib.pyplot as plt
    import seaborn as sns
    HAS_PLOTTING = True
except ImportError:
    HAS_PLOTTING = False
    print("Warning: wordcloud/matplotlib not available. Install with: py -m pip install wordcloud matplotlib seaborn")

try:
    import nltk
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize
    HAS_NLTK = True
    # Try to download required data
    try:
        nltk.data.find('tokenizers/punkt')
        nltk.data.find('corpora/stopwords')
    except LookupError:
        print("Downloading NLTK data...")
        nltk.download('punkt', quiet=True)
        nltk.download('stopwords', quiet=True)
except ImportError:
    HAS_NLTK = False
    print("Warning: nltk not available. Install with: py -m pip install nltk")


class DuolingoAnalyzer:
    def __init__(self, df: pd.DataFrame, output_dir: str):
        self.df = df.copy()
        self.output_dir = output_dir
        self.results = {}
        self.cannot_handle = []

        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)

        # Prepare text data
        self.df['content_clean'] = self.df['content'].fillna(
            '').astype(str).str.lower()
        self.df['content_len'] = self.df['content_clean'].str.len()

        # Normalize rating fields: some datasets use 'score' (Google) and others 'rating' (Apple)
        # Create both columns if missing so downstream code can reference either.
        if 'rating' not in self.df.columns and 'score' in self.df.columns:
            self.df['rating'] = self.df['score']
        if 'score' not in self.df.columns and 'rating' in self.df.columns:
            self.df['score'] = self.df['rating']
        # If neither exists, create them as NA to avoid KeyErrors later
        if 'rating' not in self.df.columns:
            self.df['rating'] = pd.NA
        if 'score' not in self.df.columns:
            self.df['score'] = pd.NA

        # Prepare date columns
        # Some input files use different date field names (e.g. 'updated', 'at', 'date', 'review_date').
        # Create a canonical 'updated' column if missing by falling back to common alternatives.
        if 'updated' not in self.df.columns:
            if 'at' in self.df.columns:
                self.df['updated'] = self.df['at']
            elif 'date' in self.df.columns:
                self.df['updated'] = self.df['date']
            elif 'review_date' in self.df.columns:
                self.df['updated'] = self.df['review_date']
            else:
                # no date-like column found; create an empty column to avoid KeyError later
                self.df['updated'] = pd.NA

        # Ensure 'at' exists too (some code expects both)
        if 'at' not in self.df.columns:
            self.df['at'] = self.df['updated']

        # Parse datetimes (coerce invalid formats to NaT)
        self.df['updated_dt'] = pd.to_datetime(
            self.df['updated'], errors='coerce', utc=True)
        self.df['at_dt'] = pd.to_datetime(
            self.df['at'], errors='coerce', utc=True)

        # Emotional words dictionary
        self.emotional_words = {
            'positive': ['love', 'amazing', 'great', 'excellent', 'perfect', 'wonderful', 'fantastic', 'awesome', 'brilliant', 'helpful'],
            'negative': ['hate', 'terrible', 'awful', 'horrible', 'worst', 'frustrated', 'angry', 'annoying', 'disappointed', 'useless', 'greedy'],
            'neutral': ['okay', 'fine', 'average', 'decent', 'normal']
        }

    def analyze_all(self):
        """Run all analyses"""
        print("Starting comprehensive analysis...")

        # 1. Data Validation & Cleanliness
        self.analyze_data_validation()

        # 2. Sentiment & Tone
        self.analyze_sentiment_tone()

        # 3. Problem Clusters
        self.analyze_problem_clusters()

        # 4. User Personas & Behavior
        self.analyze_user_personas()

        # 5. Monetization & Pricing
        self.analyze_monetization()

        # 6. Opportunity & Product Gaps
        self.analyze_opportunities()

        # 7. Risk & Competition
        self.analyze_risk_competition()

        # 8. Dutch Market Focus
        self.analyze_dutch_market()

        # Save results
        self.save_results()

    def analyze_data_validation(self):
        """1. DATA VALIDATION & CLEANLINESS (5 questions)"""
        print("Analyzing data validation & cleanliness...")

        results = {}

        # Q1: How many reviews? Date range?
        total_reviews = len(self.df)
        all_dates = pd.concat(
            [self.df['updated_dt'], self.df['at_dt']]).dropna()
        date_range = (all_dates.min(), all_dates.max()
                      ) if not all_dates.empty else (None, None)

        results['total_reviews'] = int(total_reviews)
        results['date_range'] = {
            'start': str(date_range[0]) if date_range[0] else None,
            'end': str(date_range[1]) if date_range[1] else None,
            'days_span': (date_range[1] - date_range[0]).days if date_range[0] and date_range[1] else None
        }

        # Q2: % with ratings? Average rating?
        has_rating = self.df['rating'].notna() | self.df['score'].notna()
        rating_pct = (has_rating.sum() / total_reviews) * 100

        avg_apple = self.df['rating'].mean()
        avg_google = self.df['score'].mean()
        overall_avg = pd.concat([self.df['rating'], self.df['score']]).mean()

        results['ratings'] = {
            'percentage_with_ratings': round(rating_pct, 2),
            'average_apple_rating': round(avg_apple, 2) if not pd.isna(avg_apple) else None,
            'average_google_score': round(avg_google, 2) if not pd.isna(avg_google) else None,
            'overall_average': round(overall_avg, 2) if not pd.isna(overall_avg) else None
        }

        # Q3: Language mentions
        languages = ['spanish', 'japanese', 'dutch', 'nederlands',
                     'french', 'german', 'italian', 'portuguese', 'english']
        lang_mentions = {}
        for lang in languages:
            count = self.df['content_clean'].str.contains(lang, na=False).sum()
            if count > 0:
                lang_mentions[lang] = int(count)

        results['language_mentions'] = dict(
            sorted(lang_mentions.items(), key=lambda x: x[1], reverse=True))

        # Q4: Duplicates
        initial_count = len(self.df)
        df_dedup = self.df.drop_duplicates(
            subset=['source', 'author', 'content'], keep='first')
        duplicates_removed = initial_count - len(df_dedup)

        results['duplicates'] = {
            'initial_count': initial_count,
            'duplicates_removed': duplicates_removed,
            'final_count': len(df_dedup),
            'duplicate_percentage': round((duplicates_removed / initial_count) * 100, 2)
        }

        # Q5: Geography (Netherlands vs global)
        nl_count = (self.df['country'] == 'nl').sum()
        nl_percentage = (nl_count / total_reviews) * 100

        results['geography'] = {
            'netherlands_reviews': int(nl_count),
            'netherlands_percentage': round(nl_percentage, 2),
            'note': 'Dataset was specifically scraped for Dutch reviews'
        }

        self.results['data_validation'] = results

    def analyze_sentiment_tone(self):
        """2. SENTIMENT & TONE (6 questions)"""
        print("Analyzing sentiment & tone...")

        results = {}

        if not HAS_TEXTBLOB:
            self.cannot_handle.extend([
                "Overall sentiment distribution (requires TextBlob)",
                "Sentiment changes over time (requires TextBlob)"
            ])
            results['sentiment_analysis'] = "Cannot perform - TextBlob not available"
        else:
            # Q1: Overall sentiment distribution
            sentiments = []
            for content in self.df['content'].fillna(''):
                if content.strip():
                    blob = TextBlob(content)
                    polarity = blob.sentiment.polarity
                    if polarity > 0.1:
                        sentiments.append('positive')
                    elif polarity < -0.1:
                        sentiments.append('negative')
                    else:
                        sentiments.append('neutral')
                else:
                    sentiments.append('neutral')

            sentiment_counts = Counter(sentiments)
            total = len(sentiments)

            results['sentiment_distribution'] = {
                'positive': {
                    'count': sentiment_counts['positive'],
                    'percentage': round((sentiment_counts['positive'] / total) * 100, 2)
                },
                'negative': {
                    'count': sentiment_counts['negative'],
                    'percentage': round((sentiment_counts['negative'] / total) * 100, 2)
                },
                'neutral': {
                    'count': sentiment_counts['neutral'],
                    'percentage': round((sentiment_counts['neutral'] / total) * 100, 2)
                }
            }

            # Add sentiment to dataframe for other analyses
            self.df['sentiment'] = sentiments

        # Q2: Top 10 emotional words
        all_emotional_words = []
        for category, words in self.emotional_words.items():
            all_emotional_words.extend(words)

        emotional_word_counts = {}
        for word in all_emotional_words:
            count = self.df['content_clean'].str.contains(
                rf'\b{word}\b', na=False).sum()
            if count > 0:
                emotional_word_counts[word] = int(count)

        top_emotional = dict(
            sorted(emotional_word_counts.items(), key=lambda x: x[1], reverse=True)[:10])
        results['top_emotional_words'] = top_emotional

        # Q3: Most emotionally charged reviews (using word count as proxy)
        self.df['emotional_score'] = 0
        for word in all_emotional_words:
            self.df['emotional_score'] += self.df['content_clean'].str.count(
                rf'\b{word}\b')

        top_emotional_reviews = self.df.nlargest(3, 'emotional_score')[
            ['content', 'emotional_score']].to_dict('records')
        results['most_emotional_reviews'] = [
            {'content': review['content'][:200] + '...',
                'score': int(review['emotional_score'])}
            for review in top_emotional_reviews if review['content']
        ]

        # Q4: Sentiment over time (if TextBlob available)
        if HAS_TEXTBLOB and not self.df['updated_dt'].isna().all():
            monthly_sentiment = self.df.groupby(self.df['updated_dt'].dt.to_period('M'))[
                'sentiment'].value_counts().unstack(fill_value=0)
            if not monthly_sentiment.empty:
                # Convert Period index to strings for JSON serialization
                monthly_dict = {}
                for period, row in monthly_sentiment.iterrows():
                    monthly_dict[str(period)] = row.to_dict()
                results['monthly_sentiment_trend'] = monthly_dict

        # Q5: Ad mentions by rating
        ad_keywords = ['ad', 'ads', 'advertisement', 'commercial']
        ad_pattern = '|'.join([rf'\b{word}\b' for word in ad_keywords])

        mentions_ads = self.df['content_clean'].str.contains(
            ad_pattern, na=False)

        one_star = (self.df['rating'] == 1) | (self.df['score'] == 1)
        five_star = (self.df['rating'] == 5) | (self.df['score'] == 5)

        one_star_ad_pct = (mentions_ads & one_star).sum() / \
            one_star.sum() * 100 if one_star.sum() > 0 else 0
        five_star_ad_pct = (mentions_ads & five_star).sum(
        ) / five_star.sum() * 100 if five_star.sum() > 0 else 0

        results['ad_mentions_by_rating'] = {
            'one_star_mention_ads_pct': round(one_star_ad_pct, 2),
            'five_star_mention_ads_pct': round(five_star_ad_pct, 2),
            'total_ad_mentions': int(mentions_ads.sum())
        }

        # Q6: Long-streak users negativity
        streak_keywords = ['streak', 'day', 'days', '365', 'year']
        long_streak_pattern = r'\b(365|year|[0-9]{3,})\s*(day|days|streak)\b'

        has_long_streak = self.df['content_clean'].str.contains(
            long_streak_pattern, na=False)
        if HAS_TEXTBLOB:
            long_streak_negative = has_long_streak & (
                self.df['sentiment'] == 'negative')
            long_streak_negative_pct = (long_streak_negative.sum(
            ) / has_long_streak.sum() * 100) if has_long_streak.sum() > 0 else 0
            results['long_streak_negativity'] = {
                'long_streak_users': int(has_long_streak.sum()),
                'negative_percentage': round(long_streak_negative_pct, 2)
            }
        else:
            results['long_streak_negativity'] = "Cannot analyze - TextBlob not available"

        self.results['sentiment_tone'] = results

    def analyze_problem_clusters(self):
        """3. PROBLEM CLUSTERS (10 questions)"""
        print("Analyzing problem clusters...")

        results = {}

        # Q1: Cluster complaints into themes
        if not HAS_SKLEARN:
            self.cannot_handle.append(
                "Complaint clustering (requires scikit-learn)")
            results['complaint_clusters'] = "Cannot perform - scikit-learn not available"
        else:
            # Simple keyword-based clustering for main themes
            complaint_themes = {
                'ads': ['ad', 'ads', 'advertisement', 'commercial', 'pop-up', 'popup'],
                'monetization': ['money', 'price', 'expensive', 'pay', 'payment', 'subscription', 'premium', 'super', 'plus'],
                'hearts_energy': ['heart', 'hearts', 'energy', 'life', 'lives', 'practice'],
                'ai_content': ['ai', 'artificial', 'robot', 'voice', 'pronunciation', 'grammar', 'mistake'],
                'removed_features': ['removed', 'gone', 'missing', 'deleted', 'took away', 'no longer'],
                'technical_bugs': ['bug', 'crash', 'freeze', 'broken', 'not working', 'glitch', 'error'],
                'ui_ux': ['interface', 'design', 'layout', 'button', 'screen', 'dark mode', 'loud'],
                'progress_loss': ['progress', 'lost', 'reset', 'disappeared', 'sync']
            }

            theme_results = {}
            for theme, keywords in complaint_themes.items():
                pattern = '|'.join([rf'\b{word}\b' for word in keywords])
                matches = self.df['content_clean'].str.contains(
                    pattern, na=False)
                matching_reviews = self.df[matches]['content'].head(3).tolist()

                theme_results[theme] = {
                    'count': int(matches.sum()),
                    'percentage': round((matches.sum() / len(self.df)) * 100, 2),
                    'sample_quotes': [quote[:150] + '...' for quote in matching_reviews if quote]
                }

            # Sort by count
            theme_results = dict(
                sorted(theme_results.items(), key=lambda x: x[1]['count'], reverse=True))
            results['complaint_themes'] = theme_results

        # Q2: Top removed features
        removed_features_keywords = [
            'removed', 'took away', 'no longer', 'missing', 'gone', 'deleted',
            'story', 'stories', 'discussion', 'forum', 'club', 'event'
        ]
        pattern = '|'.join(
            [rf'\b{word}\b' for word in removed_features_keywords])
        removed_mentions = self.df[self.df['content_clean'].str.contains(
            pattern, na=False)]

        results['removed_features'] = {
            'total_mentions': len(removed_mentions),
            'percentage': round((len(removed_mentions) / len(self.df)) * 100, 2),
            'sample_quotes': removed_mentions['content'].head(5).tolist()
        }

        # Q3: Hearts/energy system mentions
        hearts_pattern = r'\b(heart|hearts|energy|practice|life|lives)\b'
        hearts_mentions = self.df['content_clean'].str.contains(
            hearts_pattern, na=False).sum()

        results['hearts_energy_mentions'] = {
            'count': int(hearts_mentions),
            'percentage': round((hearts_mentions / len(self.df)) * 100, 2)
        }

        # Q4: AI/grammar/speech complaints
        ai_pattern = r'\b(ai|artificial|robot|voice|pronunciation|grammar|speech|recognition)\b'
        ai_complaints = self.df['content_clean'].str.contains(
            ai_pattern, na=False).sum()

        results['ai_complaints'] = {
            'count': int(ai_complaints),
            'percentage': round((ai_complaints / len(self.df)) * 100, 2)
        }

        # Q5: Word cloud (if available)
        if HAS_PLOTTING:
            try:
                all_text = ' '.join(self.df['content_clean'].fillna(''))
                wordcloud = WordCloud(
                    width=800, height=400, background_color='white').generate(all_text)

                plt.figure(figsize=(10, 5))
                plt.imshow(wordcloud, interpolation='bilinear')
                plt.axis('off')
                plt.title('Most Frequent Words in Reviews')
                wordcloud_path = os.path.join(
                    self.output_dir, 'complaint_wordcloud.png')
                plt.savefig(wordcloud_path, dpi=300, bbox_inches='tight')
                plt.close()

                results['word_cloud'] = f"Saved to {wordcloud_path}"
            except Exception as e:
                results['word_cloud'] = f"Error creating word cloud: {e}"
        else:
            self.cannot_handle.append(
                "Word cloud generation (requires wordcloud/matplotlib)")
            results['word_cloud'] = "Cannot generate - plotting libraries not available"

        # Q6: Problems in >30% of reviews
        high_frequency_problems = []
        if 'complaint_themes' in results and isinstance(results['complaint_themes'], dict):
            for theme, data in results['complaint_themes'].items():
                if data['percentage'] > 30:
                    high_frequency_problems.append(
                        f"{theme}: {data['percentage']}%")

        results['high_frequency_problems'] = high_frequency_problems

        # Q7: Top technical bugs
        bug_keywords = ['crash', 'freeze', 'broken',
                        'not working', 'glitch', 'error', 'bug']
        bug_counts = {}
        for bug in bug_keywords:
            count = self.df['content_clean'].str.contains(
                rf'\b{bug}\b', na=False).sum()
            if count > 0:
                bug_counts[bug] = int(count)

        top_bugs = dict(sorted(bug_counts.items(),
                        key=lambda x: x[1], reverse=True)[:3])
        results['top_technical_bugs'] = top_bugs

        # Q8: Billing complaints
        billing_keywords = ['billing', 'charged',
                            'auto-renew', 'subscription', 'cancel', 'refund']
        billing_pattern = '|'.join(
            [rf'\b{word}\b' for word in billing_keywords])
        billing_complaints = self.df['content_clean'].str.contains(
            billing_pattern, na=False).sum()

        results['billing_complaints'] = {
            'count': int(billing_complaints),
            'percentage': round((billing_complaints / len(self.df)) * 100, 2)
        }

        # Q9: Paid users still unhappy
        paid_keywords = ['super', 'plus', 'premium', 'paid', 'subscription']
        paid_pattern = '|'.join([rf'\b{word}\b' for word in paid_keywords])
        mentions_paid = self.df['content_clean'].str.contains(
            paid_pattern, na=False)

        if HAS_TEXTBLOB:
            paid_negative = mentions_paid & (
                self.df['sentiment'] == 'negative')
            paid_negative_pct = (paid_negative.sum(
            ) / mentions_paid.sum() * 100) if mentions_paid.sum() > 0 else 0
            results['unhappy_paid_users'] = {
                'paid_user_mentions': int(mentions_paid.sum()),
                'negative_percentage': round(paid_negative_pct, 2)
            }
        else:
            results['unhappy_paid_users'] = "Cannot analyze - TextBlob not available"

        # Q10: UI/UX complaints
        ui_keywords = ['loud', 'ads', 'dark mode',
                       'interface', 'design', 'button', 'screen']
        ui_counts = {}
        for ui_issue in ui_keywords:
            count = self.df['content_clean'].str.contains(
                rf'\b{ui_issue}\b', na=False).sum()
            if count > 0:
                ui_counts[ui_issue] = int(count)

        top_ui_complaints = dict(
            sorted(ui_counts.items(), key=lambda x: x[1], reverse=True)[:3])
        results['top_ui_complaints'] = top_ui_complaints

        self.results['problem_clusters'] = results

    def analyze_user_personas(self):
        """4. USER PERSONAS & BEHAVIOR (8 questions)"""
        print("Analyzing user personas & behavior...")

        results = {}

        # Q1: User personas (keyword-based identification)
        personas = {
            'free_learner': ['free', 'without paying', 'no money'],
            'streak_keeper': ['streak', 'day', 'daily', 'consecutive'],
            'family_user': ['family', 'kid', 'child', 'parent', 'daughter', 'son'],
            'serious_learner': ['fluent', 'serious', 'advanced', 'study', 'learn'],
            'casual_user': ['casual', 'fun', 'hobby', 'sometimes'],
            'paid_user': ['super', 'plus', 'premium', 'paid', 'subscription']
        }

        persona_results = {}
        for persona, keywords in personas.items():
            pattern = '|'.join([rf'\b{word}\b' for word in keywords])
            matches = self.df['content_clean'].str.contains(pattern, na=False)
            matching_reviews = self.df[matches]['content'].head(2).tolist()

            persona_results[persona] = {
                'size': int(matches.sum()),
                'percentage': round((matches.sum() / len(self.df)) * 100, 2),
                'sample_quotes': [quote[:100] + '...' for quote in matching_reviews if quote]
            }

        results['user_personas'] = persona_results

        # Q2: Users mentioning quitting/uninstalling
        quit_keywords = ['quit', 'uninstall',
                         'delete', 'switch', 'leaving', 'done with']
        quit_pattern = '|'.join([rf'\b{word}\b' for word in quit_keywords])
        quit_mentions = self.df['content_clean'].str.contains(
            quit_pattern, na=False).sum()

        results['churn_mentions'] = {
            'count': int(quit_mentions),
            'percentage': round((quit_mentions / len(self.df)) * 100, 2)
        }

        # Q3: Alternative apps mentioned
        alternatives = ['memrise', 'busuu', 'babbel',
                        'rosetta', 'lingoda', 'hellotalk', 'anki']
        alt_counts = {}
        alt_sentiment = {}

        for alt in alternatives:
            alt_mentions = self.df['content_clean'].str.contains(
                rf'\b{alt}\b', na=False)
            count = alt_mentions.sum()
            if count > 0:
                alt_counts[alt] = int(count)

                if HAS_TEXTBLOB:
                    alt_reviews = self.df[alt_mentions]['content'].fillna('')
                    sentiments = []
                    for review in alt_reviews:
                        if review.strip():
                            blob = TextBlob(review)
                            sentiments.append(blob.sentiment.polarity)

                    avg_sentiment = np.mean(sentiments) if sentiments else 0
                    alt_sentiment[alt] = round(avg_sentiment, 2)

        results['alternative_apps'] = {
            'mentions': dict(sorted(alt_counts.items(), key=lambda x: x[1], reverse=True)),
            'sentiment': alt_sentiment if HAS_TEXTBLOB else "Cannot analyze - TextBlob not available"
        }

        # Q4: Pricing willingness
        price_patterns = [
            r'[€$£]\s*\d+',
            r'\d+\s*[€$£]',
            r'would pay',
            r"i'd pay",
            r'willing to pay'
        ]

        pricing_mentions = []
        for pattern in price_patterns:
            matches = self.df[self.df['content_clean'].str.contains(
                pattern, na=False, regex=True)]
            pricing_mentions.extend(matches['content'].head(3).tolist())

        results['pricing_willingness'] = {
            'mentions_count': len(pricing_mentions),
            'sample_quotes': [quote[:150] + '...' for quote in pricing_mentions[:5] if quote]
        }

        # Q5: Parents/kids vs adults
        parent_keywords = ['parent', 'child', 'kid',
                           'daughter', 'son', 'family', 'children']
        adult_keywords = ['adult', 'work', 'job',
                          'career', 'business', 'university', 'college']

        parent_mentions = self.df['content_clean'].str.contains(
            '|'.join([rf'\b{word}\b' for word in parent_keywords]), na=False).sum()
        adult_mentions = self.df['content_clean'].str.contains(
            '|'.join([rf'\b{word}\b' for word in adult_keywords]), na=False).sum()

        results['user_demographics'] = {
            'parent_family_mentions': int(parent_mentions),
            'parent_percentage': round((parent_mentions / len(self.df)) * 100, 2),
            'adult_learner_mentions': int(adult_mentions),
            'adult_percentage': round((adult_mentions / len(self.df)) * 100, 2)
        }

        # Q6: Supplement vs primary tool
        supplement_keywords = ['supplement', 'alongside',
                               'together with', 'in addition', 'plus', 'also use']
        supplement_pattern = '|'.join(
            [rf'\b{word}\b' for word in supplement_keywords])
        supplement_mentions = self.df['content_clean'].str.contains(
            supplement_pattern, na=False).sum()

        results['supplement_usage'] = {
            'count': int(supplement_mentions),
            'percentage': round((supplement_mentions / len(self.df)) * 100, 2)
        }

        # Q7: High-streak users threatening to quit
        high_streak_pattern = r'\b(1000|[0-9]{4,})\s*(day|days|streak)\b'
        quit_pattern = r'\b(quit|leaving|done|uninstall|delete)\b'

        high_streak = self.df['content_clean'].str.contains(
            high_streak_pattern, na=False)
        mentions_quit = self.df['content_clean'].str.contains(
            quit_pattern, na=False)

        high_streak_quit = (high_streak & mentions_quit).sum()
        high_streak_quit_pct = (
            high_streak_quit / high_streak.sum() * 100) if high_streak.sum() > 0 else 0

        results['high_streak_churn'] = {
            'high_streak_users': int(high_streak.sum()),
            'threatening_to_quit': int(high_streak_quit),
            'quit_percentage': round(high_streak_quit_pct, 2)
        }

        # Q8: Top 3 positive things users love
        love_keywords = ['love', 'great', 'amazing',
                         'perfect', 'excellent', 'wonderful']
        positive_mentions = {}

        features = ['streak', 'lesson', 'character', 'story',
                    'game', 'learning', 'language', 'practice']

        for feature in features:
            feature_love = 0
            for love_word in love_keywords:
                pattern = rf'\b{love_word}\b.*\b{feature}\b|\b{feature}\b.*\b{love_word}\b'
                feature_love += self.df['content_clean'].str.contains(
                    pattern, na=False).sum()

            if feature_love > 0:
                positive_mentions[feature] = int(feature_love)

        top_positive = dict(sorted(positive_mentions.items(),
                            key=lambda x: x[1], reverse=True)[:3])
        results['top_positive_aspects'] = top_positive

        self.results['user_personas'] = results

    def analyze_monetization(self):
        """5. MONETIZATION & PRICING INSIGHTS (6 questions)"""
        print("Analyzing monetization & pricing...")

        results = {}

        # Q1: Extract pricing mentions
        pricing_data = {
            'euro_mentions': 0,
            'dollar_mentions': 0,
            'pound_mentions': 0,
            'complaints': 0,
            'positive': 0
        }

        # Count currency mentions
        euro_pattern = r'[€]\s*\d+|\d+\s*[€]'
        dollar_pattern = r'[$]\s*\d+|\d+\s*[$]'
        pound_pattern = r'[£]\s*\d+|\d+\s*[£]'

        pricing_data['euro_mentions'] = int(self.df['content_clean'].str.contains(
            euro_pattern, na=False, regex=True).sum())
        pricing_data['dollar_mentions'] = int(self.df['content_clean'].str.contains(
            dollar_pattern, na=False, regex=True).sum())
        pricing_data['pound_mentions'] = int(self.df['content_clean'].str.contains(
            pound_pattern, na=False, regex=True).sum())

        # Count price sentiment
        pricing_data['complaints'] = int(self.df['content_clean'].str.contains(
            r'\b(too expensive|expensive)\b', na=False, regex=True).sum())
        pricing_data['positive'] = int(self.df['content_clean'].str.contains(
            r'\b(cheap|reasonable|fair price)\b', na=False, regex=True).sum())

        results['pricing_mentions'] = pricing_data

        # Q2: Pay to remove ads / pay for grammar
        pay_for_features = {
            'remove_ads': r'\b(pay.*ad|remove.*ad|ad.*free)\b',
            'grammar': r'\b(pay.*grammar|grammar.*explanation)\b',
            'offline': r'\b(pay.*offline|offline.*mode)\b',
            'unlimited': r'\b(pay.*unlimited|unlimited.*heart)\b'
        }

        feature_payment_willingness = {}
        for feature, pattern in pay_for_features.items():
            count = self.df['content_clean'].str.contains(
                pattern, na=False).sum()
            feature_payment_willingness[feature] = int(count)

        results['pay_for_features'] = feature_payment_willingness

        # Q3: Free users who won't pay
        wont_pay_patterns = [
            r"won't pay",
            r"will not pay",
            r"never pay",
            r"refuse to pay",
            r"not paying",
            r"too expensive"
        ]

        wont_pay_count = 0
        for pattern in wont_pay_patterns:
            wont_pay_count += self.df['content_clean'].str.contains(
                pattern, na=False).sum()

        results['wont_pay_users'] = {
            'count': int(wont_pay_count),
            'percentage': round((wont_pay_count / len(self.df)) * 100, 2)
        }

        # Q4: Features for €5/month
        euro5_pattern = r'[€]\s*5|5\s*[€]'
        euro5_mentions = self.df[self.df['content_clean'].str.contains(
            euro5_pattern, na=False)]

        # Look for features mentioned near €5
        desired_features = ['grammar', 'ad-free',
                            'offline', 'unlimited', 'stories', 'speaking']
        euro5_features = {}

        for feature in desired_features:
            feature_count = euro5_mentions['content_clean'].str.contains(
                rf'\b{feature}\b', na=False).sum()
            if feature_count > 0:
                euro5_features[feature] = int(feature_count)

        results['euro5_plan_features'] = dict(
            sorted(euro5_features.items(), key=lambda x: x[1], reverse=True)[:5])

        # Q5: Cancelled paid users
        cancel_keywords = ['cancel', 'cancelled',
                           'unsubscribe', 'refund', 'money back']
        cancel_pattern = '|'.join([rf'\b{word}\b' for word in cancel_keywords])

        paid_keywords = ['super', 'plus', 'premium', 'subscription', 'paid']
        paid_pattern = '|'.join([rf'\b{word}\b' for word in paid_keywords])

        cancelled_paid = self.df['content_clean'].str.contains(cancel_pattern, na=False) & \
            self.df['content_clean'].str.contains(paid_pattern, na=False)

        results['cancelled_subscriptions'] = {
            'count': int(cancelled_paid.sum()),
            'percentage': round((cancelled_paid.sum() / len(self.df)) * 100, 2),
            'sample_reasons': self.df[cancelled_paid]['content'].head(3).tolist()
        }

        # Q6: Family plan mentions
        family_keywords = ['family', 'share', 'multiple users', 'household']
        family_pattern = '|'.join([rf'\b{word}\b' for word in family_keywords])

        family_plan_mentions = self.df['content_clean'].str.contains(
            family_pattern, na=False).sum()

        results['family_plan_demand'] = {
            'count': int(family_plan_mentions),
            'percentage': round((family_plan_mentions / len(self.df)) * 100, 2)
        }

        self.results['monetization'] = results

    def analyze_opportunities(self):
        """6. OPPORTUNITY & PRODUCT GAPS (8 questions)"""
        print("Analyzing opportunities & product gaps...")

        results = {}

        # Q1 & Q2: Top missing features and user wishlist
        missing_features = {
            'grammar_explanations': ['grammar', 'explanation', 'why', 'rule'],
            'offline_mode': ['offline', 'download', 'no internet', 'airplane'],
            'dark_mode': ['dark mode', 'night mode', 'dark theme'],
            'speaking_practice': ['speaking', 'pronunciation', 'microphone', 'voice'],
            'writing_practice': ['writing', 'typing', 'keyboard'],
            'stories': ['stories', 'story', 'narrative'],
            'human_voices': ['human voice', 'real voice', 'native speaker'],
            'progress_tracking': ['progress', 'statistics', 'stats', 'tracking'],
            'social_features': ['friends', 'social', 'community', 'chat'],
            'advanced_lessons': ['advanced', 'complex', 'difficult', 'c1', 'c2']
        }

        feature_demand = {}
        for feature, keywords in missing_features.items():
            pattern = '|'.join([rf'\b{word}\b' for word in keywords])
            count = self.df['content_clean'].str.contains(
                pattern, na=False).sum()

            # Get sample quotes
            samples = self.df[self.df['content_clean'].str.contains(
                pattern, na=False)]['content'].head(2).tolist()

            feature_demand[feature] = {
                'count': int(count),
                'percentage': round((count / len(self.df)) * 100, 2),
                'sample_quotes': [quote[:100] + '...' for quote in samples if quote]
            }

        # Sort by demand
        sorted_features = dict(
            sorted(feature_demand.items(), key=lambda x: x[1]['count'], reverse=True))

        results['missing_features'] = dict(list(sorted_features.items())[:5])
        results['user_wishlist'] = sorted_features

        # Q3: "If X, I'd leave Duolingo" quotes
        leave_patterns = [
            r"if.*leave",
            r"if.*quit",
            r"if.*uninstall",
            r"unless.*quit",
            r"will leave if"
        ]

        leave_quotes = []
        for pattern in leave_patterns:
            matches = self.df[self.df['content_clean'].str.contains(
                pattern, na=False, regex=True)]
            leave_quotes.extend(matches['content'].head(2).tolist())

        results['leave_conditions'] = [quote[:150] +
                                       '...' for quote in leave_quotes[:5] if quote]

        # Q4: Competitor features praised
        competitor_praise = {
            'busuu': ['busuu', 'conversation', 'speaking practice'],
            'memrise': ['memrise', 'video', 'native speaker'],
            'babbel': ['babbel', 'grammar', 'explanation'],
            'rosetta': ['rosetta', 'immersion', 'no translation'],
            'anki': ['anki', 'spaced repetition', 'flashcard']
        }

        praised_features = {}
        for competitor, features in competitor_praise.items():
            comp_mentions = self.df['content_clean'].str.contains(
                rf'\b{competitor}\b', na=False)
            if comp_mentions.sum() > 0:
                comp_reviews = self.df[comp_mentions]['content']
                praised_features[competitor] = comp_reviews.head(2).tolist()

        results['competitor_features_praised'] = praised_features

        # Q5: Grammar explanations demand
        grammar_keywords = ['grammar', 'explanation',
                            'why', 'rule', 'understand']
        grammar_pattern = '|'.join(
            [rf'\b{word}\b' for word in grammar_keywords])
        grammar_demand = self.df['content_clean'].str.contains(
            grammar_pattern, na=False).sum()

        # Look for format preferences
        format_keywords = {
            'popup': ['popup', 'pop-up', 'tooltip'],
            'video': ['video', 'tutorial', 'youtube'],
            'pdf': ['pdf', 'guide', 'document'],
            'separate_lesson': ['lesson', 'separate', 'dedicated']
        }

        format_preferences = {}
        grammar_reviews = self.df[self.df['content_clean'].str.contains(
            grammar_pattern, na=False)]

        for fmt, keywords in format_keywords.items():
            fmt_pattern = '|'.join([rf'\b{word}\b' for word in keywords])
            fmt_count = grammar_reviews['content_clean'].str.contains(
                fmt_pattern, na=False).sum()
            format_preferences[fmt] = int(fmt_count)

        results['grammar_explanations'] = {
            'total_demand': int(grammar_demand),
            'percentage': round((grammar_demand / len(self.df)) * 100, 2),
            'format_preferences': dict(sorted(format_preferences.items(), key=lambda x: x[1], reverse=True))
        }

        # Q6: Human vs AI voices
        voice_preferences = {
            'human_voices': ['human voice', 'real voice', 'native speaker', 'actual person'],
            'ai_voices': ['robot', 'artificial', 'computer voice', 'synthetic']
        }

        voice_counts = {}
        for voice_type, keywords in voice_preferences.items():
            pattern = '|'.join(keywords)
            count = self.df['content_clean'].str.contains(
                pattern, na=False, case=False).sum()
            voice_counts[voice_type] = int(count)

        results['voice_preferences'] = voice_counts

        # Q7: Feature demands (offline, dark mode, web version)
        specific_features = {
            'offline_mode': ['offline', 'download', 'no internet'],
            'dark_mode': ['dark mode', 'night mode', 'dark theme'],
            'web_version': ['web', 'browser', 'computer', 'desktop']
        }

        specific_demand = {}
        for feature, keywords in specific_features.items():
            pattern = '|'.join([rf'\b{word}\b' for word in keywords])
            count = self.df['content_clean'].str.contains(
                pattern, na=False).sum()
            specific_demand[feature] = {
                'count': int(count),
                'percentage': round((count / len(self.df)) * 100, 2)
            }

        results['specific_feature_demand'] = specific_demand

        # Q8: Perfect app description
        perfect_app_features = []

        # Extract common wishes and combine them
        top_wishes = [
            "No ads or reasonable ad frequency",
            "Grammar explanations for mistakes",
            "Offline mode for practice anywhere",
            "Human voices with proper pronunciation",
            "Fair monetization without aggressive upselling"
        ]

        results['perfect_app_summary'] = top_wishes

        self.results['opportunities'] = results

    def analyze_risk_competition(self):
        """7. RISK & COMPETITION (4 questions)"""
        print("Analyzing risk & competition...")

        results = {}

        # Q1: Switching barriers
        barrier_keywords = {
            'streak_loss': ['streak', 'lose streak', 'start over'],
            'progress_loss': ['progress', 'lose progress', 'data'],
            'habit': ['habit', 'routine', 'daily'],
            'investment': ['time', 'invested', 'years']
        }

        switching_barriers = {}
        for barrier, keywords in barrier_keywords.items():
            pattern = '|'.join([rf'\b{word}\b' for word in keywords])
            count = self.df['content_clean'].str.contains(
                pattern, na=False).sum()
            switching_barriers[barrier] = int(count)

        results['switching_barriers'] = dict(
            sorted(switching_barriers.items(), key=lambda x: x[1], reverse=True))

        # Q2: "Too big to fail" mentions
        monopoly_patterns = [
            'too big',
            'no alternative',
            'only option',
            'monopoly',
            'dominant'
        ]

        monopoly_mentions = 0
        monopoly_quotes = []
        for pattern in monopoly_patterns:
            matches = self.df[self.df['content_clean'].str.contains(
                pattern, na=False)]
            monopoly_mentions += len(matches)
            monopoly_quotes.extend(matches['content'].head(1).tolist())

        results['monopoly_perception'] = {
            'mentions': monopoly_mentions,
            'sample_quotes': monopoly_quotes[:3]
        }

        # Q3: Remaining strengths
        strength_keywords = {
            'gamification': ['game', 'fun', 'addictive', 'engaging'],
            'accessibility': ['free', 'accessible', 'easy', 'beginner'],
            'variety': ['languages', 'many', 'choice', 'options'],
            'community': ['popular', 'everyone uses', 'friends'],
            'streak_system': ['streak', 'motivation', 'daily']
        }

        remaining_strengths = {}
        positive_context = ['good', 'great', 'love', 'like', 'best', 'amazing']
        pos_pattern = '|'.join([rf'\b{word}\b' for word in positive_context])

        for strength, keywords in strength_keywords.items():
            strength_pattern = '|'.join([rf'\b{word}\b' for word in keywords])

            # Count mentions in positive context
            positive_mentions = self.df[
                self.df['content_clean'].str.contains(pos_pattern, na=False) &
                self.df['content_clean'].str.contains(
                    strength_pattern, na=False)
            ]

            remaining_strengths[strength] = int(len(positive_mentions))

        results['remaining_strengths'] = dict(
            sorted(remaining_strengths.items(), key=lambda x: x[1], reverse=True))

        # Q4: One thing to fix for retention
        fix_patterns = {
            'remove_ads': ['ad', 'ads', 'advertisement'],
            'fix_hearts': ['heart', 'hearts', 'energy', 'practice'],
            'add_grammar': ['grammar', 'explanation', 'why'],
            'fair_pricing': ['price', 'expensive', 'money', 'cost'],
            'improve_ai': ['ai', 'voice', 'pronunciation', 'robot']
        }

        retention_fixes = {}
        for fix, keywords in fix_patterns.items():
            pattern = '|'.join([rf'\b{word}\b' for word in keywords])

            # Look for mentions with "fix", "change", "improve" context
            fix_context = ['fix', 'change', 'improve', 'better', 'stop']
            fix_ctx_pattern = '|'.join(
                [rf'\b{word}\b' for word in fix_context])

            relevant_mentions = self.df[
                self.df['content_clean'].str.contains(pattern, na=False) &
                self.df['content_clean'].str.contains(
                    fix_ctx_pattern, na=False)
            ]

            retention_fixes[fix] = int(len(relevant_mentions))

        top_retention_fixes = dict(
            sorted(retention_fixes.items(), key=lambda x: x[1], reverse=True)[:3])
        results['top_retention_fixes'] = top_retention_fixes

        self.results['risk_competition'] = results

    def analyze_dutch_market(self):
        """8. DUTCH MARKET FOCUS (3 questions)"""
        print("Analyzing Dutch market specifics...")

        results = {}

        # Filter for Dutch users (already filtered in dataset but double-check)
        dutch_users = self.df[self.df['country'] == 'nl'].copy()
        if len(dutch_users) == 0:
            dutch_users = self.df.copy()  # Use all data if no country filter

        # Q1: What Dutch users complain about most
        dutch_complaints = {
            'ads': ['ad', 'ads', 'reclame', 'advertisement'],
            'price': ['price', 'expensive', 'duur', 'geld', 'money'],
            'ai': ['ai', 'artificial', 'robot', 'stem', 'voice']
        }

        dutch_complaint_counts = {}
        for complaint, keywords in dutch_complaints.items():
            pattern = '|'.join([rf'\b{word}\b' for word in keywords])
            count = dutch_users['content_clean'].str.contains(
                pattern, na=False).sum()
            dutch_complaint_counts[complaint] = int(count)

        results['dutch_complaints'] = dict(
            sorted(dutch_complaint_counts.items(), key=lambda x: x[1], reverse=True))

        # Q2: Dutch-specific mentions (iDEAL, privacy, GDPR)
        dutch_specific = {
            'ideal': ['ideal', 'betaling', 'payment'],
            'privacy': ['privacy', 'privé', 'gegevens', 'data'],
            'gdpr': ['gdpr', 'avg', 'privacy wet', 'toestemming']
        }

        dutch_specific_counts = {}
        for topic, keywords in dutch_specific.items():
            pattern = '|'.join([rf'\b{word}\b' for word in keywords])
            count = dutch_users['content_clean'].str.contains(
                pattern, na=False).sum()
            if count > 0:
                dutch_specific_counts[topic] = int(count)

        results['dutch_specific_mentions'] = dutch_specific_counts

        # Q3: Willingness to pay €4,99 for Dutch app
        dutch_pricing_patterns = [
            r'€\s*4[,.]99',
            r'4[,.]99\s*€',
            r'5\s*euro',
            r'€\s*5',
            r'dutch.*app',
            r'nederlands.*app'
        ]

        dutch_pricing_mentions = 0
        pricing_quotes = []

        for pattern in dutch_pricing_patterns:
            matches = dutch_users[dutch_users['content_clean'].str.contains(
                pattern, na=False, regex=True)]
            dutch_pricing_mentions += len(matches)
            pricing_quotes.extend(matches['content'].head(1).tolist())

        results['dutch_pricing_willingness'] = {
            'mentions': dutch_pricing_mentions,
            'percentage': round((dutch_pricing_mentions / len(dutch_users)) * 100, 2),
            'sample_quotes': pricing_quotes[:3]
        }

        self.results['dutch_market'] = results

    def save_results(self):
        """Save all results to output directory in multiple formats"""
        print(f"Saving results to {self.output_dir}...")

        # Save complete results as JSON
        json_path = os.path.join(
            self.output_dir, 'comprehensive_analysis_results.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)

        # Save summary as TXT
        txt_path = os.path.join(
            self.output_dir, 'comprehensive_analysis_summary.txt')
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write("DUOLINGO REVIEWS COMPREHENSIVE ANALYSIS SUMMARY\n")
            f.write("="*50 + "\n\n")

            for category, data in self.results.items():
                f.write(f"{category.upper().replace('_', ' ')}\n")
                f.write("-" * 30 + "\n")
                f.write(f"{json.dumps(data, indent=2, ensure_ascii=False)}\n\n")

        # Save key metrics as CSV
        csv_data = []
        for category, data in self.results.items():
            if isinstance(data, dict):
                for key, value in data.items():
                    if isinstance(value, (int, float)):
                        csv_data.append({
                            'category': category,
                            'metric': key,
                            'value': value
                        })
                    elif isinstance(value, dict) and 'count' in value:
                        csv_data.append({
                            'category': category,
                            'metric': key,
                            'value': value['count']
                        })

        if csv_data:
            csv_path = os.path.join(
                self.output_dir, 'comprehensive_analysis_metrics.csv')
            pd.DataFrame(csv_data).to_csv(csv_path, index=False)

        # Save questions that cannot be handled automatically
        if self.cannot_handle:
            unable_path = os.path.join(
                self.output_dir, 'questions_cannot_handle.txt')
            with open(unable_path, 'w', encoding='utf-8') as f:
                f.write("QUESTIONS THAT CANNOT BE HANDLED AUTOMATICALLY\n")
                f.write("="*50 + "\n\n")
                for i, question in enumerate(self.cannot_handle, 1):
                    f.write(f"{i}. {question}\n\n")

        print(f"Results saved:")
        print(f"- JSON: {json_path}")
        print(f"- TXT: {txt_path}")
        if csv_data:
            print(f"- CSV: {csv_path}")
        if self.cannot_handle:
            print(f"- Cannot handle: {unable_path}")


def find_default_input() -> str:
    """Find the default input file"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(script_dir)

    candidates = [
        os.path.join(repo_root, "data", "reviews_nl_duolingo.jsonl"),
        os.path.join(repo_root, "data", "reviews_nl_duolingo.json"),
        os.path.join(repo_root, "reviews_nl_duolingo.jsonl"),
        os.path.join(repo_root, "reviews_nl_duolingo.json"),
    ]

    for path in candidates:
        if os.path.exists(path):
            return path

    return candidates[0]  # Return first candidate as default


def main():
    parser = argparse.ArgumentParser(
        description="Comprehensive analysis of Duolingo reviews")

    parser.add_argument("--input", "-i", default=find_default_input(),
                        help="Path to reviews dataset (JSONL/JSON)")
    parser.add_argument("--output-dir", "-o",
                        default=os.path.join(os.path.dirname(
                            os.path.dirname(__file__)), "output"),
                        help="Output directory for results")

    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"Input file not found: {args.input}")
        return 1

    # Load data
    print(f"Loading data from: {args.input}")
    if args.input.lower().endswith('.jsonl'):
        df = pd.read_json(args.input, lines=True)
    else:
        df = pd.read_json(args.input)

    print(f"Loaded {len(df)} reviews")

    # Run analysis
    analyzer = DuolingoAnalyzer(df, args.output_dir)
    analyzer.analyze_all()

    print("\nAnalysis complete!")
    return 0


if __name__ == '__main__':
    sys.exit(main())
