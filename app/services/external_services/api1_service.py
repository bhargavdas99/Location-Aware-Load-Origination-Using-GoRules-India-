import re
from app.core.config import settings


async def validate_identity(pan: str):
    """Business logic for PAN Card validation"""
    pan_upper = pan.upper().strip()
    if not re.match(settings.PAN_REGEX, pan_upper):
        return {"valid": False, "error": "Invalid PAN Format"}
    return {"valid": True, "status": "verified", "pan": pan_upper}
