#!/usr/bin/env python3
"""
Comprehensive analysis script that splits reviews by October 27, 2025 and analyzes each period separately.

This script extends comprehensive_analysis.py to:
1. Split reviews into two periods: Before Oct 27 (426 reviews) and After Oct 27 (74 reviews)
2. Run the same 50+ question analysis on each period
3. Generate separate output files with comparative insights

Usage:
    python scripts/comprehensive_analysis_for_separate_files.py
    
Output:
    output/period_before_oct27/comprehensive_analysis_results.json
    output/period_before_oct27/comprehensive_analysis_summary.txt
    output/period_before_oct27/comprehensive_analysis_metrics.csv
    output/period_after_oct27/comprehensive_analysis_results.json
    output/period_after_oct27/comprehensive_analysis_summary.txt
    output/period_after_oct27/comprehensive_analysis_metrics.csv
"""

import json
import re
import os
from pathlib import Path
from datetime import datetime
from collections import Counter, defaultdict
import csv

try:
    from textblob import TextBlob
    HAS_TEXTBLOB = True
except ImportError:
    HAS_TEXTBLOB = False
    print("Warning: TextBlob not installed. Sentiment analysis will be skipped.")

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.cluster import KMeans
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False
    print("Warning: scikit-learn not installed. Clustering will be skipped.")


