"""
graph.py
--------
Builds a directed graph of blockchain transactions (addresses = nodes,
transactions = weighted edges) from a list of normalized transactions.

Minimal expected format per transaction (dict or pandas.Series):
    {
        "txid": str,
        "timestamp": int (unix epoch, seconds),
        "inputs": list[str]   -> addresses sending funds (can be several)
        "outputs": list[str]  -> addresses receiving funds (can be several)
        "amount": float       -> total amount transferred (in the chosen unit, e.g. BTC/ETH/token)
        "fee": float          -> fee (optional, default 0.0)
    }

We make no assumption about the source network (Bitcoin, Ethereum, etc.) —
the SDK works on already-normalized data. Connectors for extracting raw
data from an explorer/node are the responsibility of the user or of a
separate `connectors/` module (see docs/data_sources.md).
"""

from __future__ import annotations

import networkx as nx
from typing import Iterable, Mapping, Any


class TransactionGraph:
    """Wrapper around a networkx.MultiDiGraph specialized for AML analysis."""

    def __init__(self) -> None:
        self.graph = nx.MultiDiGraph()
        self._tx_count = 0

    @classmethod
    def from_transactions(cls, transactions: Iterable[Mapping[str, Any]]) -> "TransactionGraph":
        tg = cls()
        for tx in transactions:
            tg.add_transaction(tx)
        return tg

    def add_transaction(self, tx: Mapping[str, Any]) -> None:
        """Adds a transaction to the graph.

        `outputs` can be in two formats:
          - a list of addresses (str): the total amount is split evenly
            across each input->output pair (simplification used when exact
            per-output amounts are not available).
          - a list of dicts {"address": str, "amount": float}: exact
            amounts are used directly (recommended — needed for
            ratio-sensitive detectors, e.g. peeling chain).
        """
        txid = tx["txid"]
        inputs = tx.get("inputs", [])
        outputs = tx.get("outputs", [])
        amount = float(tx.get("amount", 0.0))
        fee = float(tx.get("fee", 0.0))
        timestamp = tx.get("timestamp")

        if not inputs or not outputs:
            raise ValueError(f"Transaction {txid} must have at least one input and one output.")

        explicit_outputs = isinstance(outputs[0], Mapping)

        if explicit_outputs:
            output_pairs = [(o["address"], float(o["amount"])) for o in outputs]
        else:
            n_pairs = len(outputs)
            per_output_amount = amount / n_pairs if n_pairs else 0.0
            output_pairs = [(addr, per_output_amount) for addr in outputs]

        n_inputs = len(inputs)
        for src in inputs:
            for dst, out_amount in output_pairs:
                self.graph.add_edge(
                    src,
                    dst,
                    key=f"{txid}:{dst}",
                    txid=txid,
                    amount=out_amount / n_inputs if n_inputs else out_amount,
                    fee=fee / (n_inputs * len(output_pairs)) if n_inputs and output_pairs else 0.0,
                    timestamp=timestamp,
                )

        self._tx_count += 1

    @property
    def num_transactions(self) -> int:
        return self._tx_count

    @property
    def num_addresses(self) -> int:
        return self.graph.number_of_nodes()

    def address_neighbors(self, address: str, direction: str = "both") -> set[str]:
        """Returns the direct (1-hop) neighboring addresses of an address."""
        if direction not in {"in", "out", "both"}:
            raise ValueError("direction must be 'in', 'out' or 'both'")
        neighbors: set[str] = set()
        if direction in ("out", "both"):
            neighbors.update(self.graph.successors(address))
        if direction in ("in", "both"):
            neighbors.update(self.graph.predecessors(address))
        return neighbors

    def subgraph_within_hops(self, address: str, hops: int = 2) -> nx.MultiDiGraph:
        """Extracts the subgraph of all addresses within `hops` distance of `address`."""
        nodes = {address}
        frontier = {address}
        for _ in range(hops):
            next_frontier: set[str] = set()
            for node in frontier:
                next_frontier.update(self.address_neighbors(node, "both"))
            next_frontier -= nodes
            nodes.update(next_frontier)
            frontier = next_frontier
        return self.graph.subgraph(nodes).copy()

    def total_in(self, address: str) -> float:
        return sum(d.get("amount", 0.0) for _, _, d in self.graph.in_edges(address, data=True))

    def total_out(self, address: str) -> float:
        return sum(d.get("amount", 0.0) for _, _, d in self.graph.out_edges(address, data=True))
