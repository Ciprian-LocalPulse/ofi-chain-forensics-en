from ofi_chain_forensics.clustering import (
    common_input_clustering,
    change_address_candidates,
    cluster_summary,
    UnionFind,
)
from ofi_chain_forensics.graph import TransactionGraph


def test_union_find_basic():
    uf = UnionFind()
    uf.union("a", "b")
    uf.union("b", "c")
    assert uf.find("a") == uf.find("c")
    groups = uf.groups()
    assert len(groups) == 1
    assert set(next(iter(groups.values()))) == {"a", "b", "c"}


def test_common_input_clustering_groups_multi_input_tx():
    txs = [
        {"txid": "t1", "inputs": ["A", "B", "C"], "outputs": ["X"], "amount": 1.0},
        {"txid": "t2", "inputs": ["D"], "outputs": ["Y"], "amount": 1.0},
    ]
    clusters = common_input_clustering(txs)
    cluster_sets = list(clusters.values())
    # A, B, C must be in the same cluster
    abc_cluster = next(c for c in cluster_sets if "A" in c)
    assert {"A", "B", "C"}.issubset(abc_cluster)
    # D is alone
    d_cluster = next(c for c in cluster_sets if "D" in c)
    assert d_cluster == {"D"}


def test_change_address_candidates_detects_novel_output():
    txs = [
        {"txid": "t1", "inputs": ["A"], "outputs": ["KNOWN1"], "amount": 5.0},
        {"txid": "t2", "inputs": ["KNOWN1"], "outputs": ["KNOWN1", "NEWADDR"], "amount": 5.0},
    ]
    candidates = change_address_candidates(txs)
    assert candidates.get("t2") == "NEWADDR"


def test_cluster_summary_sorted_by_size():
    txs = [
        {"txid": "t1", "timestamp": 1, "inputs": ["A", "B"], "outputs": ["X"], "amount": 2.0},
        {"txid": "t2", "timestamp": 2, "inputs": ["C"], "outputs": ["Y"], "amount": 1.0},
    ]
    graph = TransactionGraph.from_transactions(txs)
    clusters = common_input_clustering(txs)
    summary = cluster_summary(graph, clusters)
    assert summary[0]["size"] >= summary[-1]["size"]
