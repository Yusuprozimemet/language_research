#!/usr/bin/env python3
"""
List only the excellent apps' names (top N) determined by evaluation.py

Usage:
    python list_excellent_names.py

Outputs:
    other_apps/output/excellent_names.txt  # one name per line
    other_apps/output/excellent_names.json # JSON list of names

This script reuses the parsing and scoring logic from
`extract_excellent_apps.py` (loads it as a module by path) so it follows the
same composite scoring and ranking.
"""
from __future__ import annotations

import importlib.util
import json
import os
import argparse
from typing import List


def load_module_from_path(path: str):
    spec = importlib.util.spec_from_file_location("extract_mod", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--extract-module", default=os.path.join(os.path.dirname(__file__),
                   "extract_excellent_apps.py"), help="Path to extract_excellent_apps.py")
    p.add_argument("--evaluation", default=os.path.join(os.path.dirname(__file__),
                   "evaluation.py"), help="Path to evaluation.py")
    p.add_argument("--top", type=int, default=35,
                   help="Top N apps to list (default 35)")
    p.add_argument("--out-dir", default=os.path.join(os.path.dirname(
        os.path.dirname(__file__)), "output"), help="Output directory")
    args = p.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)

    mod = load_module_from_path(args.extract_module)

    # parse raw and extra apps using the helper from the extract module
    raw_apps = mod.extract_literal_list(args.evaluation, "raw_apps")
    try:
        extra_apps = mod.extract_literal_list(args.evaluation, "extra_apps")
    except Exception:
        extra_apps = []

    all_apps = raw_apps + extra_apps

    df = mod.compute_scores(all_apps)
    top_n = args.top
    top_df = df.head(top_n)

    names: List[str] = list(top_df["App Name"].astype(str).tolist())

    out_txt = os.path.join(args.out_dir, "excellent_names.txt")
    out_json = os.path.join(args.out_dir, "excellent_names.json")

    with open(out_txt, "w", encoding="utf-8") as fh:
        for n in names:
            fh.write(n + "\n")

    with open(out_json, "w", encoding="utf-8") as fh:
        json.dump(names, fh, ensure_ascii=False, indent=2)

    print(
        f"Wrote {len(names)} excellent app names to:\n - {out_txt}\n - {out_json}")


if __name__ == "__main__":
    main()
