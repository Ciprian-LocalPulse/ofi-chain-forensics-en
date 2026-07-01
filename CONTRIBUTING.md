# How to contribute

Thanks for your interest! A few simple rules, to stay consistent with
the spirit of the project — functional, tested code, no unsupported
claims.

## Ground rules

1. **Any new detection function comes with tests.** We don't accept
   "trust me" detectors — if you claim something detects a pattern,
   show a test that builds that pattern and verifies the detection.
2. **Any methodological claim (citations, false-positive rates) must
   have a verifiable source**, or be explicitly marked as your own
   empirical observation, not as an established fact.
3. **Don't add heavy dependencies without discussion.** The library is
   deliberately kept minimal (currently: only `networkx`).
4. **Code in English; comments/documentation can be in Romanian or
   English** — the project primarily serves the Romanian community, but
   international contributions are welcome.

## How to propose a change

1. Open an issue describing the problem/feature before writing code, if
   it's a significant change (avoids wasted work).
2. Fork + descriptive branch (`feature/etherscan-connector`,
   `fix/peeling-chain-infinite-loop`).
3. Run `pytest tests/ -v` locally — all tests must pass.
4. Open a PR with a clear description of what changed and why.

## Areas where contributions are especially welcome

- **Connectors for real data sources** (Etherscan, Blockstream, your
  own nodes) — see `docs/data_sources.md`.
- **New pattern detectors**, documented with their conceptual source.
- **Support for other networks** (Ethereum/EVM has particularities
  related to contracts and events, not yet covered in depth).
- **Benchmarks on labeled public data** (if public datasets with
  addresses known to be fraudulent exist, validating the detectors
  against them would greatly increase confidence in the results).

## Reporting security issues

If you find a vulnerability (not a regular bug), open an issue clearly
marked `security` or contact the maintainer directly, without
publishing exploitation details in the clear.
