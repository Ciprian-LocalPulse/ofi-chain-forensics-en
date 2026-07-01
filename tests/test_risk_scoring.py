from ofi_chain_forensics.graph import TransactionGraph
from ofi_chain_forensics.risk_scoring import score_addresses, top_risk_addresses


def test_blacklisted_address_gets_max_relevant_score():
    txs = [{"txid": "t1", "timestamp": 1, "inputs": ["A"], "outputs": ["B"], "amount": 1.0}]
    g = TransactionGraph.from_transactions(txs)
    scores = score_addresses(g, blacklist={"B"})
    assert scores["B"].score == 100.0
    assert scores["B"].risk_level == "high"
    assert any(f.name == "known_blacklist" for f in scores["B"].factors)


def test_proximity_to_blacklist_raises_score():
    txs = [{"txid": "t1", "timestamp": 1, "inputs": ["A"], "outputs": ["B"], "amount": 1.0}]
    g = TransactionGraph.from_transactions(txs)
    scores = score_addresses(g, blacklist={"B"})
    assert scores["A"].score > 0
    assert any(f.name == "mixer_proximity" for f in scores["A"].factors)


def test_clean_address_has_low_score():
    txs = [{"txid": "t1", "timestamp": 1, "inputs": ["A"], "outputs": ["B"], "amount": 1.0}]
    g = TransactionGraph.from_transactions(txs)
    scores = score_addresses(g)
    assert scores["A"].score == 0.0
    assert scores["A"].risk_level == "low"


def test_top_risk_addresses_ordering():
    txs = [
        {"txid": "t1", "timestamp": 1, "inputs": ["A"], "outputs": ["B"], "amount": 1.0},
        {"txid": "t2", "timestamp": 2, "inputs": ["C"], "outputs": ["D"], "amount": 1.0},
    ]
    g = TransactionGraph.from_transactions(txs)
    scores = score_addresses(g, blacklist={"D"})
    top = top_risk_addresses(scores, n=2)
    assert top[0].address == "D"
    assert top[0].score >= top[1].score


def test_score_capped_at_100():
    # a blacklisted address plus other patterns must not push the score above 100
    txs = [{
        "txid": "t1", "timestamp": 1, "inputs": ["A"],
        "outputs": [f"T{i}" for i in range(20)], "amount": 20.0
    }]
    g = TransactionGraph.from_transactions(txs)
    scores = score_addresses(g, blacklist={"A"})
    assert scores["A"].score <= 100.0
