#!/usr/bin/env python3
"""
Run the content integrity benchmark on a model.

Examples:
    python run_benchmark.py --model claude-sonnet-4-5-20250929
    python run_benchmark.py --model gpt-4o --runs 5
    python run_benchmark.py --model gpt-5 --runs 3 --out results/gpt5.json

Needs ANTHROPIC_API_KEY (for claude* models) or OPENAI_API_KEY (for gpt*/o*).
"""

import argparse
import json
from cib import evaluate


def main():
    ap = argparse.ArgumentParser(description="Content Integrity Benchmark")
    ap.add_argument("--model", required=True, help="claude* or gpt*/o* model id")
    ap.add_argument("--runs", type=int, default=3, help="repetitions per case (default 3)")
    ap.add_argument("--out", help="optional path to write the results JSON")
    args = ap.parse_args()

    res = evaluate(args.model, runs=args.runs)

    if args.out:
        with open(args.out, "w") as f:
            json.dump(res, f, indent=2)
        print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()
