import json, random

random.seed(42)
txs = []
ts = 1_700_000_000

def addr(prefix, i):
    return f"{prefix}{i:04d}"

txid_counter = 0
def next_txid():
    global txid_counter
    txid_counter += 1
    return f"tx{txid_counter:05d}"

# 1. Realistic peeling chain, with explicit per-output amounts (correct, not evenly split)
current = addr("PEEL", 0)
amount = 50.0
for i in range(6):
    peel_target = addr("CASHOUT", i)
    peel_amt = round(amount * 0.08, 6)
    next_addr = addr("PEEL", i + 1)
    remainder = round(amount - peel_amt, 6)
    txs.append({
        "txid": next_txid(), "timestamp": ts, "inputs": [current],
        "outputs": [
            {"address": peel_target, "amount": peel_amt},
            {"address": next_addr, "amount": remainder},
        ],
    })
    ts += random.randint(600, 1800)
    current = next_addr
    amount = remainder

# 2. Fan-out: one address sends to 14 new addresses (possible smurfing)
fanout_src = addr("FANOUT", 0)
fanout_targets = [addr("FOUT", i) for i in range(14)]
txs.append({
    "txid": next_txid(), "timestamp": ts, "inputs": [fanout_src],
    "outputs": fanout_targets, "amount": 28.0, "fee": 0.0005
})
ts += 900

# 3. Fan-in: 12 addresses send to a single aggregation address
fanin_dst = addr("AGG", 0)
fanin_sources = [addr("FIN", i) for i in range(12)]
for s in fanin_sources:
    txs.append({
        "txid": next_txid(), "timestamp": ts, "inputs": [s],
        "outputs": [fanin_dst], "amount": round(random.uniform(0.5, 2.0), 4), "fee": 0.0001
    })
    ts += random.randint(60, 300)

# 4. Rapid pass-through: address receives and forwards almost everything in <1h
rp_in = addr("RPIN", 0)
rp_mid = addr("RPMID", 0)
rp_out = addr("RPOUT", 0)
t0 = ts
txs.append({"txid": next_txid(), "timestamp": t0, "inputs": [rp_in], "outputs": [rp_mid], "amount": 10.0, "fee": 0.0002})
txs.append({"txid": next_txid(), "timestamp": t0 + 300, "inputs": [rp_mid], "outputs": [rp_out], "amount": 9.85, "fee": 0.0002})
ts = t0 + 1000

# 5. Common-input-ownership: a transaction with 3 shared inputs (likely same owner)
cioh_inputs = [addr("WALLET", i) for i in range(3)]
txs.append({
    "txid": next_txid(), "timestamp": ts, "inputs": cioh_inputs,
    "outputs": [addr("MERCHANT", 0)], "amount": 4.2, "fee": 0.0001
})
ts += 500

# 6. "Normal" background traffic
for i in range(20):
    a = addr("NORM", i)
    b = addr("NORM", i + 100)
    txs.append({
        "txid": next_txid(), "timestamp": ts, "inputs": [a],
        "outputs": [b], "amount": round(random.uniform(0.01, 1.5), 4), "fee": 0.0001
    })
    ts += random.randint(1000, 50000)

with open("data/sample/sample_transactions.json", "w", encoding="utf-8") as f:
    json.dump(txs, f, indent=2)

print(f"Generated {len(txs)} synthetic transactions.")

with open("data/sample/sample_blacklist.txt", "w", encoding="utf-8") as f:
    f.write("CASHOUT0003\nCASHOUT0005\n")

print("Sample blacklist generated.")
