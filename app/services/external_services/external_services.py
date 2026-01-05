import httpx
import logging
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
)
from app.core.config import settings

logger = logging.getLogger(__name__)


class ExternalServiceOrchestrator:
    def __init__(self):
        # We define the client here - which allows us to share one connection pool for all calls.
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(settings.API_TIMEOUT),
            limits=httpx.Limits(max_connections=100, max_keepalive_connections=20),
        )

    async def close(self):
        """Call this on app shutdown to close the 'Pipe' cleanly"""
        await self.client.aclose()

    @retry(
        stop=stop_after_attempt(settings.MAX_RETRIES),
        wait=wait_exponential(multiplier=1, min=2, max=6),
        retry=retry_if_exception_type((httpx.HTTPStatusError, httpx.RequestError)),
        # logs the retry attempt so we can see it in your terminal
        before_sleep=before_sleep_log(logger, logging.WARNING),
    )
    async def _post_request(self, url: str, data: dict):
        response = await self.client.post(url, json=data)

        # by default httpx doesn't return errors for response codes
        # raise_for_status tells us to retry on 4xx/5xx
        response.raise_for_status()
        return response.json()

    async def check_identity(self, pan: str):
        return await self._post_request(settings.IDENTITY_SERVICE_URL, {"pan": pan})

    async def check_fraud(self, pan: str):
        return await self._post_request(settings.FRAUD_SERVICE_URL, {"pan": pan})

    async def get_cibil_score(self, pan: str):
        return await self._post_request(settings.CIBIL_SERVICE_URL, {"pan": pan})
