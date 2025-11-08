import json
import os
from pathlib import Path

# Get the directory of this script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)

INPUT_FILE = os.path.join(PROJECT_DIR, "data", "apps_combined.jsonl")
OUTPUT_DIR = os.path.join(PROJECT_DIR, "individual")

# Create output directory if it doesn't exist
os.makedirs(OUTPUT_DIR, exist_ok=True)

count = 0

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    for line in f:
        if line.strip():
            app_data = json.loads(line.strip())

            # Get app identifier (prefer google_package, fall back to name)
            app_name = app_data.get("google_package") or app_data.get(
                "name", f"app_{count}")

            # Sanitize filename (remove invalid characters)
            safe_name = "".join(
                c if c.isalnum() or c in "._-" else "_" for c in app_name)

            # Create output filename
            output_file = os.path.join(OUTPUT_DIR, f"{safe_name}.jsonl")

            # Write individual app data to file
            with open(output_file, "w", encoding="utf-8") as out:
                json.dump(app_data, out, ensure_ascii=False, indent=2)

            count += 1
            print(f"✅ Saved: {safe_name}.jsonl ({app_name})")

print(f"\n✅ Completed: {count} app(s) separated into {OUTPUT_DIR}")
