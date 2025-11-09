#!/usr/bin/env python3
"""
Extract the "Excellent" apps (top N) from the evaluation script and attach descriptions
from the combined apps JSONL file.

Usage:
    python extract_excellent_apps.py

Outputs:
    other_apps/output/excellent_apps.csv
    other_apps/output/excellent_apps.jsonl

The script will parse the literal `raw_apps` and `extra_apps` lists from
`other_apps/scripts/evaluation.py`, recompute the composite score using the
same formula, pick the top-N apps (default 35), and attach the description
from `other_apps/data/apps_combined.jsonl` using exact or fuzzy name matching.
"""
from __future__ import annotations

import argparse
import ast
import json
import os
import re
from difflib import get_close_matches
from typing import List, Tuple

import numpy as np
import pandas as pd
from scipy.stats import zscore


def extract_literal_list(file_path: str, var_name: str):
    """Extract a Python literal list assigned to `var_name` in the given file.

    This finds the first occurrence of `var_name` and then finds the bracketed
    list literal and returns a Python object via ast.literal_eval.
    """
    text = open(file_path, encoding="utf-8").read()
    # find the var_name = [
    m = re.search(rf"\b{re.escape(var_name)}\s*=\s*\[", text)
    if not m:
        raise ValueError(
            f"Could not find assignment for {var_name} in {file_path}")
    start = m.end() - 1  # points to the '['
    # find matching closing bracket
    depth = 0
    end = None
    for i in range(start, len(text)):
        ch = text[i]
        if ch == "[":
            depth += 1
        elif ch == "]":
            depth -= 1
            if depth == 0:
                end = i + 1
                break
    if end is None:
        raise ValueError(f"Could not find end of list for {var_name}")
    literal = text[start:end]
    # Some tuples may use numpy.nan (np.nan) - ast.literal_eval cannot handle
    # expressions like `float('nan')` or `np.nan`. Replace `np.nan` with
    # the literal `None` so literal_eval can parse it; we'll let pandas
    # coerce None -> NaN later when creating the DataFrame.
    literal_safe = literal.replace("np.nan", "None")
    return ast.literal_eval(literal_safe)


def load_apps_combined(jsonl_path: str):
    mapping = {}
    if not os.path.exists(jsonl_path):
        return mapping
    with open(jsonl_path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except Exception:
                # skip malformed
                continue
            # prefer the 'name' field
            name = obj.get("name") or (obj.get("google", {}).get("title"))
            desc = None
            if isinstance(obj.get("google"), dict):
                desc = obj["google"].get("description")
            mapping[name] = {"desc": desc, "raw": obj}
    return mapping


def compute_scores(all_apps: List[Tuple]) -> pd.DataFrame:
    df = pd.DataFrame(all_apps, columns=[
        "App Name", "Rating", "Google Ratings", "Reviews (Dataset)", "Genre"
    ])
    df = df.drop_duplicates(
        subset="App Name", keep="first").reset_index(drop=True)
    df["Rating"] = pd.to_numeric(df["Rating"], errors="coerce")
    df["Google Ratings"] = pd.to_numeric(df["Google Ratings"], errors="coerce")
    df["Reviews (Dataset)"] = pd.to_numeric(
        df["Reviews (Dataset)"], errors="coerce")

    df["log_ratings"] = np.log1p(df["Google Ratings"].fillna(0))
    df["log_reviews"] = np.log1p(df["Reviews (Dataset)"].fillna(0))

    df["z_rating"] = zscore(df["Rating"].fillna(df["Rating"].median()))
    df["z_log_ratings"] = zscore(
        df["log_ratings"]) if df["log_ratings"].nunique() > 1 else 0
    df["z_log_reviews"] = zscore(
        df["log_reviews"]) if df["log_reviews"].nunique() > 1 else 0

    genre_bonus = {
        "Education": 1.0,
        "Educational": 1.0,
        "Productivity": 0.8,
        "Tools": 0.6,
        "Books & Reference": 0.6,
        "Travel & Local": 0.6
    }
    df["genre_bonus"] = df["Genre"].map(genre_bonus).fillna(0.6)
    df["z_genre"] = zscore(
        df["genre_bonus"]) if df["genre_bonus"].nunique() > 1 else 0

    df["Composite Score"] = (
        0.40 * df["z_rating"] +
        0.30 * df["z_log_ratings"] +
        0.20 * df["z_log_reviews"] +
        0.10 * df["z_genre"]
    )

    df = df.sort_values("Composite Score",
                        ascending=False).reset_index(drop=True)
    df["Rank"] = df.index + 1
    return df


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--evaluation", default=os.path.join(os.path.dirname(__file__),
                   "evaluation.py"), help="Path to evaluation.py")
    p.add_argument("--apps-jsonl", default=os.path.join(os.path.dirname(os.path.dirname(
        __file__)), "data", "apps_combined.jsonl"), help="Path to apps_combined.jsonl")
    p.add_argument("--top", type=int, default=35,
                   help="Top N apps to extract (default 35)")
    p.add_argument("--out-dir", default=os.path.join(os.path.dirname(
        os.path.dirname(__file__)), "output"), help="Output directory")
    args = p.parse_args()

    eval_py = args.evaluation
    apps_jsonl = args.apps_jsonl
    top_n = args.top
    out_dir = args.out_dir
    os.makedirs(out_dir, exist_ok=True)

    # parse raw_apps and extra_apps from evaluation.py
    try:
        raw_apps = extract_literal_list(eval_py, "raw_apps")
    except Exception as e:
        raise RuntimeError(f"Failed to parse raw_apps from {eval_py}: {e}")
    try:
        extra_apps = extract_literal_list(eval_py, "extra_apps")
    except Exception:
        extra_apps = []

    all_apps = raw_apps + extra_apps

    df = compute_scores(all_apps)

    top_df = df.head(top_n).copy()

    mapping = load_apps_combined(apps_jsonl)
    names_available = list(mapping.keys())

    results = []
    for _, row in top_df.iterrows():
        name = row["App Name"]
        desc = None
        matched_key = None
        if name in mapping and mapping[name]["desc"]:
            desc = mapping[name]["desc"]
            matched_key = name
        else:
            # try to match against titles using difflib
            candidates = get_close_matches(
                name, names_available, n=1, cutoff=0.7)
            if candidates:
                matched_key = candidates[0]
                desc = mapping[matched_key].get("desc")

        results.append({
            "Rank": int(row["Rank"]),
            "App Name": name,
            "Rating": row.get("Rating"),
            "Google Ratings": int(row.get("Google Ratings") or 0),
            "Reviews (Dataset)": int(row.get("Reviews (Dataset)") or 0),
            "Composite Score": float(row.get("Composite Score") or 0.0),
            "Matched Name": matched_key,
            "Description": desc
        })

    # save CSV
    out_csv = os.path.join(out_dir, "excellent_apps.csv")
    pd.DataFrame(results).to_csv(out_csv, index=False)

    # save JSONL (full description JSON per line)
    out_jsonl = os.path.join(out_dir, "excellent_apps.jsonl")
    with open(out_jsonl, "w", encoding="utf-8") as fh:
        for r in results:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")

    print(f"Wrote {len(results)} top apps to:\n - {out_csv}\n - {out_jsonl}")


if __name__ == "__main__":
    main()
