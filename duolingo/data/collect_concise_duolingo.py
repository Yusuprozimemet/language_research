#!/usr/bin/env python3
"""
Read duolingo/data/reviews_nl_duolingo.jsonl and write concise_duolingo.json
keeping only the fields: source, author, content

Output format: JSON array (list) written to duolingo/data/concise_duolingo.json with UTF-8 encoding.
This script streams input and writes output incrementally so it works for large files.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
INPUT = ROOT / "reviews_nl_duolingo.jsonl"
OUTPUT = ROOT / "concise_duolingo.json"

FIELDS = ("source", "author", "content")


def extract_fields(obj):
    # Return dict with only the requested fields. If a field missing, set None.
    return {k: obj.get(k) for k in FIELDS}


def main():
    if not INPUT.exists():
        print(f"Input file not found: {INPUT}")
        return

    # Stream read and write JSON array without loading everything into memory.
    with INPUT.open("r", encoding="utf-8") as fin, OUTPUT.open("w", encoding="utf-8") as fout:
        fout.write("[")
        first = True
        for line in fin:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                # Skip malformed lines but continue processing
                continue
            concise = extract_fields(obj)
            if not first:
                fout.write(",\n")
            else:
                first = False
            json.dump(concise, fout, ensure_ascii=False)
        fout.write("\n]")

    print(f"Wrote concise JSON to {OUTPUT}")


if __name__ == "__main__":
    main()
