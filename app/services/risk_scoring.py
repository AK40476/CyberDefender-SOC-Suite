SEVERITY_SCORES = {
    "critical": 40,
    "high": 30,
    "medium": 15,
    "low": 5,
}

DETECTION_SCORES = {
    "IOC_MATCH": 30,
    "CREDENTIAL_STUFFING": 25,
    "BRUTE_FORCE_LOGIN": 20,
}


def calculate_risk_score(alert):
    score = 0

    severity = (alert.severity or "medium").lower()

    score += SEVERITY_SCORES.get(
        severity,
        0
    )

    score += DETECTION_SCORES.get(
        alert.detection_rule,
        0
    )

    if alert.status == "new":
        score += 10

    return min(score, 100)


def get_risk_priority(score):
    if score >= 80:
        return "critical"

    if score >= 60:
        return "high"

    if score >= 30:
        return "medium"

    return "low"