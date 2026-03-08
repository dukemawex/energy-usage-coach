from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Guideline:
    title: str
    url: str
    snippet: str


@dataclass
class RecommendationResult:
    usage_forecast_kwh: float
    forecast_confidence: str
    recommendations: list[str]
    citations: list[str]
    safety_guardrails: list[str]
    uncertainty_disclosure: str
    metadata: dict[str, Any] = field(default_factory=dict)
