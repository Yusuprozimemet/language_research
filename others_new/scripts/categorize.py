import json
import os
import pandas as pd
from datetime import datetime
from collections import defaultdict

# Directory setup
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
INPUT_DIR = os.path.join(PROJECT_DIR, "individual")
OUTPUT_DIR = os.path.join(PROJECT_DIR, "output")

os.makedirs(OUTPUT_DIR, exist_ok=True)


def safe_number(value, default=0):
    """Safely convert value to number"""
    if value is None or value == "N/A":
        return default
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        # Handle strings like "1,000,000+" or "500,000,000+"
        cleaned = value.replace(',', '').replace('+', '').replace('>', '')
        try:
            return float(cleaned)
        except ValueError:
            return default
    return default


def extract_app_metrics(app_data):
    """Extract key metrics from app data"""
    name = app_data.get('name', 'Unknown App')
    package = app_data.get('google_package', 'N/A')

    google = app_data.get('google', {})
    apple = app_data.get('apple', {})
    reviews = app_data.get('reviews', [])

    # Google Play metrics
    google_rating = safe_number(google.get('rating'))
    google_ratings_total = safe_number(google.get('ratings_total'))
    google_installs = safe_number(google.get('installs'))

    # Apple App Store metrics
    apple_rating = safe_number(apple.get('rating')) if apple else 0
    apple_ratings_total = safe_number(
        apple.get('ratings_total')) if apple else 0

    # Review analysis
    review_count = len(reviews)
    review_ratings = [r.get('rating') for r in reviews if isinstance(
        r.get('rating'), (int, float))]
    avg_review_rating = sum(review_ratings) / \
        len(review_ratings) if review_ratings else 0

    # Platform presence
    has_google = bool(google)
    has_apple = bool(apple)

    # Genre/category
    genre = google.get('genre', 'Unknown')

    return {
        'name': name,
        'package': package,
        'google_rating': google_rating,
        'google_ratings_total': google_ratings_total,
        'google_installs': google_installs,
        'apple_rating': apple_rating,
        'apple_ratings_total': apple_ratings_total,
        'review_count': review_count,
        'avg_review_rating': avg_review_rating,
        'has_google': has_google,
        'has_apple': has_apple,
        'genre': genre,
        'total_ratings': google_ratings_total + apple_ratings_total,
        'combined_rating': (google_rating + apple_rating) / (int(has_google) + int(has_apple)) if (has_google or has_apple) else 0
    }


def categorize_apps(apps_df):
    """Categorize apps based on performance metrics"""
    categories = {}

    # Calculate percentiles for thresholds
    rating_high = apps_df['combined_rating'].quantile(0.75)
    rating_low = apps_df['combined_rating'].quantile(0.25)

    total_ratings_high = apps_df['total_ratings'].quantile(0.75)
    total_ratings_med = apps_df['total_ratings'].quantile(0.5)

    review_count_high = apps_df['review_count'].quantile(0.75)
    review_count_med = apps_df['review_count'].quantile(0.5)

    # Primary categorization: Good vs Bad apps
    excellent_apps = apps_df[
        (apps_df['combined_rating'] >= 4.0) &
        (apps_df['total_ratings'] >= total_ratings_high)
    ]

    good_apps = apps_df[
        (apps_df['combined_rating'] >= rating_high) &
        (apps_df['combined_rating'] < 4.0) &
        (apps_df['total_ratings'] >= total_ratings_med)
    ]

    popular_but_polarizing = apps_df[
        (apps_df['total_ratings'] >= total_ratings_high) &
        (apps_df['combined_rating'] < rating_high) &
        (apps_df['combined_rating'] >= 3.0)
    ]

    poor_apps = apps_df[
        (apps_df['combined_rating'] < rating_low) |
        ((apps_df['combined_rating'] < 3.0) &
         (apps_df['total_ratings'] < total_ratings_med))
    ]

    niche_apps = apps_df[
        (apps_df['total_ratings'] < total_ratings_med) &
        (apps_df['combined_rating'] >= rating_high)
    ]

    # Apps with lots of collected reviews (high engagement in our dataset)
    highly_reviewed_in_dataset = apps_df[apps_df['review_count']
                                         >= review_count_high]

    categories = {
        'excellent': excellent_apps,
        'good': good_apps,
        'popular_but_polarizing': popular_but_polarizing,
        'poor': poor_apps,
        'niche': niche_apps,
        'highly_reviewed_in_dataset': highly_reviewed_in_dataset
    }

    return categories, {
        'rating_high': rating_high,
        'rating_low': rating_low,
        'total_ratings_high': total_ratings_high,
        'total_ratings_med': total_ratings_med,
        'review_count_high': review_count_high,
        'review_count_med': review_count_med
    }


