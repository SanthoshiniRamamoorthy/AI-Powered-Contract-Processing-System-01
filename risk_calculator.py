# app/services/risk_calculator.py

def calculate_overall_risk(identified_risks: list) -> int:
    """
    Calculates a deterministic risk score based on the identified risks list.
    
    Args:
        identified_risks: List of risk dictionaries with 'severity' field
        
    Returns:
        int: Risk score between 0-10
    """
    if not identified_risks:
        return 0
    
    # Risk scores based on severity levels
    score_map = {
        "low": 2,
        "medium": 5,
        "high": 8
    }
    
    total = 0
    for item in identified_risks:
        severity = item.get("severity", "low").lower()
        total += score_map.get(severity, 0)
    
    # Cap the maximum score at 10
    return min(total, 10)


def get_risk_rating(risk_score: int) -> str:
    """
    Convert numerical risk score to categorical rating.
    
    Args:
        risk_score: Numerical score between 0-10
        
    Returns:
        str: Risk rating (LOW, MODERATE, HIGH)
    """
    if risk_score >= 7:
        return "HIGH"
    elif risk_score >= 4:
        return "MODERATE"
    else:
        return "LOW"