"""
ofi-chain-forensics
====================
Open-source Python library for blockchain fraud and money-laundering
detection, through structural analysis of the transaction graph.

Complementary module to the Open Fraud Intelligence (OFI) project.
License: MIT. Free for any use, commercial or non-commercial.

Quick example:

    from ofi_chain_forensics import TransactionGraph, score_addresses

    graph = TransactionGraph.from_transactions(my_transactions)
    scores = score_addresses(graph, blacklist=my_known_bad_addresses)

    for addr, s in sorted(scores.items(), key=lambda x: -x[1].score)[:10]:
        print(addr, s.score, s.risk_level)
"""

from .graph import TransactionGraph
from .clustering import common_input_clustering, change_address_candidates, cluster_summary
from .patterns import (
    PatternMatch,
    detect_fan_out,
    detect_fan_in,
    detect_rapid_passthrough,
    detect_peeling_chain,
    run_all_detectors,
)
from .risk_scoring import RiskFactor, RiskScore, score_addresses, top_risk_addresses
from .export import export_csv, export_json, export_ofi_compatible

__version__ = "0.1.0"

__all__ = [
    "TransactionGraph",
    "common_input_clustering",
    "change_address_candidates",
    "cluster_summary",
    "PatternMatch",
    "detect_fan_out",
    "detect_fan_in",
    "detect_rapid_passthrough",
    "detect_peeling_chain",
    "run_all_detectors",
    "RiskFactor",
    "RiskScore",
    "score_addresses",
    "top_risk_addresses",
    "export_csv",
    "export_json",
    "export_ofi_compatible",
]
