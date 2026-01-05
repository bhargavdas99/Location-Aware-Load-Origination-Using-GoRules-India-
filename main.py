import uvicorn
import logging
from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.api.loan import router as loan_router
from app.api.mocks import router as mocks_router
from app.services.external_services.external_services import ExternalServiceOrchestrator

# Setup logging so we can see the startup/shutdown process
logger = logging.getLogger(__name__)

# Initialize the orchestrator globally so it can be reused across all requests
orchestrator = ExternalServiceOrchestrator()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- STARTUP ---
    logger.info("Application starting up...")

    yield

    # --- SHUTDOWN ---
    # Crucial: This is to gracefully closes the HTTP connection pool.
    logger.info("Closing external service connections...")
    await orchestrator.close()
    logger.info("Application shutdown complete.")


app = FastAPI(
    title="Location Aware Loan Engine",
    description="A resilient loan origination system using GoRules and Async external services.",
    lifespan=lifespan,
)

# Include the routes
app.include_router(loan_router)
app.include_router(mocks_router)

if __name__ == "__main__":
    # Note: It's common to use the string "app.main:app" for reload mode
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
