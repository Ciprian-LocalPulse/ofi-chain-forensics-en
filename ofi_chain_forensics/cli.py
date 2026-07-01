"""
cli.py
------
Command-line interface for ofi-chain-forensics.

Usage:
    python -m ofi_chain_forensics.cli analyze data/sample/sample_transactions.json \
        --blacklist data/sample/sample_blacklist.txt \
        --out-csv results.csv --out-json results.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .graph import TransactionGraph
from .risk_scoring import score_addresses, top_risk_addresses
from .export import export_csv, export_json, export_ofi_compatible
from .clustering import common_input_clustering, cluster_summary


def _load_transactions(path: str) -> list[dict]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("The transactions file must contain a JSON list.")
    return data


def _load_blacklist(path: str | None) -> set[str]:
    if not path:
        return set()
    return {line.strip() for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip()}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="ofi-chain-forensics",
        description="Fraud/AML analysis on blockchain transaction graphs.",
    )
    parser.add_argument("transactions", help="JSON file with the list of normalized transactions.")
    parser.add_argument("--blacklist", help=".txt file with one address per line, known blacklist.")
    parser.add_argument("--out-csv", help="Output path for CSV results.")
    parser.add_argument("--out-json", help="Output path for full JSON results.")
    parser.add_argument("--out-ofi", help="Output path for OFI-compatible JSON (risk >= threshold only).")
    parser.add_argument("--min-score", type=float, default=30.0, help="Minimum score threshold for --out-ofi (default 30).")
    parser.add_argument("--top", type=int, default=15, help="How many top-risk addresses to display in the console.")
    parser.add_argument("--show-clusters", action="store_true", help="Also display the CIOH cluster summary.")

    args = parser.parse_args(argv)

    transactions = _load_transactions(args.transactions)
    blacklist = _load_blacklist(args.blacklist)

    graph = TransactionGraph.from_transactions(transactions)
    print(f"Graph built: {graph.num_addresses} addresses, {graph.num_transactions} transactions.\n")

    scores = score_addresses(graph, blacklist=blacklist)
    top = top_risk_addresses(scores, n=args.top)

    print(f"Top {len(top)} addresses by risk score:")
    print(f"{'Address':<45}{'Score':>8}  Level")
    print("-" * 70)
    for s in top:
        print(f"{s.address:<45}{s.score:>8.2f}  {s.risk_level}")

    if args.show_clusters:
        clusters = common_input_clustering(transactions)
        summary = cluster_summary(graph, clusters)
        print("\nTop clusters (common-input-ownership heuristic):")
        for c in summary[:10]:
            print(f"  cluster ({c['size']} addresses) — in: {c['total_in']:.4f}, out: {c['total_out']:.4f}")

    if args.out_csv:
        export_csv(scores, args.out_csv)
        print(f"\nCSV saved: {args.out_csv}")
    if args.out_json:
        export_json(scores, args.out_json)
        print(f"JSON saved: {args.out_json}")
    if args.out_ofi:
        export_ofi_compatible(scores, args.out_ofi, min_score=args.min_score)
        print(f"OFI-compatible export saved: {args.out_ofi} (threshold >= {args.min_score})")

    return 0


if __name__ == "__main__":
    sys.exit(main())
