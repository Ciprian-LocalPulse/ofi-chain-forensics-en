from ofi_chain_forensics.graph import TransactionGraph
from ofi_chain_forensics.patterns import (
    detect_fan_out,
    detect_fan_in,
    detect_rapid_passthrough,
    detect_peeling_chain,
)


def test_detect_fan_out_triggers_above_threshold():
    txs = [{
        "txid": "t1", "timestamp": 1, "inputs": ["SRC"],
        "outputs": [f"T{i}" for i in range(12)], "amount": 12.0
    }]
    g = TransactionGraph.from_transactions(txs)
    matches = detect_fan_out(g, threshold=10)
    addresses = {m.address for m in matches}
    assert "SRC" in addresses


def test_detect_fan_out_does_not_trigger_below_threshold():
    txs = [{
        "txid": "t1", "timestamp": 1, "inputs": ["SRC"],
        "outputs": ["T1", "T2"], "amount": 2.0
    }]
    g = TransactionGraph.from_transactions(txs)
    matches = detect_fan_out(g, threshold=10)
    assert all(m.address != "SRC" for m in matches)


def test_detect_fan_in_triggers():
    txs = [
        {"txid": f"t{i}", "timestamp": i, "inputs": [f"S{i}"], "outputs": ["DST"], "amount": 1.0}
        for i in range(11)
    ]
    g = TransactionGraph.from_transactions(txs)
    matches = detect_fan_in(g, threshold=10)
    addresses = {m.address for m in matches}
    assert "DST" in addresses


def test_detect_rapid_passthrough():
    txs = [
        {"txid": "t1", "timestamp": 1000, "inputs": ["IN"], "outputs": ["MID"], "amount": 10.0},
        {"txid": "t2", "timestamp": 1200, "inputs": ["MID"], "outputs": ["OUT"], "amount": 9.9},
    ]
    g = TransactionGraph.from_transactions(txs)
    matches = detect_rapid_passthrough(g, min_retained_ratio_below=0.05, max_seconds_between=3600)
    addresses = {m.address for m in matches}
    assert "MID" in addresses


def test_detect_rapid_passthrough_ignores_retained_funds():
    txs = [
        {"txid": "t1", "timestamp": 1000, "inputs": ["IN"], "outputs": ["MID"], "amount": 10.0},
        {"txid": "t2", "timestamp": 1200, "inputs": ["MID"], "outputs": ["OUT"], "amount": 2.0},
    ]
    g = TransactionGraph.from_transactions(txs)
    matches = detect_rapid_passthrough(g, min_retained_ratio_below=0.05, max_seconds_between=3600)
    addresses = {m.address for m in matches}
    assert "MID" not in addresses


def test_detect_peeling_chain():
    txs = []
    current = "START"
    amount = 100.0
    ts = 0
    for i in range(6):
        peel = round(amount * 0.05, 6)
        remainder = round(amount - peel, 6)
        nxt = f"STEP{i}"
        txs.append({
            "txid": f"t{i}", "timestamp": ts, "inputs": [current],
            "outputs": [
                {"address": f"PEELED{i}", "amount": peel},
                {"address": nxt, "amount": remainder},
            ],
        })
        current = nxt
        amount = remainder
        ts += 100

    g = TransactionGraph.from_transactions(txs)
    matches = detect_peeling_chain(g, min_chain_length=3, peel_ratio_max=0.6)
    assert len(matches) >= 1
