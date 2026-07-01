"""
Example of using ofi-chain-forensics as a Python library (not via the
CLI). Run: python examples/basic_usage.py
"""

import json
from pathlib import Path

from ofi_chain_forensics import (
    TransactionGraph,
    score_addresses,
    top_risk_addresses,
    common_input_clustering,
    cluster_summary,
    run_all_detectors,
    export_ofi_compatible,
)

DATA_PATH = Path(__file__).parent.parent / "data" / "sample" / "sample_transactions.json"
BLACKLIST_PATH = Path(__file__).parent.parent / "data" / "sample" / "sample_blacklist.txt"


def main() -> None:
    transactions = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    blacklist = {line.strip() for line in BLACKLIST_PATH.read_text(encoding="utf-8").splitlines() if line.strip()}

    graph = TransactionGraph.from_transactions(transactions)
    print(f"Graph: {graph.num_addresses} addresses, {graph.num_transactions} transactions\n")

    # 1. Raw pattern detectors
    matches = run_all_detectors(graph)
    print(f"Patterns detected: {len(matches)}")
    for m in matches[:5]:
        print(f"  - {m.pattern} @ {m.address} (score: {m.score})")

    # 2. Full risk scoring, with blacklist
    scores = score_addresses(graph, blacklist=blacklist)
    print("\nTop 5 addresses by risk:")
    for s in top_risk_addresses(scores, n=5):
        print(f"  {s.address}: {s.score} ({s.risk_level})")
        for f in s.factors:
            print(f"      -> {f.name}: +{f.contribution} | {f.explanation}")

    # 3. Address clustering (common-input-ownership)
    clusters = common_input_clustering(transactions)
    summary = cluster_summary(graph, clusters)
    print(f"\nClusters identified: {len(summary)} (showing top 3 by size)")
    for c in summary[:3]:
        print(f"  cluster with {c['size']} addresses: {c['addresses']}")

    # 4. OFI-compatible export, ready to import into other tools in the ecosystem
    out_path = Path("/tmp/example_ofi_export.json")
    export_ofi_compatible(scores, out_path, min_score=20.0)
    print(f"\nOFI-compatible export saved to: {out_path}")


if __name__ == "__main__":
    main()
