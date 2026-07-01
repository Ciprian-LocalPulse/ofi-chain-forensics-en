# Changelog

All notable changes to this project are documented in this file. The
format roughly follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and versioning follows [Semantic Versioning](https://semver.org/).

## [0.1.0] - 2026-06-30

### Added
- Transaction graph construction (`TransactionGraph`), with support for
  explicit per-output amounts or a simplified even split.
- Address clustering via the Common-Input-Ownership Heuristic (CIOH) and
  change-address candidate detection.
- Four suspicious-pattern detectors: peeling chain, fan-out, fan-in,
  rapid pass-through.
- Rule-based, explainable risk-scoring engine (every point of score
  comes with a natural-language explanation).
- CSV, JSON, and OFI-compatible export (`export_ofi_compatible`).
- Functional CLI (`python -m ofi_chain_forensics.cli`).
- 21 unit tests, covering all core modules.
- Documentation: README, `docs/methodology.md`, `docs/data_sources.md`,
  `CONTRIBUTING.md`.
- Synthetic sample data (`data/sample/`) and a generator script
  (`examples/generate_sample_data.py`).

[0.1.0]: https://github.com/Ciprian-LocalPulse/ofi-chain-forensics/releases/tag/v0.1.0
