#!/usr/bin/env python3
"""
scrape.py

Scrape Dutch (nl / Netherlands) reviews for:
 - Apple App Store (RSS customer reviews)
 - Google Play (google_play_scraper)

Supports:
 - Single-app mode (default Duolingo)
 - Multi-app mode (--multi) using PACKAGE_MAP

Output: JSON Lines (.jsonl)

Dependencies:
  pip install requests google-play-scraper
"""

import argparse
import os
import json
import time
from typing import List, Dict, Optional

import requests

try:
    from google_play_scraper import reviews as gp_reviews
    from google_play_scraper import Sort as GP_SORT
except Exception:
    gp_reviews = None
    GP_SORT = None


# ========================================================
# MULTI-APP PACKAGE MAP
# Format: "App Name": (Google Package Name, Apple App ID or None)
# Fill in Apple IDs later if known.
# ========================================================
PACKAGE_MAP = {
    "Duolingo": ("com.duolingo", "570060128"),
    "Quizlet": ("com.quizlet.quizletandroid", None),
    "Busuu": ("com.busuu.android.enc", None),
    "Falou": ("com.moymer.falou", None),
    "Babbel": ("com.babbel.mobile.android.en", None),
    "Rosetta Stone": ("air.com.rosettastone.mobile.CoursePlayer", None),
    "Memrise": ("com.memrise.android.memrisecompanion", None),
}


# ========================================================
# Apple Review Fetcher
# ========================================================
def fetch_apple_reviews(app_id: str, country: str = "nl", lang: str = "nl",
                        max_reviews: int = 500, sleep: float = 0.5) -> List[Dict]:
    reviews = []
    page = 1

    while len(reviews) < max_reviews:
        url = f"https://itunes.apple.com/{country}/rss/customerreviews/page={page}/id={app_id}/sortBy=mostRecent/json"
        try:
            resp = requests.get(url, timeout=15)
            if resp.status_code == 404:
                break
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            print(f"[apple] error fetching page {page}: {e}")
            break

        entries = data.get("feed", {}).get("entry", [])
        if not entries:
            break

        for entry in entries:
            if "content" not in entry and "im:rating" not in entry:
                continue

            content_field = entry.get("content", {})
            content_text = content_field.get("label") if isinstance(
                content_field, dict) else content_field

            rating_field = entry.get("im:rating", {})
            rating = int(rating_field.get("label")) if rating_field else None

            reviews.append({
                "source": "apple",
                "app_id": app_id,
                "country": country,
                "language": lang,
                "author": entry.get("author", {}).get("name", {}).get("label"),
                "title": entry.get("title", {}).get("label"),
                "content": content_text,
                "rating": rating,
                "version": entry.get("im:version", {}).get("label"),
                "updated": entry.get("updated", {}).get("label"),
            })

            if len(reviews) >= max_reviews:
                break

        page += 1
        time.sleep(sleep)

    print(f"[apple] fetched {len(reviews)} reviews (requested {max_reviews})")
    return reviews[:max_reviews]


# ========================================================
# Google Review Fetcher
# ========================================================
def fetch_google_reviews(package_name: str, lang: str = "nl", country: str = "nl",
                         max_reviews: int = 500, sleep: float = 0.2, chunk: int = 200) -> List[Dict]:

    if gp_reviews is None:
        raise RuntimeError(
            "google-play-scraper missing. Install: pip install google-play-scraper")

    collected = []
    continuation_token = None
    remaining = max_reviews

    while remaining > 0:
        take = min(chunk, remaining)

        try:
            if continuation_token:
                result = gp_reviews(package_name, lang=lang, country=country,
                                    sort=GP_SORT.NEWEST, count=take, continuation_token=continuation_token)
            else:
                result = gp_reviews(package_name, lang=lang, country=country,
                                    sort=GP_SORT.NEWEST, count=take)
        except Exception as e:
            print(f"[google] error fetching reviews: {e}")
            break

        items = result[0] if isinstance(result, tuple) else result
        continuation_token = result[1] if isinstance(
            result, tuple) and len(result) > 1 else None

        if not items:
            break

        for it in items:
            collected.append({
                "source": "google",
                "package": package_name,
                "country": country,
                "language": lang,
                "author": it.get("userName"),
                "content": it.get("content"),
                "score": it.get("score"),
                "thumbs_up_count": it.get("thumbsUpCount"),
                "review_created_version": it.get("reviewCreatedVersion"),
                "at": it.get("at").isoformat() if it.get("at") else None,
            })

            if len(collected) >= max_reviews:
                break

        remaining = max_reviews - len(collected)
        time.sleep(sleep)

    print(
        f"[google] fetched {len(collected)} reviews (requested {max_reviews})")
    return collected[:max_reviews]


# ========================================================
# Writer
# ========================================================
def write_jsonl(reviews: List[Dict], out_path: str):
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    with open(out_path, "a", encoding="utf-8") as f:
        for r in reviews:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


# ========================================================
# Main
# ========================================================
def main():
    parser = argparse.ArgumentParser(
        description="Scrape app reviews (Apple + Google) in Dutch.")
    parser.add_argument("--apple-app-id", default="570060128")
    parser.add_argument("--android-package", default="com.duolingo")
    parser.add_argument("--country", default="nl")
    parser.add_argument("--lang", default="nl")
    parser.add_argument("--count", type=int, default=500)
    parser.add_argument("--multi", action="store_true",
                        help="Scrape all apps in PACKAGE_MAP.")
    parser.add_argument("--no-google", action="store_true")
    parser.add_argument("--no-apple", action="store_true")

    default_out = os.path.join(os.path.dirname(__file__), "reviews_nl.jsonl")
    parser.add_argument("--out", default=default_out)

    args, _ = parser.parse_known_args()

    wanted = args.count
    total_written = 0

    print(f"Output → {os.path.abspath(args.out)}")

    # MULTI-APP MODE
    if args.multi:
        for app_name, (pkg, apple_id) in PACKAGE_MAP.items():
            print(f"\n===== {app_name} =====")

            if not args.no_apple and apple_id:
                apple_reviews = fetch_apple_reviews(
                    apple_id, args.country, args.lang, wanted)
                write_jsonl(apple_reviews, args.out)
                total_written += len(apple_reviews)

            if not args.no_google and pkg:
                google_reviews = fetch_google_reviews(
                    pkg, args.lang, args.country, wanted)
                write_jsonl(google_reviews, args.out)
                total_written += len(google_reviews)

    # SINGLE-APP MODE
    else:
        if not args.no_apple:
            apple_reviews = fetch_apple_reviews(
                args.apple_app_id, args.country, args.lang, wanted)
            write_jsonl(apple_reviews, args.out)
            total_written += len(apple_reviews)

        if not args.no_google:
            google_reviews = fetch_google_reviews(
                args.android_package, args.lang, args.country, wanted)
            write_jsonl(google_reviews, args.out)
            total_written += len(google_reviews)

    print(f"\nDone. Total reviews written: {total_written}")


if __name__ == "__main__":
    main()
