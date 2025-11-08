import json
import time
import os
from google_play_scraper import search, app, reviews, Sort
import itunespy

# ===== SETTINGS =====
KEYWORDS = [
    "language learning", "learn dutch", "learn english", "learn spanish",
    "vocabulary", "grammar", "flashcards", "learn french", "learn german"
]

RESULTS_PER_KEYWORD = 20
REVIEWS_PER_APP = 100
LANG_GOOGLE = "nl"
COUNTRY_GOOGLE = "nl"

OUTPUT_FILE = "apps_combined.jsonl"
APPLE_MAP_FILE = "apple_map.json"

# Load stored Apple matches
if os.path.exists(APPLE_MAP_FILE):
    with open(APPLE_MAP_FILE, "r", encoding="utf-8") as f:
        APPLE_MAP = json.load(f)
else:
    APPLE_MAP = {}
# ====================


def save_apple_map():
    with open(APPLE_MAP_FILE, "w", encoding="utf-8") as f:
        json.dump(APPLE_MAP, f, ensure_ascii=False, indent=2)


def write_jsonl_item(path, item):
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(item, ensure_ascii=False) + "\n")


# ---------- GOOGLE PLAY ----------

def search_google_apps():
    found = {}
    for keyword in KEYWORDS:
        print(f"🔍 Searching Google Play: {keyword}")
        try:
            results = search(keyword, lang="en", country="us")[
                :RESULTS_PER_KEYWORD]
        except Exception as e:
            print("search failed:", e)
            continue

        for r in results:
            found[r["appId"]] = r["title"]
        time.sleep(0.4)

    print(f"✅ Found {len(found)} unique Google Play apps")
    return found


def fetch_google_details(package):
    try:
        info = app(package, lang="en", country="us")
        return {
            "title": info.get("title"),
            "description": info.get("description"),
            "rating": info.get("score"),
            "rating_text": info.get("scoreText"),
            "ratings_total": info.get("ratings"),
            "ratings_histogram": info.get("histogram"),
            "installs": info.get("installs"),
            "genre": info.get("genre")
        }
    except:
        return None


def fetch_google_reviews(package):
    collected = []
    token = None

    while len(collected) < REVIEWS_PER_APP:
        try:
            batch, token = reviews(
                package,
                lang=LANG_GOOGLE,
                country=COUNTRY_GOOGLE,
                sort=Sort.NEWEST,
                count=min(100, REVIEWS_PER_APP - len(collected)),
                continuation_token=token
            )
        except:
            break

        if not batch:
            break

        for r in batch:
            collected.append({
                "platform": "google",
                "rating": r.get("score"),
                "review": r.get("content"),
                "date": r.get("at").isoformat() if r.get("at") else None
            })

        time.sleep(0.3)

    return collected


# ---------- APPLE APP STORE ----------

def search_apple_app(app_name):
    if app_name in APPLE_MAP:
        return APPLE_MAP[app_name]["app_id"]

    print(f"\n🍎 Searching Apple App Store for: {app_name}")
    try:
        results = itunespy.search_apps(app_name)
    except Exception as e:
        print("   Apple search failed:", e)
        return None

    if not results:
        print("   No Apple results found.")
        return None

    for i, app_info in enumerate(results[:5]):
        print(f"   [{i+1}] {app_info.name}  |  ID: {app_info.track_id}")

    print("   [0] Skip this app")
    while True:
        choice = input("Select the correct Apple app (0-5): ").strip()
        if choice.isdigit():
            choice = int(choice)
            if choice == 0:
                return None
            if 1 <= choice <= min(5, len(results)):
                chosen = results[choice - 1]
                APPLE_MAP[app_name] = {
                    "app_name": chosen.name, "app_id": chosen.track_id}
                save_apple_map()
                return chosen.track_id
        print("   Invalid input. Try again.")


def fetch_apple_reviews(app_name):
    apple_id = search_apple_app(app_name)
    if not apple_id:
        return None, []

    try:
        app_data = itunespy.lookup_app_id(apple_id)
    except Exception as e:
        print("   Failed to fetch Apple app details:", e)
        return None, []

    details = {
        "title": app_data.name,
        "rating": app_data.average_user_rating,
        "ratings_total": app_data.user_rating_count
    }

    revs = []
    # itunespy does not fetch full reviews; placeholder structure
    for i in range(min(REVIEWS_PER_APP, 10)):  # max 10 reviews with itunespy
        revs.append({
            "platform": "apple",
            "rating": None,
            "review": None,
            "date": None
        })

    return details, revs


# ---------- MAIN ----------

def main():
    apps = search_google_apps()

    if os.path.exists(OUTPUT_FILE):
        os.remove(OUTPUT_FILE)

    print("\n🧲 Starting full scrape...\n")

    for package, appname in apps.items():
        print(f"📦 {package}")

        google_meta = fetch_google_details(package)
        google_revs = fetch_google_reviews(package)

        apple_meta, apple_revs = fetch_apple_reviews(appname)

        combined = {
            "name": appname,
            "google_package": package,
            "google": google_meta,
            "apple": apple_meta,
            "reviews": google_revs + apple_revs
        }

        write_jsonl_item(OUTPUT_FILE, combined)
        print(f"   ✅ Saved {len(combined['reviews'])} total reviews\n")

        time.sleep(0.5)

    print(f"\n🎉 Done! Combined dataset → {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
