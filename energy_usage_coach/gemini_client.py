from __future__ import annotations

import json
import os
from typing import Protocol

from .models import Guideline, RecommendationResult


class Recommender(Protocol):
    def generate_recommendations(
        self,
        *,
        historical_usage_kwh: list[float],
        context: str,
        guidelines: list[Guideline],
    ) -> RecommendationResult:
        ...


class GeminiRecommender:
    """Generate recommendation payloads with Gemini in strict JSON format."""

    def __init__(self, api_key: str | None = None, model: str = "gemini-1.5-pro") -> None:
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model = model
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is required for GeminiRecommender")

    def generate_recommendations(
        self,
        *,
        historical_usage_kwh: list[float],
        context: str,
        guidelines: list[Guideline],
    ) -> RecommendationResult:
        try:
            from google import genai
        except ImportError as exc:
            raise RuntimeError(
                "google-genai is not installed. Install with `pip install .[integrations]`."
            ) from exc

        prompt = self._build_prompt(
            historical_usage_kwh=historical_usage_kwh,
            context=context,
            guidelines=guidelines,
        )
        client = genai.Client(api_key=self.api_key)
        response = client.models.generate_content(model=self.model, contents=prompt)
        payload = json.loads(response.text)

        required = {
            "usage_forecast_kwh",
            "forecast_confidence",
            "recommendations",
            "citations",
            "safety_guardrails",
            "uncertainty_disclosure",
        }
        missing = required.difference(payload.keys())
        if missing:
            raise ValueError(f"Gemini response missing required keys: {sorted(missing)}")

        return RecommendationResult(**{k: payload[k] for k in required})

    def _build_prompt(
        self,
        *,
        historical_usage_kwh: list[float],
        context: str,
        guidelines: list[Guideline],
    ) -> str:
        guideline_lines = [
            f"- {g.title} | {g.url} | {g.snippet[:300]}" for g in guidelines
        ]

        return (
            "You are an energy advisor. Return ONLY valid JSON with keys: "
            "usage_forecast_kwh, forecast_confidence, recommendations, citations, "
            "safety_guardrails, uncertainty_disclosure.\n"
            "Requirements:\n"
            "1) Recommendations must be evidence-backed and map to citations.\n"
            "2) Include explicit safety guardrails for electrical/HVAC actions.\n"
            "3) Include an uncertainty disclosure with assumptions and limits.\n"
            "4) Do not provide unsafe advice or code violations.\n\n"
            f"Historical monthly usage (kWh): {historical_usage_kwh}\n"
            f"Context: {context}\n"
            "Guidelines:\n"
            + "\n".join(guideline_lines)
        )
