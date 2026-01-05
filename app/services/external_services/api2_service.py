import random


async def check_fraud_risk():
    """Business logic for Fraud simulation with failure injection"""
    # 20% failure rate as requested
    if random.random() < 0.2:
        return {"success": False, "error": "Internal Server Error"}

    return {"success": True, "risk_score": "low", "status": "clear"}
