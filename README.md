# ofi-chain-forensics — English version

🇷🇴 [Versiunea în română este aici](../ofi-chain-forensics-ro/README.md)

Open-source Python library for **blockchain fraud and money-laundering
detection**, through structural analysis of the transaction graph
(addresses, flows, patterns). Complementary module to the
[Open Fraud Intelligence (OFI)](https://github.com/Ciprian-LocalPulse/open-fraud-intelligence)
project.

**100% free, MIT licensed, no account, no API key, no usage limits.**

## Why it exists

Most "blockchain forensics" tools are either closed commercial products
(Chainalysis, Elliptic — inaccessible to independent researchers,
NGOs, or investigative journalists without a budget), or isolated,
undocumented, untested scripts. This project implements the
well-established heuristics from the research literature (cited
explicitly in [docs/methodology.md](docs/methodology.md)) as a clean,
tested, auditable library, usable by anyone.

**Important — read before using the results**: no score produced here
IS legal proof of fraud. It is a prioritization tool for human
analysts. Full details on limitations and known false-positive rates:
[docs/methodology.md](docs/methodology.md).

## What it does

- **Builds a transaction graph** from a normalized list of transactions
  (`ofi_chain_forensics.graph.TransactionGraph`).
- **Address clustering** via the Common-Input-Ownership Heuristic and
  change-address detection (`ofi_chain_forensics.clustering`).
- **Suspicious pattern detectors**: peeling chain, fan-out, fan-in,
  rapid pass-through (`ofi_chain_forensics.patterns`).
- **Explainable risk scoring**, based on transparent rules — every point
  of score comes with a natural-language explanation
  (`ofi_chain_forensics.risk_scoring`).
- **Export** to CSV, JSON, and a format directly compatible with the OFI
  dataset (`ofi_chain_forensics.export`).
- **Functional CLI**, ready to use from the command line.

## Installation

```bash
git clone https://github.com/Ciprian-LocalPulse/ofi-chain-forensics.git
cd ofi-chain-forensics
pip install -r requirements.txt
```

Or as an editable package:

```bash
pip install -e .
```

## Quick usage — CLI

```bash
python -m ofi_chain_forensics.cli data/sample/sample_transactions.json \
    --blacklist data/sample/sample_blacklist.txt \
    --show-clusters \
    --out-csv results.csv \
    --out-json results.json \
    --top 15
```

Output:

```
Graph built: 88 addresses, 42 transactions.

Top 15 addresses by risk score:
Address                                          Score  Level
----------------------------------------------------------------------
CASHOUT0003                                    100.00  high
CASHOUT0005                                    100.00  high
PEEL0003                                         45.00  moderate
...
```

## Quick usage — as a library

```python
from ofi_chain_forensics import TransactionGraph, score_addresses, top_risk_addresses

graph = TransactionGraph.from_transactions(my_transactions)
scores = score_addresses(graph, blacklist=my_known_bad_addresses)

for s in top_risk_addresses(scores, n=10):
    print(s.address, s.score, s.risk_level)
```

See [examples/basic_usage.py](examples/basic_usage.py) for a full,
directly runnable example.

## Expected data format

```json
{
  "txid": "abc123",
  "timestamp": 1700000000,
  "inputs": ["source_address_1", "source_address_2"],
  "outputs": [
    {"address": "dest_address_1", "amount": 0.5},
    {"address": "dest_address_2", "amount": 1.2}
  ],
  "fee": 0.0001
}
```

The library does not connect to any live blockchain — it works on
already-extracted, normalized data, regardless of source (Bitcoin,
Ethereum, any other network). Guide for obtaining and normalizing real
data: [docs/data_sources.md](docs/data_sources.md).

## Running tests

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

21 tests, covering every module (graph, clustering, pattern detectors,
scoring).

## Integration with OFI

The `export_ofi_compatible()` function produces input directly
compatible with the structure of the
[Open Fraud Intelligence](https://github.com/Ciprian-LocalPulse/open-fraud-intelligence)
dataset, so high-risk addresses can be imported as alerts/indicators
into the OFI ecosystem (compatible with OpenCTI/MISP via the existing
OFI SDK).

## Limitations — in brief

- Does not identify real-world identities, only addresses.
- Does not detect advanced obfuscation (CoinJoin, good mixers, privacy
  coins).
- Rule-based scoring, not trained ML — predictable and auditable, but
  does not "learn" from new data automatically.
- Results always require human review.

Full details: [docs/methodology.md](docs/methodology.md).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Connectors for real data
sources (Etherscan, Blockstream, your own nodes) are especially
welcome.

## License

MIT — see [LICENSE](LICENSE). Free for any use, commercial or
non-commercial, with no conditions other than preserving the copyright
notice.

## Support

This project is developed and maintained independently, without
institutional funding. If it has saved you hours of searching, taught
you something, or you simply want to back independent open-access
research and keep this project free for everyone, you can contribute
directly through any of the channels below.

<div align="center">

<table>
<tr><td colspan="2">

### 🇪🇺 European Payment — SEPA / EUR <sub>· CEA · AES-256</sub>

| Field | Detail |
|---|---|
| Recipient | Ciprian Stefan Plesca |
| IBAN | `BE83 9679 1975 8915` |
| SWIFT / BIC | `TRWIBEB1XXX` |
| Bank | Wise, Rue du Trône 100, 3rd floor, Brussels, 1050, Belgium |

</td></tr>
<tr><td colspan="2">

### 🇬🇧 United Kingdom Payment — Faster Payments / GBP <sub>· AIA · SHA-3</sub>

| Field | Detail |
|---|---|
| Recipient | Ciprian Stefan Plesca |
| Account number | `92055372` |
| Sort code | `23-14-70` |
| IBAN | `GB68 TRWI 2314 7092 0553 72` |
| SWIFT / BIC | `TRWIGB2LXXX` |
| Bank | Wise Payments Limited, 1st Floor, Worship Square, 65 Clifton Street, London, EC2A 4JE, United Kingdom |

</td></tr>
<tr><td colspan="2">

### 🇺🇸 United States Payment — ACH / Wire / USD <sub>· ICA · RSA-4096</sub>

| Field | Detail |
|---|---|
| Recipient | Ciprian Stefan Plesca |
| Account type | Checking |
| Routing number | `026073150` |
| Account number | `8314225367` |
| SWIFT / BIC | `CMFGUS33` |
| Bank | Community Federal Savings Bank, 89-16 Jamaica Ave, Woodhaven, NY, 11421, United States |

</td></tr>
</table>

</div>

<div align="center">

| ₿ Bitcoin (BTC) | Ξ Ethereum (ETH) | PP PayPal |
|---|---|---|
| `bc1qf3yy0w8z37rwavxpu38wem3yffpanw7wzj32qj` | `0x27d9a6a5b8507e6031bb044319410da96222d402` | [paypal.me/agentflowenterprise](https://paypal.me/agentflowenterprise) |

</div>