def generate_categories_md(apps_df, categories, thresholds):
    """Generate comprehensive categories markdown report with full app lists"""

    total_apps = len(apps_df)

    md_content = f"""# 📱 Complete App Categories Analysis Report

*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*

## 📊 Executive Summary

**Total Apps Analyzed:** {total_apps} apps

**Quick Category Breakdown:**
- 🌟 **Excellent Apps**: {len(categories['excellent'])} apps ({(len(categories['excellent'])/total_apps)*100:.1f}%)
- 👍 **Good Apps**: {len(categories['good'])} apps ({(len(categories['good'])/total_apps)*100:.1f}%)
- ⚡ **Popular but Polarizing**: {len(categories['popular_but_polarizing'])} apps ({(len(categories['popular_but_polarizing'])/total_apps)*100:.1f}%)
- 💎 **Niche/Specialized**: {len(categories['niche'])} apps ({(len(categories['niche'])/total_apps)*100:.1f}%)
- 📉 **Poor Performing**: {len(categories['poor'])} apps ({(len(categories['poor'])/total_apps)*100:.1f}%)
- 💬 **Highly Reviewed (Dataset)**: {len(categories['highly_reviewed_in_dataset'])} apps ({(len(categories['highly_reviewed_in_dataset'])/total_apps)*100:.1f}%)

**Analysis Thresholds:**
- High Rating Threshold: {thresholds['rating_high']:.2f}+ stars
- Low Rating Threshold: {thresholds['rating_low']:.2f} stars
- High Total Ratings: {thresholds['total_ratings_high']:,.0f}+ ratings
- Medium Total Ratings: {thresholds['total_ratings_med']:,.0f}+ ratings
- High Review Count (Dataset): {thresholds['review_count_high']:.0f}+ reviews

---

## 🏆 DETAILED CATEGORY ANALYSIS

"""    # Category descriptions and analysis
    category_info = {
        'excellent': {
            'title': '🌟 Excellent Apps',
            'description': 'High ratings (4.0+) AND high user base (top 25% in total ratings)',
            'emoji': '🌟'
        },
        'good': {
            'title': '👍 Good Apps',
            'description': 'Good ratings (top 25%) with decent user base',
            'emoji': '👍'
        },
        'popular_but_polarizing': {
            'title': '⚡ Popular but Polarizing',
            'description': 'High user base but mixed ratings (3.0-3.75)',
            'emoji': '⚡'
        },
        'niche': {
            'title': '💎 Niche/Specialized Apps',
            'description': 'High ratings but smaller user base (specialized audience)',
            'emoji': '💎'
        },
        'poor': {
            'title': '📉 Poor Performing Apps',
            'description': 'Low ratings OR (below 3.0 rating with small user base)',
            'emoji': '📉'
        },
        'highly_reviewed_in_dataset': {
            'title': '💬 Highly Reviewed (Dataset)',
            'description': 'Apps with most reviews in our collected dataset (high engagement)',
            'emoji': '💬'
        }
    }

    # Process each category with comprehensive details
    category_order = ['excellent', 'good', 'popular_but_polarizing',
                      'niche', 'poor', 'highly_reviewed_in_dataset']

    for cat_key in category_order:
        cat_df = categories[cat_key]
        info = category_info[cat_key]
        count = len(cat_df)
        percentage = (count / total_apps) * 100

        md_content += f"### {info['title']} ({count} apps - {percentage:.1f}%)\n\n"
        md_content += f"**Description:** {info['description']}\n\n"

        if cat_df.empty:
            md_content += "*No apps found in this category.*\n\n---\n\n"
            continue

        # Category statistics
        avg_rating = cat_df['combined_rating'].mean()
        avg_total_ratings = cat_df['total_ratings'].mean()
        avg_reviews = cat_df['review_count'].mean()

        md_content += "**📊 Category Statistics:**\n"
        md_content += f"- Average Rating: {avg_rating:.2f}/5.0\n"
        md_content += f"- Average Total Ratings: {avg_total_ratings:,.0f}\n"
        md_content += f"- Average Reviews in Dataset: {avg_reviews:.0f}\n\n"

        # COMPLETE list of ALL apps in this category
        md_content += f"**📋 COMPLETE LIST - ALL {count} APPS:**\n\n"

        # Sort by combined rating (highest first), then by total ratings
        sorted_apps = cat_df.sort_values(
            ['combined_rating', 'total_ratings'], ascending=[False, False])

        md_content += "| # | App Name | Rating | Google Ratings | Apple Ratings | Reviews (Dataset) | Genre | Package |\n"
        md_content += "|---|----------|--------|----------------|---------------|-------------------|-------|----------|\n"

        for i, (_, app) in enumerate(sorted_apps.iterrows(), 1):
            name = app['name']
            rating = f"{app['combined_rating']:.2f}" if app['combined_rating'] > 0 else "N/A"
            google_ratings = f"{app['google_ratings_total']:,.0f}" if app['google_ratings_total'] > 0 else "N/A"
            apple_ratings = f"{app['apple_ratings_total']:,.0f}" if app['apple_ratings_total'] > 0 else "N/A"
            review_count = f"{app['review_count']:.0f}"
            genre = app['genre'][:15] + \
                "..." if len(app['genre']) > 15 else app['genre']
            package = app['package'][:25] + \
                "..." if len(app['package']) > 25 else app['package']

            md_content += f"| {i} | {name} | {rating} | {google_ratings} | {apple_ratings} | {review_count} | {genre} | {package} |\n"

        md_content += "\n"

        # Top 3 performers in this category
        top_3 = sorted_apps.head(3)
        if len(top_3) > 0:
            md_content += f"**🏆 Top 3 in this category:**\n"
            for i, (_, app) in enumerate(top_3.iterrows(), 1):
                medal = ["🥇", "🥈", "🥉"][i-1]
                total_ratings_text = f"({app['total_ratings']:,.0f} total ratings)" if app[
                    'total_ratings'] > 0 else "(no ratings data)"
                md_content += f"{medal} **{app['name']}** - {app['combined_rating']:.2f}★ {total_ratings_text}\n"
            md_content += "\n"

        md_content += "---\n\n"

    # Overall statistics and insights
    md_content += "## 📈 Overall Statistics\n\n"

    # Genre distribution
    genre_dist = apps_df['genre'].value_counts().head(10)
    md_content += "### Top Genres\n\n"
    for genre, count in genre_dist.items():
        percentage = (count / total_apps) * 100
        md_content += f"- **{genre}**: {count} apps ({percentage:.1f}%)\n"

    md_content += "\n### Platform Distribution\n\n"
    google_only = len(apps_df[(apps_df['has_google'])
                      & (~apps_df['has_apple'])])
    apple_only = len(
        apps_df[(~apps_df['has_google']) & (apps_df['has_apple'])])
    both_platforms = len(
        apps_df[(apps_df['has_google']) & (apps_df['has_apple'])])

    md_content += f"- **Google Play Only**: {google_only} apps ({(google_only/total_apps)*100:.1f}%)\n"
    md_content += f"- **App Store Only**: {apple_only} apps ({(apple_only/total_apps)*100:.1f}%)\n"
    md_content += f"- **Both Platforms**: {both_platforms} apps ({(both_platforms/total_apps)*100:.1f}%)\n\n"

    # Top performers overall
    md_content += "## 🏅 Top Performers Overall\n\n"

    md_content += "### 🌟 Highest Rated Apps\n\n"
    top_rated = apps_df.nlargest(10, 'combined_rating')[
        ['name', 'combined_rating', 'total_ratings', 'genre']]
    md_content += "| Rank | App Name | Rating | Total Ratings | Genre |\n"
    md_content += "|------|----------|--------|---------------|-------|\n"

    for i, (_, app) in enumerate(top_rated.iterrows(), 1):
        name = app['name'][:35] + \
            "..." if len(app['name']) > 35 else app['name']
        rating = f"{app['combined_rating']:.2f}"
        total_ratings = f"{app['total_ratings']:,.0f}" if app['total_ratings'] > 0 else "N/A"
        genre = app['genre']
        md_content += f"| {i} | {name} | {rating} | {total_ratings} | {genre} |\n"

    md_content += "\n### 📊 Most Popular Apps (by Total Ratings)\n\n"
    most_popular = apps_df.nlargest(10, 'total_ratings')[
        ['name', 'combined_rating', 'total_ratings', 'genre']]
    md_content += "| Rank | App Name | Rating | Total Ratings | Genre |\n"
    md_content += "|------|----------|--------|---------------|-------|\n"

    for i, (_, app) in enumerate(most_popular.iterrows(), 1):
        name = app['name'][:35] + \
            "..." if len(app['name']) > 35 else app['name']
        rating = f"{app['combined_rating']:.2f}" if app['combined_rating'] > 0 else "N/A"
        total_ratings = f"{app['total_ratings']:,.0f}"
        genre = app['genre']
        md_content += f"| {i} | {name} | {rating} | {total_ratings} | {genre} |\n"

    md_content += "\n### 💬 Most Reviewed in Dataset\n\n"
    most_reviewed = apps_df.nlargest(10, 'review_count')[
        ['name', 'combined_rating', 'review_count', 'genre']]
    md_content += "| Rank | App Name | Rating | Reviews Collected | Genre |\n"
    md_content += "|------|----------|--------|--------------------|-------|\n"

    for i, (_, app) in enumerate(most_reviewed.iterrows(), 1):
        name = app['name'][:35] + \
            "..." if len(app['name']) > 35 else app['name']
        rating = f"{app['combined_rating']:.2f}" if app['combined_rating'] > 0 else "N/A"
        review_count = f"{app['review_count']:.0f}"
        genre = app['genre']
        md_content += f"| {i} | {name} | {rating} | {review_count} | {genre} |\n"

    # Add category overlap analysis
    md_content += "## 📊 CATEGORY OVERLAP ANALYSIS\n\n"

    # Find apps that appear in multiple categories
    all_app_names = set(apps_df['name'])
    category_memberships = {}

    for app_name in all_app_names:
        memberships = []
        for cat_name, cat_df in categories.items():
            if app_name in cat_df['name'].values:
                memberships.append(cat_name)
        category_memberships[app_name] = memberships

    # Apps in multiple categories
    multi_category_apps = {name: cats for name,
                           cats in category_memberships.items() if len(cats) > 1}

    if multi_category_apps:
        md_content += f"**🔄 Apps appearing in multiple categories ({len(multi_category_apps)} apps):**\n\n"
        for app_name, cats in sorted(multi_category_apps.items()):
            cat_names = ", ".join(
                [cat.replace('_', ' ').title() for cat in cats])
            md_content += f"- **{app_name}**: {cat_names}\n"
        md_content += "\n"

    # Apps in no primary categories (excellent, good, poor)
    primary_categories = ['excellent', 'good', 'poor']
    apps_in_primary = set()
    for cat in primary_categories:
        apps_in_primary.update(categories[cat]['name'].values)

    apps_not_in_primary = all_app_names - apps_in_primary
    if apps_not_in_primary:
        md_content += f"**🔍 Apps not in primary categories ({len(apps_not_in_primary)} apps):**\n"
        md_content += "*(These are in niche, polarizing, or highly-reviewed categories only)*\n\n"
        for app_name in sorted(apps_not_in_primary):
            cats = [cat.replace('_', ' ').title()
                    for cat in category_memberships.get(app_name, [])]
            md_content += f"- **{app_name}**: {', '.join(cats) if cats else 'No categories'}\n"
        md_content += "\n"

    # Comprehensive summary insights
    md_content += f"""## 🔍 COMPREHENSIVE KEY INSIGHTS

### 📈 Good vs Bad Apps Summary:
- **🌟 Excellent Apps**: {len(categories['excellent'])} apps ({(len(categories['excellent'])/total_apps)*100:.1f}%) - **TOP PERFORMERS**
- **👍 Good Apps**: {len(categories['good'])} apps ({(len(categories['good'])/total_apps)*100:.1f}%) - **SOLID PERFORMERS**
- **📉 Poor Apps**: {len(categories['poor'])} apps ({(len(categories['poor'])/total_apps)*100:.1f}%) - **NEED IMPROVEMENT**

### 🎯 Market Health Analysis:
- **✅ Success Rate**: {((len(categories['excellent']) + len(categories['good']))/total_apps)*100:.1f}% of apps are performing well (Excellent + Good)
- **⚠️ Risk Category**: {(len(categories['poor'])/total_apps)*100:.1f}% of apps are underperforming
- **🔄 Mixed Performers**: {(len(categories['popular_but_polarizing']) + len(categories['niche']))/total_apps*100:.1f}% are niche or polarizing

### 📊 Dataset Insights:
- **Most reviews collected**: {apps_df['review_count'].max():.0f} reviews (single app)
- **Average reviews per app**: {apps_df['review_count'].mean():.1f} reviews
- **Apps with 0 reviews in dataset**: {len(apps_df[apps_df['review_count'] == 0])} apps
- **Apps with 100+ reviews**: {len(apps_df[apps_df['review_count'] >= 100])} apps

### 🏪 Platform Distribution:
- **Google Play Only**: {len(apps_df[(apps_df['has_google']) & (~apps_df['has_apple'])])} apps
- **App Store Only**: {len(apps_df[(~apps_df['has_google']) & (apps_df['has_apple'])])} apps  
- **Both Platforms**: {len(apps_df[(apps_df['has_google']) & (apps_df['has_apple'])])} apps

### 🎮 Genre Breakdown:
{chr(10).join([f"- **{genre}**: {count} apps ({count/total_apps*100:.1f}%)" for genre, count in apps_df['genre'].value_counts().head(8).items()])}

### 🔢 Rating Distribution:
- **4.0+ stars**: {len(apps_df[apps_df['combined_rating'] >= 4.0])} apps ({len(apps_df[apps_df['combined_rating'] >= 4.0])/total_apps*100:.1f}%)
- **3.0-3.9 stars**: {len(apps_df[(apps_df['combined_rating'] >= 3.0) & (apps_df['combined_rating'] < 4.0)])} apps ({len(apps_df[(apps_df['combined_rating'] >= 3.0) & (apps_df['combined_rating'] < 4.0)])/total_apps*100:.1f}%)
- **Below 3.0 stars**: {len(apps_df[apps_df['combined_rating'] < 3.0])} apps ({len(apps_df[apps_df['combined_rating'] < 3.0])/total_apps*100:.1f}%)
- **No rating data**: {len(apps_df[apps_df['combined_rating'] == 0])} apps ({len(apps_df[apps_df['combined_rating'] == 0])/total_apps*100:.1f}%)

### 📱 Download Scale:
- **1M+ installs**: {len(apps_df[apps_df['google_installs'] >= 1000000])} apps
- **100K+ installs**: {len(apps_df[apps_df['google_installs'] >= 100000])} apps  
- **10K+ installs**: {len(apps_df[apps_df['google_installs'] >= 10000])} apps

---

## 🎯 ACTIONABLE RECOMMENDATIONS

### For App Developers:
1. **Study Excellent Apps** ({len(categories['excellent'])} apps) - Analyze what makes them successful
2. **Avoid Poor App Patterns** ({len(categories['poor'])} apps) - Learn from their mistakes
3. **Target Niche Markets** ({len(categories['niche'])} apps show high ratings are possible with smaller audiences)

### For Users/Researchers:
1. **Best Apps to Use**: Focus on the {len(categories['excellent'])} Excellent apps for quality experience
2. **Apps to Avoid**: Be cautious with the {len(categories['poor'])} Poor performing apps
3. **Hidden Gems**: Check the {len(categories['niche'])} Niche apps for specialized needs

### For Market Analysis:
1. **Market is {((len(categories['excellent']) + len(categories['good']))/total_apps)*100:.0f}% healthy** with good/excellent apps
2. **{(len(categories['poor'])/total_apps)*100:.0f}% failure rate** indicates competitive market
3. **Opportunity exists** in underserved niches

---
*This comprehensive analysis covers all {total_apps} language learning and education apps in the dataset, categorized by performance metrics including ratings, user base size, and review engagement.*
"""

    return md_content


