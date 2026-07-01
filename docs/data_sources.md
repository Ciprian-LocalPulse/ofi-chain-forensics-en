# Data sources

`ofi-chain-forensics` does not include connectors to live blockchains —
deliberately, in order to remain a pure analysis library, without
dependencies on external APIs, keys, or rate limits imposed by third
parties.

Below are real options for obtaining transactions and normalizing them
to the expected format (see `ofi_chain_forensics/graph.py` for the
exact schema).

## Bitcoin / UTXO-based chains

- **Bitcoin Core (your own node)** — `getrawtransaction` +
  `decoderawtransaction` via RPC, for full control and no dependency on
  third-party services.
- **Blockstream Esplora API** (`https://blockstream.info/api/`) — a
  public, free API, no authentication needed for basic queries.
- **Mempool.space API** — a similar, open-source alternative.

## Ethereum / EVM-compatible chains

- **Etherscan API** (requires a free key) — `txlist` per address.
- **Your own node (Geth/Erigon) + `eth_getTransactionByHash`** — for
  full control.
- Note: on EVM, the concept of "input/output" differs from UTXO — for
  simple transactions, input = the `from` address, output = the `to`
  address. For contracts and DeFi (swaps, multi-hop), normalization
  requires parsing events (logs), not just the transaction's base
  fields.

## Normalization

Regardless of the source, transform each transaction into the format:

```json
{
  "txid": "...",
  "timestamp": 1700000000,
  "inputs": ["address1", "address2"],
  "outputs": [
    {"address": "address3", "amount": 0.5},
    {"address": "address4", "amount": 1.2}
  ],
  "fee": 0.0001
}
```

Use the format with explicit per-output amounts whenever your data
source provides them — ratio-sensitive detectors (peeling chain) are
much more accurate with exact amounts than with an assumed even split.

## Contributions welcome

If you build a connector for a specific data source (Etherscan,
Blockstream, your own node, etc.), a PR adding a `connectors/` module
is welcome — see `CONTRIBUTING.md`.
