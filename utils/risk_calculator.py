def calculate_risk_score(likelihood: int, impact: int) -> int:
    """
    Calculate risk score based on 5x5 matrix.
    Score = Likelihood * Impact
    """
    if not (1 <= likelihood <= 5 and 1 <= impact <= 5):
        raise ValueError("Likelihood and Impact must be between 1 and 5.")
    return likelihood * impact

def determine_risk_level(risk_score: int) -> str:
    """
    Determine risk classification based on score.
    1-4 = Low
    5-9 = Medium
    10-16 = High
    17-25 = Critical
    """
    if 1 <= risk_score <= 4:
        return "Low"
    elif 5 <= risk_score <= 9:
        return "Medium"
    elif 10 <= risk_score <= 16:
        return "High"
    elif 17 <= risk_score <= 25:
        return "Critical"
    else:
        raise ValueError(f"Invalid risk score: {risk_score}. Must be between 1 and 25.")
