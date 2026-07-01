"""
risk_scoring.py
----------------
RULE-BASED, explainable and auditable risk-scoring engine.

We do not use a "black box" model — every point of score comes with an
attached explanation. This is a deliberate decision: in a domain with
real legal impact (AML/fraud), an unexplainable score is useless and
potentially dangerous. If you want scoring based on ML trained on your
own data, this module offers `RiskFactor` as an interface you can
extend with your own signals.

The final score is normalized 0-100. Suggested thresholds (configurable):
  0-29   : low risk
  30-59  : moderate risk — manual review recommended
  60-100 : high risk — priority investigation recommended

WARNING: this score does NOT constitute legal proof of illicit
activity. It is a prioritization tool for analysts, not a verdict.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .graph import TransactionGraph
from .patterns import PatternMatch, run_all_detectors

# default weights per pattern type — can be overridden by the user
DEFAULT_WEIGHTS: dict[str, float] = {
    "fan_out": 15.0,
    "fan_in": 15.0,
    "rapid_passthrough": 25.0,
    "peeling_chain": 30.0,
    "known_blacklist": 100.0,  # see blacklist_match() below
    "mixer_proximity": 20.0,
}


@dataclass
class RiskFactor:
    name: str
    contribution: float
    explanation: str


@dataclass
class RiskScore:
    address: str
    score: float
    risk_level: str
    factors: list[RiskFactor] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "address": self.address,
            "score": self.score,
            "risk_level": self.risk_level,
            "factors": [
                {"name": f.name, "contribution": f.contribution, "explanation": f.explanation}
                for f in self.factors
            ],
        }


def _risk_level(score: float) -> str:
    if score >= 60:
        return "high"
    if score >= 30:
        return "moderate"
    return "low"


def blacklist_match(address: str, blacklist: set[str]) -> bool:
    return address in blacklist


def score_addresses(
    graph: TransactionGraph,
    blacklist: set[str] | None = None,
    weights: dict[str, float] | None = None,
    detector_kwargs: dict[str, Any] | None = None,
) -> dict[str, RiskScore]:
    """Computes a RiskScore per address in the graph.

    blacklist: set of addresses known to be associated with
               fraud/sanctions (e.g. imported from OFI or from public
               OFAC/DNSC lists).
    """
    weights = weights or DEFAULT_WEIGHTS
    blacklist = blacklist or set()
    detector_kwargs = detector_kwargs or {}

    matches: list[PatternMatch] = run_all_detectors(graph, **detector_kwargs)
    matches_by_address: dict[str, list[PatternMatch]] = {}
    for m in matches:
        matches_by_address.setdefault(m.address, []).append(m)

    scores: dict[str, RiskScore] = {}

    for address in graph.graph.nodes:
        factors: list[RiskFactor] = []
        raw_total = 0.0

        for m in matches_by_address.get(address, []):
            weight = weights.get(m.pattern, 10.0)
            contribution = round(weight * m.score, 2)
            raw_total += contribution
            factors.append(
                RiskFactor(
                    name=m.pattern,
                    contribution=contribution,
                    explanation=_explain_pattern(m),
                )
            )

        if blacklist_match(address, blacklist):
            contribution = weights.get("known_blacklist", 100.0)
            raw_total += contribution
            factors.append(
                RiskFactor(
                    name="known_blacklist",
                    contribution=contribution,
                    explanation="The address appears on a list of addresses known to be associated with fraud/sanctions.",
                )
            )

        # addresses directly connected (1 hop) to a blacklisted address get
        # a "proximity" signal — funds that transited close to a source
        # known to be risky
        if blacklist and not blacklist_match(address, blacklist):
            neighbors = graph.address_neighbors(address, "both")
            if neighbors & blacklist:
                contribution = weights.get("mixer_proximity", 20.0)
                raw_total += contribution
                factors.append(
                    RiskFactor(
                        name="mixer_proximity",
                        contribution=contribution,
                        explanation="The address interacted directly (1 hop) with a blacklisted address.",
                    )
                )

        score = round(min(100.0, raw_total), 2)
        scores[address] = RiskScore(
            address=address,
            score=score,
            risk_level=_risk_level(score),
            factors=factors,
        )

    return scores


def _explain_pattern(match: PatternMatch) -> str:
    explanations = {
        "fan_out": f"The address sent funds to {match.details.get('distinct_recipients')} distinct addresses — possible distribution/smurfing.",
        "fan_in": f"The address received funds from {match.details.get('distinct_senders')} distinct addresses — possible pre-cash-out aggregation.",
        "rapid_passthrough": f"The address forwarded {round((1 - match.details.get('retained_ratio', 0)) * 100, 1)}% of the funds in {match.details.get('seconds_between')}s — possible automated layering.",
        "peeling_chain": f"The address is the starting point of a {match.details.get('chain_length')}-step chain with gradual peeling — a classic fund-obfuscation pattern.",
    }
    return explanations.get(match.pattern, f"Pattern detected: {match.pattern}")


def top_risk_addresses(scores: dict[str, RiskScore], n: int = 20) -> list[RiskScore]:
    return sorted(scores.values(), key=lambda s: s.score, reverse=True)[:n]
