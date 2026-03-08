# energy-usage-coach

Forecast energy usage and generate safe, evidence-backed recommendations.

## What this does

1. Uses **Tavily** to retrieve relevant energy-efficiency guidelines.
2. Uses **Gemini** to forecast usage and generate recommendations that include:
   - Explicit citations
   - Safety guardrails
   - Uncertainty disclosure
3. Runs a **guardrail validator** that rejects unsafe advice.

## Install

```bash
pip install -e .[integrations,dev]
```

## Environment

```bash
export TAVILY_API_KEY=...
export GEMINI_API_KEY=...
```

## Run

```bash
python -m energy_usage_coach.cli \
  --topic "single-family home in hot climate" \
  --context "home built in 1998; electric resistance water heater; TOU tariff" \
  --usage "820,790,760,710,680,720,810,880,900,860,830,800"
```

## Guardrails

The validator rejects recommendations if they:
- Include known unsafe advice (meter tampering, bypassing breakers/fuses, disabling alarms, unsafe DIY panel rewiring)
- Omit citations
- Omit safety guardrails
- Omit uncertainty disclosure

## Tests

```bash
pytest -q
```
