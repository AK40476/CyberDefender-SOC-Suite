
from types import SimpleNamespace

import pytest

from app.services.risk_scoring import (
    DETECTION_SCORES,
    SEVERITY_SCORES,
    calculate_risk_score,
)

@pytest.mark.parametrize(
    ("severity", "rule", "status", "expected"),
    [
        ("critical", "IOC_MATCH", "new", 80),
        ("high", "BRUTE_FORCE_LOGIN", "new", 60),
        ("medium", "CREDENTIAL_STUFFING", "new", 50),
        ("low", "BRUTE_FORCE_LOGIN", "resolved", 25),
        ("low", "UNKNOWN_RULE", "resolved", 5),
        ("critical", "IOC_MATCH", "resolved", 70),
    ],
)
def test_calculate_risk_score(severity, rule, status, expected):
    alert = SimpleNamespace(
        severity=severity,
        detection_rule=rule,
        status=status,
    )

    assert calculate_risk_score(alert) == expected


def test_strongest_current_combination_scores_80():
    alert = SimpleNamespace(
        severity="critical",
        detection_rule="IOC_MATCH",
        status="new",
    )

    assert calculate_risk_score(alert) == 80

    
def test_risk_score_is_capped_at_100(monkeypatch):
    monkeypatch.setitem(SEVERITY_SCORES, "critical", 90)
    monkeypatch.setitem(DETECTION_SCORES, "IOC_MATCH", 30)

    alert = SimpleNamespace(
        severity="critical",
        detection_rule="IOC_MATCH",
        status="new",
    )

    assert calculate_risk_score(alert) == 100
