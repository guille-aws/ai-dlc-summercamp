"""Routing Evaluator: decides auto-adjudicate vs human review (OR-5..OR-8)."""

from __future__ import annotations

from dataclasses import dataclass

from clairo_shared.config import ConfigProvider
from clairo_shared.models import DecisionOutcome, PreliminaryDecision


@dataclass
class RoutingDecision:
    route: str  # "auto" or "human"
    threshold_used: float


class RoutingEvaluator:
    def __init__(self, config: ConfigProvider = None):
        self.config = config or ConfigProvider()

    def evaluate(self, decision: PreliminaryDecision) -> RoutingDecision:
        """Return a RoutingDecision. Reads threshold fresh (OR-5)."""
        threshold, error = self.config.get_threshold()
        if error or threshold is None:
            threshold = 0.8  # safe default if config unavailable

        # needs_more_info always routes to human (OR-7 / BR-15).
        if decision.outcome == DecisionOutcome.NEEDS_MORE_INFO:
            return RoutingDecision(route="human", threshold_used=threshold)

        if decision.confidence >= threshold:
            return RoutingDecision(route="auto", threshold_used=threshold)
        return RoutingDecision(route="human", threshold_used=threshold)
