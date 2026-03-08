from energy_usage_coach.guardrails import GuardrailValidationError, GuardrailValidator
from energy_usage_coach.models import RecommendationResult


def test_guardrail_validator_allows_safe_payload() -> None:
    result = RecommendationResult(
        usage_forecast_kwh=500.0,
        forecast_confidence="medium",
        recommendations=["Seal duct leaks and tune HVAC annually."],
        citations=["https://www.energy.gov/energysaver"],
        safety_guardrails=["Use licensed electricians for panel work."],
        uncertainty_disclosure="Forecast assumes similar occupancy and weather.",
    )

    GuardrailValidator().validate(result)


def test_guardrail_validator_rejects_unsafe_payload() -> None:
    result = RecommendationResult(
        usage_forecast_kwh=500.0,
        forecast_confidence="low",
        recommendations=["You can bypass breaker trips to avoid outages."],
        citations=[],
        safety_guardrails=[],
        uncertainty_disclosure="",
    )

    try:
        GuardrailValidator().validate(result)
        assert False, "expected GuardrailValidationError"
    except GuardrailValidationError as exc:
        message = str(exc)
        assert "bypass_circuit_breaker" in message
        assert "missing_citations" in message
        assert "missing_safety_guardrails" in message
        assert "missing_uncertainty_disclosure" in message
