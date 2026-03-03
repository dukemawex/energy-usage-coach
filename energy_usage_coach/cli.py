from __future__ import annotations

import argparse
import json

from .coach import EnergyUsageCoach
from .gemini_client import GeminiRecommender
from .tavily_client import TavilyGuidelinesRetriever


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Energy usage coach")
    parser.add_argument("--topic", required=True, help="Building type or scenario")
    parser.add_argument("--context", required=True, help="Local context and constraints")
    parser.add_argument(
        "--usage",
        required=True,
        help="Comma-separated monthly usage values in kWh (e.g., 410,398,450)",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    usage = [float(x.strip()) for x in args.usage.split(",") if x.strip()]

    coach = EnergyUsageCoach(
        guidelines_retriever=TavilyGuidelinesRetriever(),
        recommender=GeminiRecommender(),
    )

    result = coach.forecast_and_recommend(
        topic=args.topic,
        context=args.context,
        historical_usage_kwh=usage,
    )
    print(json.dumps(result.__dict__, indent=2))


if __name__ == "__main__":
    main()
