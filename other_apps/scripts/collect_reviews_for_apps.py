#!/usr/bin/env python3
"""
Collect reviews (Google Play + Apple fallback) for a list of language apps.

This script uses the helper functions in `other_apps/data/scraper.py`.
It fetches up to N reviews per app (default 300) from Google Play using hardcoded package names.

Outputs:
  other_apps/output/reviews_<slug>.jsonl  # per-app reviews
  other_apps/output/reviews_combined.jsonl # all apps appended

Usage:
  python collect_reviews_for_apps_fixed.py

Notes:
 - Requires `google_play_scraper` and `itunespy` installed.
 - Uses hardcoded packages to avoid search failures.
 - Google Play limits apply; uses continuation tokens where possible.
"""
from __future__ import annotations

import json
import os
import time
import argparse
import re
from pathlib import Path

import importlib.util
from pathlib import Path

# Import the scraper module by path
script_dir = Path(__file__).resolve().parent
scraper_path = script_dir.parent / "data" / "scraper.py"
spec = importlib.util.spec_from_file_location("scraper_mod", str(scraper_path))
scraper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(scraper)

APPS = [
    "Duolingo",
    "Quizlet",
    "Busuu",
    "Falou",
    "Babbel",
    "Rosetta Stone",
    "Memrise",
]

# Hardcoded package names from Google Play URLs (Nov 2025)
PACKAGE_MAP = {
    "Duolingo": ("com.duolingo", "Duolingo: Language Lessons"),
    "Quizlet": ("com.quizlet.quizletandroid", "Quizlet: More than Flashcards"),
    "Busuu": ("com.busuu.android.enc", "Busuu: Learn & Speak Languages"),
    "Falou": ("com.moymer.falou", "Falou - Fast language learning"),
    "Babbel": ("com.babbel.mobile.android.en", "Babbel - Learn Languages"),
    "Rosetta Stone": ("air.com.rosettastone.mobile.CoursePlayer", "Rosetta Stone: Learn, Practice"),
    "Memrise": ("com.memrise.android.memrisecompanion", "Memrise: Languages for life"),
}


def slugify(name: str) -> str:
    s = name.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s


def collect_for_app(name: str, out_dir: str, per_app: int = 300):
    if name not in PACKAGE_MAP:
        print(f"No package found for '{name}' – skipping.")
        return 0

    package, title = PACKAGE_MAP[name]
    print(f"Collecting for {name} -> {package} ({title})")

    # Adjust module-level constant
    scraper.REVIEWS_PER_APP = per_app

    try:
        google_meta = scraper.fetch_google_details(package)
        google_revs = scraper.fetch_google_reviews(package)
    except Exception as e:
        print(f"Error fetching Google data for {name}: {e}")
        google_meta = {}
        google_revs = []

    # Apple fallback (uses title)
    try:
        apple_meta, apple_revs = scraper.fetch_apple_reviews(title)
    except Exception as e:
        print(f"Error fetching Apple data for {name}: {e}")
        apple_meta = {}
        apple_revs = []

    combined = {
        "name": title or name,
        "google_package": package,
        "google": google_meta,
        "apple": apple_meta,
        "reviews": google_revs + (apple_revs or [])
    }

    # Save per-app file
    slug = slugify(name)
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    out_file = os.path.join(out_dir, f"reviews_{slug}.jsonl")
    with open(out_file, "w", encoding="utf-8") as fh:
        fh.write(json.dumps(combined, ensure_ascii=False) + "\n")

    print(f"Saved {len(combined['reviews'])} reviews for {name} -> {out_file}")
    return len(combined["reviews"])


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--out-dir", default=os.path.join(os.path.dirname(__file__),
                   "..", "output"), help="Output directory")
    p.add_argument("--per-app", type=int, default=300,
                   help="Number of reviews per app to fetch (default 300)")
    args = p.parse_args()

    out_dir = os.path.abspath(args.out_dir)
    combined_out = os.path.join(out_dir, "reviews_combined.jsonl")
    Path(out_dir).mkdir(parents=True, exist_ok=True)

    # Optional: Append to combined file
    combined_reviews = []
    if os.path.exists(combined_out):
        with open(combined_out, "r", encoding="utf-8") as fh:
            for line in fh:
                combined_reviews.append(json.loads(line.strip()))

    total = 0
    for app_name in APPS:
        try:
            n = collect_for_app(app_name, out_dir, per_app=args.per_app)
            total += n

            # Append to combined (per-app data)
            slug = slugify(app_name)
            per_app_file = os.path.join(out_dir, f"reviews_{slug}.jsonl")
            if os.path.exists(per_app_file):
                with open(per_app_file, "r", encoding="utf-8") as fh:
                    combined_reviews.append(json.loads(fh.read().strip()))
        except Exception as e:
            print(f"Error collecting for {app_name}: {e}")
        time.sleep(1.0)  # Rate limit

    # Save combined
    with open(combined_out, "w", encoding="utf-8") as fh:
        for rev_data in combined_reviews:
            fh.write(json.dumps(rev_data, ensure_ascii=False) + "\n")

    print(
        f"Done. Collected approximately {total} reviews (sum across apps). Combined file: {combined_out}")


if __name__ == "__main__":
    main()
