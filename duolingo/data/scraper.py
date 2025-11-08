#!/usr/bin/env python3
"""
scrape.py

Scrape Dutch (nl / Netherlands) reviews for a given app from:
 - Apple App Store (iTunes RSS customer reviews)
 - Google Play (google_play_scraper package)

Defaults target Duolingo:
  - Apple App ID: 570060128
  - Google Play package: com.duolingo

Output: JSON lines file (one JSON object per line).

Dependencies:
  pip install requests google-play-scraper

Usage examples:
  python scrape.py --count 500 --out duolingo_nl_reviews.jsonl
  python scrape.py --apple-app-id 570060128 --android-package com.duolingo --count 300
"""

import argparse
import os
import json
import time
import math
from typing import List, Dict, Optional

import requests

# google_play_scraper may be optional if user wants only Apple reviews
try:
    from google_play_scraper import reviews as gp_reviews
    from google_play_scraper import Sort as GP_SORT
except Exception:
    gp_reviews = None
    GP_SORT = None


# -------------------------
# Apple App Store reviewer (RSS JSON)
# -------------------------
def fetch_apple_reviews(app_id: str, country: str = "nl", lang: str = "nl",
                        max_reviews: int = 500, sleep: float = 0.5) -> List[Dict]:
    """
    Fetch reviews from iTunes RSS feed.
    Returns a list of normalized review dicts (source='apple').
    """
    reviews = []
    page = 1
    # The RSS feed returns a "feed" with entries. The first 'entry' can be app metadata.
    # Each page typically contains up to 50 reviews (not guaranteed), so paginate.
    while len(reviews) < max_reviews:
        url = f"https://itunes.apple.com/{country}/rss/customerreviews/page={page}/id={app_id}/sortBy=mostRecent/json"
        try:
            resp = requests.get(url, timeout=15)
            if resp.status_code == 404:
                # no reviews or invalid page/app
                break
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            print(f"[apple] error fetching page {page}: {e}")
            break

        feed = data.get("feed", {})
        entries = feed.get("entry", [])
        # If entries is empty or only contains metadata, stop
        if not entries:
            break

        # The first entry may be the app metadata; reviews start at index 1 typically.
        # Safely iterate and skip entries that look like metadata (no 'content' or 'im:rating')
        for entry in entries:
            # skip metadata-like entry
            if "content" not in entry and "im:rating" not in entry:
                continue
            # Sometimes the first entry is app metadata; check for author/name fields too.
            try:
                content_field = entry.get("content", {})
                content_text = content_field.get("label") if isinstance(
                    content_field, dict) else content_field
                rating_field = entry.get("im:rating", {})
                rating = int(rating_field.get("label")
                             ) if rating_field else None
                author = entry.get("author", {}).get("name", {}).get("label")
                title = entry.get("title", {}).get("label")
                updated = entry.get("updated", {}).get("label")
                version = entry.get("im:version", {}).get(
                    "label") if entry.get("im:version") else None
            except Exception:
                # fall back to raw
                content_text = entry.get("content", {}).get("label") if isinstance(
                    entry.get("content"), dict) else entry.get("content")
                rating = None
                author = None
                title = None
                updated = None
                version = None

            if not content_text and not title:
                continue

            reviews.append({
                "source": "apple",
                "app_id": app_id,
                "country": country,
                "language": lang,
                "author": author,
                "title": title,
                "content": content_text,
                "rating": rating,
                "version": version,
                "updated": updated,
            })

            if len(reviews) >= max_reviews:
                break

        # If we didn't find review-like entries this page, break
        # (avoid infinite loop)
        if all("content" not in e and "im:rating" not in e for e in entries):
            break

        page += 1
        time.sleep(sleep)

    print(f"[apple] fetched {len(reviews)} reviews (requested {max_reviews})")
    return reviews[:max_reviews]


