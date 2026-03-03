from __future__ import annotations

from dataclasses import dataclass

from .models import RecommendationResult


UNSAFE_PATTERNS = {
    "bypass_circuit_breaker": "Advice must never recommend bypassing breakers, fuses, or safety cutoffs.",
    "disable_smoke_detector": "Advice must never recommend disabling fire/smoke alarms.",
    "tamper_meter": "Advice must never suggest tampering with utility meters.",
    "unlicensed_electrical_work": "Advice must not encourage dangerous electrical modifications by unlicensed people.",
}

TRIGGER_TERMS = {
    "bypass_circuit_breaker": ["bypass breaker", "remove fuse", "override circuit breaker"],
    "disable_smoke_detector": ["disable smoke detector", "remove smoke alarm battery"],
    "tamper_meter": ["tamper with meter", "bypass utility meter", "slow meter"],
    "unlicensed_electrical_work": ["rewire your panel yourself", "modify service entrance", "unsafe diy wiring"],
}


@dataclass
class GuardrailViolation:
    rule_id: str
    message: str
    matched_text: str


class GuardrailValidationError(ValueError):
    def __init__(self, violations: list[GuardrailViolation]) -> None:
        details = "; ".join(
            f"{violation.rule_id}: {violation.message} (matched: '{violation.matched_text}')"
            for violation in violations
        )
        super().__init__(f"Unsafe recommendation rejected: {details}")
        self.violations = violations


class GuardrailValidator:
    def validate(self, result: RecommendationResult) -> None:
        violations: list[GuardrailViolation] = []
        lowered_recommendations = "\n".join(result.recommendations).lower()

        for rule_id, terms in TRIGGER_TERMS.items():
            for term in terms:
                if term in lowered_recommendations:
                    violations.append(
                        GuardrailViolation(
                            rule_id=rule_id,
                            message=UNSAFE_PATTERNS[rule_id],
                            matched_text=term,
                        )
                    )

        if not result.citations:
            violations.append(
                GuardrailViolation(
                    rule_id="missing_citations",
                    message="Recommendations must include explicit citations.",
                    matched_text="[]",
                )
            )

        if not result.safety_guardrails:
            violations.append(
                GuardrailViolation(
                    rule_id="missing_safety_guardrails",
                    message="Response must include safety guardrails.",
                    matched_text="[]",
                )
            )

        if not result.uncertainty_disclosure.strip():
            violations.append(
                GuardrailViolation(
                    rule_id="missing_uncertainty_disclosure",
                    message="Response must disclose uncertainty.",
                    matched_text="",
                )
            )

        if violations:
            raise GuardrailValidationError(violations)
