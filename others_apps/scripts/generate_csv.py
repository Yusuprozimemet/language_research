import json
import os
import csv
from datetime import datetime

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
    """Extract app metrics from JSON data"""
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
    genre = google.get('genre', 'Unknown') if google else 'Unknown'

    # Combined metrics
    total_ratings = google_ratings_total + apple_ratings_total
    combined_rating = (google_rating + apple_rating) / (int(has_google) +
                                                        int(has_apple)) if (has_google or has_apple) else 0

    return {
        'App Name': name,
        'Package': package,
        'Rating (Google)': round(google_rating, 2) if google_rating > 0 else 'N/A',
        'Rating (Apple)': round(apple_rating, 2) if apple_rating > 0 else 'N/A',
        'Combined Rating': round(combined_rating, 2) if combined_rating > 0 else 'N/A',
        'Total Ratings (Google)': int(google_ratings_total) if google_ratings_total > 0 else 0,
        'Total Ratings (Apple)': int(apple_ratings_total) if apple_ratings_total > 0 else 0,
        'Total Ratings (All)': int(total_ratings) if total_ratings > 0 else 0,
        'Review Count (Dataset)': review_count,
        'Average Review Rating': round(avg_review_rating, 2) if avg_review_rating > 0 else 'N/A',
        'Google Installs': int(google_installs) if google_installs > 0 else 0,
        'Genre': genre,
        'Platform': ('Google & Apple' if has_google and has_apple else 'Google Only' if has_google else 'Apple Only' if has_apple else 'Unknown')
    }


def main():
    """Main function to generate apps.csv"""
    print("🚀 Starting CSV generation...")
    print(f"📁 Input directory: {INPUT_DIR}")
    print(f"📁 Output directory: {OUTPUT_DIR}")

    # Get all JSON files
    files = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith(
        '.jsonl') or f.lower().endswith('.json')]
    if not files:
        print(f"❌ No JSON files found in {INPUT_DIR}")
        return

    print(f"📚 Found {len(files)} app files to process...\n")

    # Process all apps
    all_apps = []
    processed = 0
    skipped = 0

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
            skipped += 1

    print(f"✅ Successfully processed {processed} apps")
    if skipped > 0:
        print(f"⚠️  Skipped {skipped} apps due to errors")

    # Sort by combined rating (descending) then by total ratings (descending)
    all_apps.sort(key=lambda x: (
        0 if isinstance(x['Combined Rating'], str) else x['Combined Rating'],
        x['Total Ratings (All)']
    ), reverse=True)

    # Write to CSV
    csv_path = os.path.join(OUTPUT_DIR, 'apps.csv')

    if all_apps:
        fieldnames = list(all_apps[0].keys())

        with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_apps)

        print(f"\n✅ CSV file generated successfully!")
        print(f"📄 Saved to: {csv_path}")
        print(f"📊 Total apps in CSV: {len(all_apps)}")

        # Print sample
        print(f"\n📋 First 5 apps in CSV:")
        print("-" * 120)
        for i, app in enumerate(all_apps[:5], 1):
            print(f"{i}. {app['App Name']}")
            print(
                f"   Rating: {app['Combined Rating']} | Total Ratings: {app['Total Ratings (All)']} | Reviews: {app['Review Count (Dataset)']} | Genre: {app['Genre']}")
        print("-" * 120)

        # Statistics
        print(f"\n📊 CSV Statistics:")
        valid_ratings = [app['Combined Rating'] for app in all_apps if isinstance(
            app['Combined Rating'], (int, float))]
        if valid_ratings:
            print(
                f"   Average Rating: {sum(valid_ratings) / len(valid_ratings):.2f}")
            print(f"   Highest Rated: {max(valid_ratings):.2f}")
            print(f"   Lowest Rated: {min(valid_ratings):.2f}")

        total_ratings_sum = sum([app['Total Ratings (All)']
                                for app in all_apps])
        print(f"   Total Ratings Across All Apps: {total_ratings_sum:,}")

        total_reviews_sum = sum([app['Review Count (Dataset)']
                                for app in all_apps])
        print(f"   Total Reviews in Dataset: {total_reviews_sum}")

        genres = set([app['Genre'] for app in all_apps])
        print(f"   Unique Genres: {len(genres)}")
    else:
        print("❌ No apps found to process!")


if __name__ == '__main__':
    main()