# -------------------------
# Google Play reviewer (google_play_scraper)
# -------------------------
def fetch_google_reviews(package_name: str, lang: str = "nl", country: str = "nl",
                         max_reviews: int = 500, sleep: float = 0.2, chunk: int = 200) -> List[Dict]:
    """
    Fetch reviews from Google Play using google_play_scraper package.
    Returns a list of normalized review dicts (source='google').
    """
    if gp_reviews is None:
        raise RuntimeError(
            "google_play_scraper not installed. Install with: pip install google-play-scraper")

    collected = []
    continuation_token = None
    remaining = max_reviews

    # google_play_scraper supports count but may be limited; fetch in chunks and use pagination token
    while remaining > 0:
        take = min(chunk, remaining)
        try:
            # The gp_reviews function returns (results, continuation_token) when continuation_token provided
            # but different versions vary; handle both shapes.
            if continuation_token:
                result = gp_reviews(
                    package_name,
                    lang=lang,
                    country=country,
                    sort=GP_SORT.NEWEST,
                    count=take,
                    continuation_token=continuation_token,
                )
            else:
                result = gp_reviews(
                    package_name,
                    lang=lang,
                    country=country,
                    sort=GP_SORT.NEWEST,
                    count=take,
                )
        except TypeError:
            # Older versions might not accept continuation_token kw; call without it and rely on count only
            result = gp_reviews(
                package_name,
                lang=lang,
                country=country,
                sort=GP_SORT.NEWEST,
                count=take,
            )
        except Exception as e:
            print(f"[google] error fetching reviews chunk: {e}")
            break

        # result may be tuple (reviews, continuation_token) or just a list
        if isinstance(result, tuple) and len(result) >= 1:
            items = result[0]
            continuation_token = result[1] if len(result) > 1 else None
        else:
            items = result
            # some implementations include 'next' token in meta; we won't rely on it

        if not items:
            break

        for it in items:
            # typical item fields: userName, userImage, content, score, thumbsUpCount, reviewCreatedVersion, at
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

        if len(items) < take:
            # fewer results than requested => exhausted
            break

        remaining = max_reviews - len(collected)
        # If continuation_token is falsy, we will still loop but rely on gp_reviews count param. Avoid infinite loop.
        if not continuation_token and remaining > 0 and len(items) == 0:
            break

        time.sleep(sleep)

    print(
        f"[google] fetched {len(collected)} reviews (requested {max_reviews})")
    return collected[:max_reviews]


# -------------------------
# Writer
# -------------------------
def write_jsonl(reviews: List[Dict], out_path: str):
    # Ensure parent directory exists
    parent = os.path.dirname(out_path) or "."
    try:
        os.makedirs(parent, exist_ok=True)
    except Exception:
        pass

    # Append JSON lines to the file
    with open(out_path, "a", encoding="utf-8") as f:
        for r in reviews:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


# -------------------------
# CLI
# -------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Scrape app reviews from Apple App Store and Google Play (Dutch).")
    parser.add_argument("--apple-app-id", default="570060128",
                        help="Apple App Store numeric app id (default Duolingo: 570060128)")
    parser.add_argument("--android-package", default="com.duolingo",
                        help="Google Play package name (default Duolingo: com.duolingo)")
    parser.add_argument("--country", default="nl",
                        help="Country code for store (default: nl)")
    parser.add_argument("--lang", default="nl",
                        help="Language code (default: nl)")
    parser.add_argument("--count", type=int, default=500,
                        help="Total reviews to fetch from each store (default: 500).")
    default_out = os.path.join(os.path.dirname(
        __file__), "reviews_nl_duolingo.jsonl")
    parser.add_argument("--out", default=default_out,
                        help="Output JSONL file (appends if exists). Defaults to the data folder next to this script.")
    parser.add_argument("--no-google", action="store_true",
                        help="Skip Google Play scraping.")
    parser.add_argument("--no-apple", action="store_true",
                        help="Skip Apple App Store scraping.")

    # ✅ FIX: allow unknown args (like -f from Jupyter)
    args, _ = parser.parse_known_args()

    wanted = args.count
    print(
        f"Starting scrape: apple_app_id={args.apple_app_id} android_package={args.android_package} country={args.country} lang={args.lang} count={args.count}")
    print(f"Appending results to: {os.path.abspath(args.out)}")

    total_written = 0

    if not args.no_apple:
        try:
            apple_reviews = fetch_apple_reviews(
                app_id=args.apple_app_id, country=args.country, lang=args.lang, max_reviews=wanted)
            write_jsonl(apple_reviews, args.out)
            total_written += len(apple_reviews)
        except Exception as e:
            print(f"[apple] failed: {e}")

    if not args.no_google:
        try:
            google_reviews = fetch_google_reviews(
                package_name=args.android_package, lang=args.lang, country=args.country, max_reviews=wanted)
            write_jsonl(google_reviews, args.out)
            total_written += len(google_reviews)
        except Exception as e:
            print(f"[google] failed: {e}")
            print(
                "Hint: ensure google-play-scraper is installed: pip install google-play-scraper")

    print(f"Done. Total reviews appended to {args.out}: {total_written}")


if __name__ == "__main__":
    main()
