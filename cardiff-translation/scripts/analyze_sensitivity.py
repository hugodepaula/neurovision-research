"""Run the human-reference questionnaire sensitivity analysis."""

from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".cache/matplotlib"))
os.environ.setdefault("HF_HOME", str(ROOT / ".cache/huggingface"))
os.environ.setdefault("HF_HUB_DISABLE_XET", "1")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="New output directory; existing directories are never overwritten",
    )
    parser.add_argument("--resamples", type=int, default=10000)
    parser.add_argument("--permutations", type=int, default=10000)
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument(
        "--semantic",
        choices=["auto", "off"],
        default="auto",
        help="auto attempts both models and exits 2 if either is unavailable; off explicitly requests lexical analysis",
    )
    parser.add_argument(
        "--exploratory-margin",
        type=float,
        default=0.01,
        help="Raw-score tolerance sensitivity, not a validated equivalence margin",
    )
    args = parser.parse_args()
    if args.exploratory_margin <= 0:
        parser.error("exploratory margin must be positive")
    output = args.output or ROOT / "results/sensitivity" / datetime.now(
        timezone.utc
    ).strftime("%Y%m%dT%H%M%S%fZ")
    from cardiff.analysis.sensitivity.pipeline import run_analysis

    metadata = run_analysis(
        ROOT,
        output,
        args.resamples,
        args.seed,
        args.permutations,
        args.semantic,
        args.exploratory_margin,
    )
    print(f"Report: {output / 'report.html'}; status: {metadata['status']}", flush=True)
    return 2 if metadata["status"] == "partial" else 0


if __name__ == "__main__":
    raise SystemExit(main())