class ComprehensiveAnalyzerForPeriods:
    """Analyzes reviews split by date period."""

    def __init__(self, jsonl_path, split_date='2025-10-27'):
        self.jsonl_path = jsonl_path
        self.split_date = datetime.fromisoformat(split_date).date()
        self.df_before = []
        self.df_after = []
        self.load_and_split_data()

    def load_and_split_data(self):
        """Load JSONL and split by date."""
        print(f"Loading data from {self.jsonl_path}...")

        with open(self.jsonl_path, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    review = json.loads(line)
                    date_str = review.get('updated')

                    if date_str:
                        try:
                            dt = datetime.fromisoformat(
                                date_str.replace('Z', '+00:00'))
                            if dt.date() < self.split_date:
                                self.df_before.append(review)
                            else:
                                self.df_after.append(review)
                        except:
                            pass
                except:
                    pass

        print(f"Loaded {len(self.df_before)} reviews before {self.split_date}")
        print(
            f"Loaded {len(self.df_after)} reviews from {self.split_date} onwards")

    def analyze_period(self, reviews, period_name):
        """Run comprehensive analysis on a period's reviews."""
        print(f"\n{'='*60}")
        print(f"Analyzing {period_name}: {len(reviews)} reviews")
        print(f"{'='*60}")

        results = {
            'period': period_name,
            'total_reviews': len(reviews),
            'analysis': {}
        }

        # 1. DATA VALIDATION
        results['analysis']['data_validation'] = self._analyze_data_validation(
            reviews)

        # 2. SENTIMENT & TONE
        results['analysis']['sentiment_tone'] = self._analyze_sentiment_tone(
            reviews)

        # 3. PROBLEM CLUSTERS
        results['analysis']['problem_clusters'] = self._analyze_problem_clusters(
            reviews)

        # 4. USER PERSONAS
        results['analysis']['user_personas'] = self._analyze_user_personas(
            reviews)

        # 5. MONETIZATION
        results['analysis']['monetization'] = self._analyze_monetization(
            reviews)

        # 6. OPPORTUNITIES
        results['analysis']['opportunities'] = self._analyze_opportunities(
            reviews)

        # 7. RISK & COMPETITION
        results['analysis']['risk_competition'] = self._analyze_risk_competition(
            reviews)

        # 8. DUTCH MARKET
        results['analysis']['dutch_market'] = self._analyze_dutch_market(
            reviews)

        return results

    def _analyze_data_validation(self, reviews):
        """Q1-Q5: Data validation questions."""
        ratings = [r.get('rating', 0) for r in reviews if r.get('rating')]
        avg_rating = sum(ratings) / len(ratings) if ratings else 0
        rating_dist = Counter(ratings)

        sources = Counter(r.get('source', 'unknown') for r in reviews)

        return {
            'total_reviews': len(reviews),
            'avg_rating': round(avg_rating, 2),
            'rating_distribution': dict(sorted(rating_dist.items())),
            'sources': dict(sources),
            'date_range': {
                'earliest': min((r.get('updated', '')[:10] for r in reviews if r.get('updated')), default='N/A'),
                'latest': max((r.get('updated', '')[:10] for r in reviews if r.get('updated')), default='N/A'),
            }
        }

    def _analyze_sentiment_tone(self, reviews):
        """Q1-Q6: Sentiment and tone analysis."""
        sentiments = {'Positive': 0, 'Negative': 0, 'Neutral': 0}
        emotional_words = Counter()

        positive_words = ['great', 'love', 'perfect', 'amazing', 'awesome',
                          'excellent', 'best', 'wonderful', 'fantastic', 'brilliant']
        negative_words = ['annoying', 'hate', 'horrible', 'terrible',
                          'worst', 'awful', 'bad', 'poor', 'useless', 'frustrating']

        for review in reviews:
            content = (review.get('title', '') + ' ' +
                       review.get('content', '')).lower()

            if HAS_TEXTBLOB:
                try:
                    blob = TextBlob(content)
                    polarity = blob.sentiment.polarity
                    if polarity > 0.1:
                        sentiments['Positive'] += 1
                    elif polarity < -0.1:
                        sentiments['Negative'] += 1
                    else:
                        sentiments['Neutral'] += 1
                except:
                    sentiments['Neutral'] += 1

            # Track emotional words
            words = re.findall(r'\b\w+\b', content)
            for word in words:
                if word in positive_words or word in negative_words:
                    emotional_words[word] += 1

        return {
            'sentiment_distribution': sentiments,
            'top_emotional_words': dict(emotional_words.most_common(10)),
        }

    def _analyze_problem_clusters(self, reviews):
        """Q1-Q10: Problem cluster identification."""
        themes = {
            'monetization': 0,
            'energy_system': 0,
            'ai_content': 0,
            'ads': 0,
            'removed_features': 0,
            'technical': 0,
            'billing': 0,
            'other': 0
        }

        monetization_patterns = [
            r'premium', r'paywall', r'price', r'expensive', r'pay.*win', r'super duolingo', r'\$\d+', r'€\d+'
        ]
        energy_patterns = [r'energy', r'heart',
                           r'limit.*pract', r'practice.*limit']
        ai_patterns = [r'ai\b', r'robot.*voic',
                       r'grammar', r'speech.*recog', r'pronounc']
        ad_patterns = [r'ad\w*', r'advertis']
        removed_patterns = [r'remove\b', r'disappear\b',
                            r'gone\b', r'streak', r'forum', r'immersion']
        tech_patterns = [r'bug', r'crash', r'freeze', r'error', r'glitch']
        billing_patterns = [r'billing', r'refund',
                            r'cancel.*subscription', r'auto.*renew']

        for review in reviews:
            content = (review.get('title', '') + ' ' +
                       review.get('content', '')).lower()

            found = False
            for pattern in monetization_patterns:
                if re.search(pattern, content):
                    themes['monetization'] += 1
                    found = True
                    break

            if not found:
                for pattern in energy_patterns:
                    if re.search(pattern, content):
                        themes['energy_system'] += 1
                        found = True
                        break

            if not found:
                for pattern in ai_patterns:
                    if re.search(pattern, content):
                        themes['ai_content'] += 1
                        found = True
                        break

            if not found:
                for pattern in ad_patterns:
                    if re.search(pattern, content):
                        themes['ads'] += 1
                        found = True
                        break

            if not found:
                for pattern in removed_patterns:
                    if re.search(pattern, content):
                        themes['removed_features'] += 1
                        found = True
                        break

            if not found:
                for pattern in tech_patterns:
                    if re.search(pattern, content):
                        themes['technical'] += 1
                        found = True
                        break

            if not found:
                for pattern in billing_patterns:
                    if re.search(pattern, content):
                        themes['billing'] += 1
                        found = True
                        break

        # Calculate percentages
        total = len(reviews)
        themes_pct = {k: round((v / total * 100), 1)
                      if total > 0 else 0 for k, v in themes.items()}

        return {
            'complaint_themes': themes,
            'complaint_themes_pct': themes_pct,
            'top_themes': sorted([(k, v) for k, v in themes.items()], key=lambda x: x[1], reverse=True)[:3]
        }

    def _analyze_user_personas(self, reviews):
        """Q1-Q8: User persona identification."""
        personas = {
            'free_learner': 0,
            'streak_keeper': 0,
            'casual_learner': 0,
            'family_user': 0,
            'serious_learner': 0,
            'paid_power_user': 0
        }

        churn_signals = {
            'quit': 0,
            'uninstall': 0,
            'switch_apps': 0,
            'streak_mention': 0
        }

        for review in reviews:
            content = (review.get('title', '') + ' ' +
                       review.get('content', '')).lower()
            rating = review.get('rating', 0)

            # Persona detection
            if re.search(r'premium|super|paid|subscription', content):
                personas['paid_power_user'] += 1
            elif re.search(r'family|kids|children|mom|dad', content):
                personas['family_user'] += 1
            elif re.search(r'streak|day.*row|consecutive', content):
                personas['streak_keeper'] += 1
            elif re.search(r'grammar|level|b1|fluent|serious', content):
                personas['serious_learner'] += 1
            elif re.search(r'nice|okay|decent|alright', content):
                personas['casual_learner'] += 1
            else:
                personas['free_learner'] += 1

            # Churn signals
            if re.search(r'quit|leaving|stop.*using', content):
                churn_signals['quit'] += 1
            if re.search(r'uninstall|delete.*app', content):
                churn_signals['uninstall'] += 1
            if re.search(r'switch|memrise|busuu|babbel|alternative', content):
                churn_signals['switch_apps'] += 1
            if re.search(r'streak', content):
                churn_signals['streak_mention'] += 1

        total_churn = sum(churn_signals.values())
        churn_pct = round((total_churn / len(reviews) * 100),
                          1) if reviews else 0

        return {
            'personas': personas,
            'churn_signals': churn_signals,
            'churn_percentage': churn_pct
        }

    def _analyze_monetization(self, reviews):
        """Q1-Q6: Monetization and pricing analysis."""
        pricing_mentions = {
            'euro': 0,
            'dollar': 0,
            'pound': 0,
            'too_expensive': 0,
            'reasonable_price': 0,
            'pay_to_remove_ads': 0,
            'pay_for_grammar': 0,
            'wont_pay': 0
        }

        for review in reviews:
            content = (review.get('title', '') + ' ' +
                       review.get('content', '')).lower()

            if re.search(r'€', content) or re.search(r'euro', content):
                pricing_mentions['euro'] += 1
            if re.search(r'\$', content) or re.search(r'dollar', content):
                pricing_mentions['dollar'] += 1
            if re.search(r'£', content) or re.search(r'pound', content):
                pricing_mentions['pound'] += 1
            if re.search(r'expensive|too.*much|overpriced', content):
                pricing_mentions['too_expensive'] += 1
            if re.search(r'worth.*price|reasonable|fair.*price', content):
                pricing_mentions['reasonable_price'] += 1
            if re.search(r'pay.*remov.*ad|ad.*free.*paid', content):
                pricing_mentions['pay_to_remove_ads'] += 1
            if re.search(r'pay.*grammar|grammar.*paid', content):
                pricing_mentions['pay_for_grammar'] += 1
            if re.search(r"won't.*pay|not.*pay|never.*pay", content):
                pricing_mentions['wont_pay'] += 1

        # Calculate percentages
        total = len(reviews)
        pricing_pct = {k: round((v / total * 100), 1) if total >
                       0 else 0 for k, v in pricing_mentions.items()}

        return {
            'pricing_mentions': pricing_mentions,
            'pricing_mentions_pct': pricing_pct
        }

    def _analyze_opportunities(self, reviews):
        """Q1-Q8: Feature requests and opportunities."""
        features = {
            'grammar_explanations': 0,
            'offline_mode': 0,
            'dark_mode': 0,
            'speaking_practice': 0,
            'human_voices': 0,
            'web_version': 0,
            'advanced_lessons': 0,
            'streaming_access': 0
        }

        for review in reviews:
            content = (review.get('title', '') + ' ' +
                       review.get('content', '')).lower()

            if re.search(r'grammar|explain.*why', content):
                features['grammar_explanations'] += 1
            if re.search(r'offline|download.*lesson|no.*internet', content):
                features['offline_mode'] += 1
            if re.search(r'dark.*mode|night.*mode|dark.*theme', content):
                features['dark_mode'] += 1
            if re.search(r'speak|pronunciation|oral', content):
                features['speaking_practice'] += 1
            if re.search(r'human.*voice|real.*voice|native.*speaker', content):
                features['human_voices'] += 1
            if re.search(r'web.*version|desktop|computer', content):
                features['web_version'] += 1
            if re.search(r'advanced|level|b1|b2|difficult', content):
                features['advanced_lessons'] += 1
            if re.search(r'stream|watch|video', content):
                features['streaming_access'] += 1

        # Calculate percentages
        total = len(reviews)
        features_pct = {k: round((v / total * 100), 1)
                        if total > 0 else 0 for k, v in features.items()}

        return {
            'feature_requests': features,
            'feature_requests_pct': features_pct,
            'top_features': sorted([(k, v) for k, v in features.items()], key=lambda x: x[1], reverse=True)[:5]
        }

    def _analyze_risk_competition(self, reviews):
        """Q1-Q4: Risk and competitive analysis."""
        risks = {
            'streak_loss': 0,
            'habit_routine': 0,
            'progress_investment': 0,
            'familiarity': 0,
            'friends_competition': 0
        }

        competitors = {
            'memrise': 0,
            'busuu': 0,
            'babbel': 0,
            'rosetta_stone': 0,
            'lingoda': 0
        }

        for review in reviews:
            content = (review.get('title', '') + ' ' +
                       review.get('content', '')).lower()

            if re.search(r'streak', content):
                risks['streak_loss'] += 1
            if re.search(r'habit|routine|daily', content):
                risks['habit_routine'] += 1
            if re.search(r'invested|time.*spent|progress', content):
                risks['progress_investment'] += 1
            if re.search(r'familiar|know.*how|used.*to', content):
                risks['familiarity'] += 1
            if re.search(r'friend|compete|leaderboard', content):
                risks['friends_competition'] += 1

            if re.search(r'memrise', content):
                competitors['memrise'] += 1
            if re.search(r'busuu', content):
                competitors['busuu'] += 1
            if re.search(r'babbel', content):
                competitors['babbel'] += 1
            if re.search(r'rosetta.*stone|rosetta', content):
                competitors['rosetta_stone'] += 1
            if re.search(r'lingoda', content):
                competitors['lingoda'] += 1

        return {
            'switching_barriers': risks,
            'competitors_mentioned': competitors
        }

    def _analyze_dutch_market(self, reviews):
        """Q1-Q3: Dutch market specific analysis."""
        dutch_language = 0
        local_terms = 0
        pricing_4_99 = 0

        dutch_terms = [
            'nederlands', 'holland', 'dutch', 'nl', 'groningen', 'amsterdam', 'rotterdam',
            'alsjeblieft', 'dank', 'graag', 'fijn', 'erg', 'heel', 'gewoon'
        ]

        for review in reviews:
            content = (review.get('title', '') + ' ' +
                       review.get('content', '')).lower()

            if re.search(r'nederlands|dutch|nl\b', content):
                dutch_language += 1

            for term in dutch_terms:
                if term in content:
                    local_terms += 1
                    break

            if re.search(r'€4\.99|4\.99', content):
                pricing_4_99 += 1

        total = len(reviews)
        return {
            'dutch_language_mentions': dutch_language,
            'dutch_language_pct': round((dutch_language / total * 100), 1) if total > 0 else 0,
            'local_terms_mentions': local_terms,
            'pricing_4_99_mentions': pricing_4_99,
            'pricing_4_99_pct': round((pricing_4_99 / total * 100), 1) if total > 0 else 0
        }

    def save_results(self, results, output_dir):
        """Save analysis results to JSON, TXT, and CSV."""
        os.makedirs(output_dir, exist_ok=True)

        # Save JSON
        json_path = os.path.join(
            output_dir, 'comprehensive_analysis_results.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"✓ Saved JSON: {json_path}")

        # Save TXT summary
        txt_path = os.path.join(
            output_dir, 'comprehensive_analysis_summary.txt')
        with open(txt_path, 'w', encoding='utf-8') as f:
            self._write_txt_summary(f, results)
        print(f"✓ Saved TXT: {txt_path}")

        # Save CSV metrics
        csv_path = os.path.join(
            output_dir, 'comprehensive_analysis_metrics.csv')
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            self._write_csv_metrics(f, results)
        print(f"✓ Saved CSV: {csv_path}")

    def _write_txt_summary(self, f, results):
        """Write human-readable text summary."""
        period = results['period']
        total = results['total_reviews']

        f.write(f"COMPREHENSIVE ANALYSIS SUMMARY - {period}\n")
        f.write(f"{'='*70}\n")
        f.write(f"Total Reviews: {total}\n\n")

        # Data Validation
        f.write(f"1. DATA VALIDATION\n")
        dv = results['analysis']['data_validation']
        f.write(f"   Average Rating: {dv['avg_rating']}\n")
        f.write(
            f"   Date Range: {dv['date_range']['earliest']} to {dv['date_range']['latest']}\n")
        f.write(f"   Sources: {dv['sources']}\n\n")

        # Sentiment
        f.write(f"2. SENTIMENT & TONE\n")
        sentiment = results['analysis']['sentiment_tone']
        f.write(f"   Sentiment: {sentiment['sentiment_distribution']}\n")
        f.write(
            f"   Top Emotional Words: {sentiment['top_emotional_words']}\n\n")

        # Problems
        f.write(f"3. PROBLEM CLUSTERS\n")
        problems = results['analysis']['problem_clusters']
        f.write(f"   Themes: {problems['complaint_themes']}\n")
        f.write(f"   Top Themes: {problems['top_themes']}\n\n")

        # Personas
        f.write(f"4. USER PERSONAS\n")
        personas = results['analysis']['user_personas']
        f.write(f"   Personas: {personas['personas']}\n")
        f.write(f"   Churn Signals: {personas['churn_signals']}\n")
        f.write(f"   Churn %: {personas['churn_percentage']}%\n\n")

        # Monetization
        f.write(f"5. MONETIZATION\n")
        monetization = results['analysis']['monetization']
        f.write(f"   Pricing Mentions: {monetization['pricing_mentions']}\n\n")

        # Opportunities
        f.write(f"6. OPPORTUNITIES\n")
        opps = results['analysis']['opportunities']
        f.write(f"   Top Features: {opps['top_features']}\n\n")

        # Risk
        f.write(f"7. RISK & COMPETITION\n")
        risk = results['analysis']['risk_competition']
        f.write(f"   Switching Barriers: {risk['switching_barriers']}\n")
        f.write(f"   Competitors: {risk['competitors_mentioned']}\n\n")

        # Dutch Market
        f.write(f"8. DUTCH MARKET\n")
        dutch = results['analysis']['dutch_market']
        f.write(
            f"   Dutch Language Mentions: {dutch['dutch_language_mentions']} ({dutch['dutch_language_pct']}%)\n")
        f.write(f"   Local Terms: {dutch['local_terms_mentions']}\n")
        f.write(
            f"   €4.99 Pricing: {dutch['pricing_4_99_mentions']} ({dutch['pricing_4_99_pct']}%)\n")

    def _write_csv_metrics(self, f, results):
        """Write CSV metrics."""
        writer = csv.writer(f)

        period = results['period']
        total = results['total_reviews']

        # Header
        writer.writerow(['Metric', 'Value'])

        # Basic
        writer.writerow(['Period', period])
        writer.writerow(['Total Reviews', total])

        # Data Validation
        dv = results['analysis']['data_validation']
        writer.writerow(['Average Rating', dv['avg_rating']])

        # Sentiment
        sentiment = results['analysis']['sentiment_tone']
        for sentiment_type, count in sentiment['sentiment_distribution'].items():
            pct = round((count / total * 100), 1) if total > 0 else 0
            writer.writerow(
                [f'{sentiment_type} Sentiment', f'{count} ({pct}%)'])

        # Problems
        problems = results['analysis']['problem_clusters']
        writer.writerow(['', ''])
        writer.writerow(['Complaint Themes', 'Count'])
        for theme, count in sorted(problems['complaint_themes'].items(), key=lambda x: x[1], reverse=True):
            pct = round((count / total * 100), 1) if total > 0 else 0
            writer.writerow(
                [theme.replace('_', ' ').title(), f'{count} ({pct}%)'])

        # Personas
        personas = results['analysis']['user_personas']
        writer.writerow(['', ''])
        writer.writerow(['User Personas', 'Count'])
        for persona, count in sorted(personas['personas'].items(), key=lambda x: x[1], reverse=True):
            pct = round((count / total * 100), 1) if total > 0 else 0
            writer.writerow(
                [persona.replace('_', ' ').title(), f'{count} ({pct}%)'])

        # Feature Requests
        opps = results['analysis']['opportunities']
        writer.writerow(['', ''])
        writer.writerow(['Feature Requests', 'Count'])
        for feature, count in sorted(opps['feature_requests'].items(), key=lambda x: x[1], reverse=True):
            pct = round((count / total * 100), 1) if total > 0 else 0
            writer.writerow(
                [feature.replace('_', ' ').title(), f'{count} ({pct}%)'])


def main():
    """Main execution."""
    input_file = 'data/reviews_nl_duolingo.jsonl'
    output_before = 'output/period_before_oct27'
    output_after = 'output/period_after_oct27'

    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found!")
        return

    # Initialize analyzer
    analyzer = ComprehensiveAnalyzerForPeriods(input_file)

    # Analyze both periods
    results_before = analyzer.analyze_period(
        analyzer.df_before, 'Before Oct 27, 2025 (426 reviews)')
    results_after = analyzer.analyze_period(
        analyzer.df_after, 'From Oct 27, 2025 onwards (74 reviews)')

    # Save results
    print(f"\nSaving results...")
    analyzer.save_results(results_before, output_before)
    analyzer.save_results(results_after, output_after)

    print(f"\n{'='*70}")
    print(f"✓ Analysis complete!")
    print(f"✓ Before Oct 27 results: {output_before}/")
    print(f"✓ After Oct 27 results: {output_after}/")
    print(f"{'='*70}")


if __name__ == '__main__':
    main()
