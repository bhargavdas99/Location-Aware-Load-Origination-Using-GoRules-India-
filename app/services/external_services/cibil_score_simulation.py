import asyncio


async def fetch_credit_score(pan: str):
    """Business logic for CIBIL score simulation"""
    # Simulation of a slight network delay
    await asyncio.sleep(0.5)
    return {"score": 750, "pan": pan, "provider": "TransUnion CIBIL"}
