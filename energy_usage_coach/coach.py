from __future__ import annotations

from dataclasses import asdict

from .gemini_client import Recommender
from .guardrails import GuardrailValidator
from .models import RecommendationResult
from .tavily_client import GuidelinesRetriever


class EnergyUsageCoach:
    def __init__(
        self,
        *,
        guidelines_retriever: GuidelinesRetriever,
        recommender: Recommender,
        guardrail_validator: GuardrailValidator | None = None,
    ) -> None:
        self.guidelines_retriever = guidelines_retriever
        self.recommender = recommender
        self.guardrail_validator = guardrail_validator or GuardrailValidator()

    def forecast_and_recommend(
        self,
        *,
        topic: str,
        context: str,
        historical_usage_kwh: list[float],
    ) -> RecommendationResult:
        guidelines = self.guidelines_retriever.fetch_guidelines(topic)
        result = self.recommender.generate_recommendations(
            historical_usage_kwh=historical_usage_kwh,
            context=context,
            guidelines=guidelines,
        )
        self.guardrail_validator.validate(result)
        result.metadata = {
            "guideline_count": len(guidelines),
            "guidelines": [asdict(g) for g in guidelines],
        }
        return result