def main():
    """Main function to analyze and categorize apps"""
    print("🚀 Starting app categorization analysis...")

    # Get all JSON files
    files = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith(
        '.jsonl') or f.lower().endswith('.json')]
    if not files:
        print(f"❌ No JSON files found in {INPUT_DIR}")
        return

    print(f"📚 Found {len(files)} app files to analyze...")

    # Process all apps
    all_apps = []
    processed = 0

    for fname in files:
        file_path = os.path.join(INPUT_DIR, fname)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                app_data = json.load(f)

            metrics = extract_app_metrics(app_data)
            all_apps.append(metrics)
            processed += 1

        except Exception as e:
            print(f"⚠️  Error processing {fname}: {e}")

    print(f"✅ Successfully processed {processed} apps")

    # Create DataFrame for analysis
    apps_df = pd.DataFrame(all_apps)
    print(f"📊 DataFrame created with {len(apps_df)} apps")

    # Categorize apps
    categories, thresholds = categorize_apps(apps_df)

    # Generate report
    print("📝 Generating categories report...")
    md_content = generate_categories_md(apps_df, categories, thresholds)

    # Save report
    output_path = os.path.join(OUTPUT_DIR, 'categories.md')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(md_content)

    print(f"✅ Categories report saved to: {output_path}")

    # Print summary to console
    print(f"\n📊 SUMMARY:")
    print(f"   Total Apps: {len(apps_df)}")
    for cat_name, cat_df in categories.items():
        count = len(cat_df)
        percentage = (count / len(apps_df)) * 100
        print(
            f"   {cat_name.replace('_', ' ').title()}: {count} apps ({percentage:.1f}%)")


if __name__ == '__main__':
    main()
