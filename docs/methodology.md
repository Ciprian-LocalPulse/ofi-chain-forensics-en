# Methodology and limitations

This document explains exactly what `ofi-chain-forensics` does and does
NOT do, so that anyone using it — analyst, researcher, or developer —
understands the tool's limits before trusting it.

## What the library does

It analyzes the structure of a transaction graph (who sends to whom,
when, how much) and looks for known structural patterns associated in
the research literature with fund obfuscation or money laundering:

- **Common-Input-Ownership Heuristic (CIOH)** — Meiklejohn et al., 2013,
  *"A Fistful of Bitcoins: Characterizing Payments Among Men with No
  Names"*. If several addresses appear as inputs in the same
  transaction, they likely belong to the same wallet/entity.
- **Peeling chain detection** — a pattern documented in multiple
  blockchain forensics studies (e.g. Chainalysis, Elliptic — public
  reports), where a large amount is gradually "peeled off" through
  successive transactions.
- **Fan-out / Fan-in** — generic structural signals of unusual
  distribution or aggregation of funds.
- **Rapid pass-through** — addresses that act as a fast "hop", typical
  of automated layering.

## What the library does NOT do

- **It does not identify real-world identities.** Everything it
  produces is addresses and risk scores — no names, no people, no legal
  entities.
- **It is not legal proof.** A high risk score is a signal for further
  investigation, not a conclusion. Using the results as the sole basis
  for accusations or decisions with legal impact is a misuse of the
  tool.
- **It does not detect everything.** Modern obfuscation techniques —
  CoinJoin, well-implemented mixers, cross-chain swaps, privacy coins
  (Monero, Zcash in shielded mode) — can deliberately evade these
  heuristics. The absence of a signal does NOT mean the absence of
  fraud.
- **It does not connect automatically to live blockchains.** The
  library works on already-extracted, normalized data. Connecting to an
  explorer/node (Bitcoin Core, Etherscan API, etc.) is the user's
  responsibility — see `docs/data_sources.md` for suggestions.
- **It does not use trained machine learning.** Scoring is based on
  explicit, weighted rules, precisely so it stays auditable. If you
  need ML, the `risk_scoring.py` module offers an interface
  (`RiskFactor`) that is easy to extend with your own signals.

## Known false-positive rates

- **Fan-out/Fan-in**: legitimate exchanges (payment processors, crypto
  payroll services) naturally generate high fan-out/fan-in. The default
  thresholds (10) are conservative, but can still flag completely
  legitimate activity.
- **Peeling chain**: wallets that perform automatic UTXO rebalancing can
  produce similar patterns without any intent to obfuscate.
- **Rapid pass-through**: legitimate swap/bridge services (DEXs,
  cross-chain bridges) behave exactly this way by design.

**Practical conclusion**: any score produced by this library must be
interpreted by a human analyst, in context, never automatically as a
"verdict".

## References

- Meiklejohn, S. et al. (2013). *A Fistful of Bitcoins: Characterizing
  Payments Among Men with No Names.* IMC '13.
- Androulaki, E. et al. (2013). *Evaluating User Privacy in Bitcoin.*
  Financial Cryptography and Data Security.
- Chainalysis & Elliptic — annual public crime reports (terminology and
  structural patterns generally accepted across the industry).
