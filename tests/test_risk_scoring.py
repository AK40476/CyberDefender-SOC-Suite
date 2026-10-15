import pytest

from app.services.risk_scoring import (
    get_risk_priority,
)


@pytest.mark.parametrize(
    ("score", "expected"),
    [
        (0, "low"),
        (5, "low"),
        (29, "low"),
        (30, "medium"),
        (59, "medium"),
        (60, "high"),
        (79, "high"),
        (80, "critical"),
        (100, "critical"),
    ],
)
def test_risk_priority_thresholds(score, expected):
    assert get_risk_priority(score) == expected