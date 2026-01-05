from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str

    # Business Rules
    DECISION_RULE_KEY: str = "loan_decision"

    # Resiliency Settings
    MAX_RETRIES: int = 3
    API_TIMEOUT: float = 5.0

    # Validation
    PAN_REGEX: str = "^[A-Z]{5}[0-9]{4}[A-Z]{1}$"

    # External URLs
    IDENTITY_SERVICE_URL: str
    FRAUD_SERVICE_URL: str
    CIBIL_SERVICE_URL: str

    # Pydantic configuration to read the .env file
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


# Single instance to be used across the app
settings = Settings()
