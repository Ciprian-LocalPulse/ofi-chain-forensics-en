"""
clustering.py
--------------
Classic address-clustering heuristics based on the transaction graph.
These are well-established techniques from the blockchain research
literature (Meiklejohn et al. 2013, "A Fistful of Bitcoins"; Androulaki
et al. 2013) — NOT new magic, but correct and documented implementations
of proven methods, useful for anyone who wants to use them without
reinventing the wheel.

1. Common-Input-Ownership Heuristic (CIOH):
   If several addresses appear as inputs in the same transaction, it is
   very likely they are controlled by the same entity (signing a
   transaction requires the private keys of all inputs).

2. Change-Address Heuristic (simple, optional heuristic):
   If a transaction has exactly one "novel" output (an address that
   appears only once across the whole dataset) and the rest of the
   outputs are already-known/reused addresses, the novel output is a
   candidate "change address", belonging to the same owner as the
   inputs.

These heuristics are NOT infallible (CoinJoin, mixers, and modern
wallets can deliberately evade them) — any result must be treated as a
clue, not a certainty. See docs/methodology.md for limitations.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Iterable, Mapping, Any

from .graph import TransactionGraph


class UnionFind:
    """Simple union-find structure for grouping addresses into clusters."""

    def __init__(self) -> None:
        self.parent: dict[str, str] = {}

    def find(self, x: str) -> str:
        self.parent.setdefault(x, x)
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, a: str, b: str) -> None:
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.parent[ra] = rb

    def groups(self) -> dict[str, set[str]]:
        result: dict[str, set[str]] = defaultdict(set)
        for node in self.parent:
            result[self.find(node)].add(node)
        return dict(result)


def common_input_clustering(transactions: Iterable[Mapping[str, Any]]) -> dict[str, set[str]]:
    """Applies CIOH to a list of raw transactions (not a graph) and returns clusters.

    Returns a dict {cluster_id: {addresses}} — cluster_id is an arbitrary
    representative from within the cluster, not a semantic ID.
    """
    uf = UnionFind()
    for tx in transactions:
        inputs = list(tx.get("inputs", []))
        if len(inputs) < 2:
            # still register the address, so it shows up as its own cluster
            for addr in inputs:
                uf.find(addr)
            continue
        first = inputs[0]
        for other in inputs[1:]:
            uf.union(first, other)
    return uf.groups()


def change_address_candidates(
    transactions: Iterable[Mapping[str, Any]],
) -> dict[str, str]:
    """Identifies, for each eligible transaction, the change-address
    candidate. Returns {txid: candidate_address}.

    Eligibility: the transaction has >=2 outputs, of which exactly one is
    a "novel" address (has not appeared as an output in any other
    transaction in the dataset), and the rest of the outputs are
    already-seen addresses.
    """
    transactions = list(transactions)
    output_seen_count: dict[str, int] = defaultdict(int)
    for tx in transactions:
        for addr in tx.get("outputs", []):
            output_seen_count[addr] += 1

    candidates: dict[str, str] = {}
    for tx in transactions:
        outputs = tx.get("outputs", [])
        if len(outputs) < 2:
            continue
        novel = [a for a in outputs if output_seen_count[a] == 1]
        if len(novel) == 1:
            candidates[tx["txid"]] = novel[0]
    return candidates


def cluster_summary(graph: TransactionGraph, clusters: Mapping[str, set[str]]) -> list[dict[str, Any]]:
    """Generates a per-cluster summary: number of addresses, total in/out volume."""
    summary = []
    for cluster_id, addresses in clusters.items():
        total_in = sum(graph.total_in(a) for a in addresses)
        total_out = sum(graph.total_out(a) for a in addresses)
        summary.append(
            {
                "cluster_id": cluster_id,
                "size": len(addresses),
                "addresses": sorted(addresses),
                "total_in": round(total_in, 8),
                "total_out": round(total_out, 8),
            }
        )
    summary.sort(key=lambda c: c["size"], reverse=True)
    return summary
