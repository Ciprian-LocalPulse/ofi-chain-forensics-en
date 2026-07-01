import pytest
from ofi_chain_forensics.graph import TransactionGraph


def make_simple_tx():
    return [
        {"txid": "t1", "timestamp": 1000, "inputs": ["A"], "outputs": ["B"], "amount": 10.0, "fee": 0.01},
        {"txid": "t2", "timestamp": 1100, "inputs": ["B"], "outputs": ["C"], "amount": 9.5, "fee": 0.01},
    ]


def test_graph_builds_correct_node_count():
    g = TransactionGraph.from_transactions(make_simple_tx())
    assert g.num_addresses == 3
    assert g.num_transactions == 2


def test_total_in_out():
    g = TransactionGraph.from_transactions(make_simple_tx())
    assert g.total_in("B") == pytest.approx(10.0)
    assert g.total_out("B") == pytest.approx(9.5)
    assert g.total_in("A") == 0.0


def test_neighbors():
    g = TransactionGraph.from_transactions(make_simple_tx())
    assert g.address_neighbors("B", "in") == {"A"}
    assert g.address_neighbors("B", "out") == {"C"}
    assert g.address_neighbors("B", "both") == {"A", "C"}


def test_add_transaction_requires_inputs_outputs():
    g = TransactionGraph()
    with pytest.raises(ValueError):
        g.add_transaction({"txid": "bad", "inputs": [], "outputs": ["X"], "amount": 1.0})


def test_amount_split_across_multiple_pairs():
    g = TransactionGraph()
    g.add_transaction({
        "txid": "multi", "timestamp": 1, "inputs": ["A", "B"], "outputs": ["C", "D"], "amount": 4.0
    })
    # 2 inputs x 2 outputs = 4 edges, each worth 1.0
    assert g.total_out("A") == pytest.approx(2.0)
    assert g.total_in("C") == pytest.approx(2.0)


def test_subgraph_within_hops():
    txs = [
        {"txid": "t1", "timestamp": 1, "inputs": ["A"], "outputs": ["B"], "amount": 1.0},
        {"txid": "t2", "timestamp": 2, "inputs": ["B"], "outputs": ["C"], "amount": 1.0},
        {"txid": "t3", "timestamp": 3, "inputs": ["C"], "outputs": ["D"], "amount": 1.0},
    ]
    g = TransactionGraph.from_transactions(txs)
    sub = g.subgraph_within_hops("A", hops=1)
    assert set(sub.nodes) == {"A", "B"}
    sub2 = g.subgraph_within_hops("A", hops=2)
    assert set(sub2.nodes) == {"A", "B", "C"}
