"""
patterns.py
-----------
Detectors for structural patterns frequently associated with money
laundering or fund obfuscation on blockchains. Each detector is
documented with its conceptual source and known false-positive rate —
none of them is presented as "proof of fraud", but rather as a signal
for further investigation (consistent with how OFI already treats DNSC
sources).

Patterns covered:
  - Peeling chain: a large amount is successively "peeled off" through a
    chain of transactions, with a small portion sent to a third-party
    address and the rest forwarded further on (typical for gradual
    withdrawal from mixers or exchanges toward cash-out).
  - Fan-out: an address sends funds simultaneously to an unusually large
    number of new addresses (possible distribution / "smurfing").
  - Fan-in: an unusually large number of addresses send funds to a
    single address within a short time window (possible pre-cash-out
    aggregation).
  - Rapid pass-through: an address receives funds and forwards >X% of
    them in less than Y seconds (sign of automated "hopping", typical of
    layering).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .graph import TransactionGraph


@dataclass
class PatternMatch:
    pattern: str
    address: str
    score: float  # 0.0 - 1.0, signal intensity, NOT probability of fraud
    details: dict[str, Any] = field(default_factory=dict)


def detect_fan_out(graph: TransactionGraph, threshold: int = 10) -> list[PatternMatch]:
    matches = []
    for node in graph.graph.nodes:
        out_neighbors = set(graph.graph.successors(node))
        if len(out_neighbors) >= threshold:
            score = min(1.0, len(out_neighbors) / (threshold * 3))
            matches.append(
                PatternMatch(
                    pattern="fan_out",
                    address=node,
                    score=round(score, 3),
                    details={"distinct_recipients": len(out_neighbors)},
                )
            )
    return matches


def detect_fan_in(graph: TransactionGraph, threshold: int = 10) -> list[PatternMatch]:
    matches = []
    for node in graph.graph.nodes:
        in_neighbors = set(graph.graph.predecessors(node))
        if len(in_neighbors) >= threshold:
            score = min(1.0, len(in_neighbors) / (threshold * 3))
            matches.append(
                PatternMatch(
                    pattern="fan_in",
                    address=node,
                    score=round(score, 3),
                    details={"distinct_senders": len(in_neighbors)},
                )
            )
    return matches


def detect_rapid_passthrough(
    graph: TransactionGraph,
    min_retained_ratio_below: float = 0.05,
    max_seconds_between: int = 3600,
) -> list[PatternMatch]:
    """Looks for addresses that receive funds and forward almost all of
    them (retaining under `min_retained_ratio_below` of the amount)
    within a short interval.
    """
    matches = []
    for node in graph.graph.nodes:
        in_edges = list(graph.graph.in_edges(node, data=True))
        out_edges = list(graph.graph.out_edges(node, data=True))
        if not in_edges or not out_edges:
            continue

        total_in = sum(d.get("amount", 0.0) for _, _, d in in_edges)
        total_out = sum(d.get("amount", 0.0) for _, _, d in out_edges)
        if total_in <= 0:
            continue

        retained_ratio = max(0.0, (total_in - total_out) / total_in)

        last_in_ts = max((d.get("timestamp") or 0) for _, _, d in in_edges)
        first_out_ts = min((d.get("timestamp") or 0) for _, _, d in out_edges)
        delta = first_out_ts - last_in_ts

        if retained_ratio <= min_retained_ratio_below and 0 <= delta <= max_seconds_between:
            score = round(1.0 - retained_ratio, 3)
            matches.append(
                PatternMatch(
                    pattern="rapid_passthrough",
                    address=node,
                    score=score,
                    details={
                        "retained_ratio": round(retained_ratio, 4),
                        "seconds_between": delta,
                        "total_in": round(total_in, 8),
                        "total_out": round(total_out, 8),
                    },
                )
            )
    return matches


def detect_peeling_chain(
    graph: TransactionGraph,
    min_chain_length: int = 4,
    peel_ratio_max: float = 0.15,
) -> list[PatternMatch]:
    """Follows chains of transactions where, at each step, a small
    fraction of the amount (<= peel_ratio_max) "breaks off" to a
    third-party address, while the rest continues to a single next
    address in the chain.
    """
    matches: list[PatternMatch] = []
    visited_starts: set[str] = set()

    for node in graph.graph.nodes:
        if node in visited_starts:
            continue
        chain = [node]
        current = node
        peeled_addresses = []

        while True:
            out_edges = list(graph.graph.out_edges(current, data=True))
            if len(out_edges) != 2:
                break
            total_out = sum(d.get("amount", 0.0) for _, _, d in out_edges)
            if total_out <= 0:
                break

            small_edge = min(out_edges, key=lambda e: e[2].get("amount", 0.0))
            large_edge = max(out_edges, key=lambda e: e[2].get("amount", 0.0))
            small_ratio = small_edge[2].get("amount", 0.0) / total_out

            if small_ratio > peel_ratio_max:
                break

            peeled_addresses.append(small_edge[1])
            current = large_edge[1]
            chain.append(current)
            visited_starts.add(current)

            if len(chain) > 50:  # anti-infinite-loop protection
                break

        if len(chain) - 1 >= min_chain_length:
            matches.append(
                PatternMatch(
                    pattern="peeling_chain",
                    address=node,
                    score=round(min(1.0, (len(chain) - 1) / (min_chain_length * 2)), 3),
                    details={
                        "chain_length": len(chain) - 1,
                        "chain": chain,
                        "peeled_to": peeled_addresses,
                    },
                )
            )

    return matches


def run_all_detectors(graph: TransactionGraph, **kwargs: Any) -> list[PatternMatch]:
    """Runs all available detectors with default parameters (or overrides
    via kwargs, e.g. fan_out_threshold=15)."""
    results: list[PatternMatch] = []
    results += detect_fan_out(graph, threshold=kwargs.get("fan_out_threshold", 10))
    results += detect_fan_in(graph, threshold=kwargs.get("fan_in_threshold", 10))
    results += detect_rapid_passthrough(
        graph,
        min_retained_ratio_below=kwargs.get("min_retained_ratio_below", 0.05),
        max_seconds_between=kwargs.get("max_seconds_between", 3600),
    )
    results += detect_peeling_chain(
        graph,
        min_chain_length=kwargs.get("min_chain_length", 4),
        peel_ratio_max=kwargs.get("peel_ratio_max", 0.15),
    )
    return results
