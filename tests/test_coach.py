from energy_usage_coach.coach import EnergyUsageCoach
from energy_usage_coach.models import Guideline, RecommendationResult


class FakeRetriever:
    def fetch_guidelines(self, topic: str, *, max_results: int = 5) -> list[Guideline]:
        assert topic
        return [
            Guideline(
                title="DOE Home Energy Saver",
                url="https://www.energy.gov/energysaver",
                snippet="General efficiency best practices.",
            )
        ]


class FakeRecommender:
    def generate_recommendations(self, *, historical_usage_kwh, context, guidelines):
        assert historical_usage_kwh
        assert context
        assert guidelines
        return RecommendationResult(
            usage_forecast_kwh=742.5,
            forecast_confidence="medium",
            recommendations=["Install a smart thermostat and optimize setpoints."],
            citations=["https://www.energy.gov/energysaver"],
            safety_guardrails=["Do not open electrical panels unless licensed."],
            uncertainty_disclosure="Actual usage may vary due to weather and occupancy.",
        )


def test_coach_pipeline() -> None:
    coach = EnergyUsageCoach(guidelines_retriever=FakeRetriever(), recommender=FakeRecommender())
    result = coach.forecast_and_recommend(
        topic="single-family home",
        context="hot climate",
        historical_usage_kwh=[700, 710, 680],
    )

    assert result.usage_forecast_kwh == 742.5
    assert result.metadata["guideline_count"] == 1
