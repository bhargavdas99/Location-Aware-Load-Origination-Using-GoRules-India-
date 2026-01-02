import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.api.loan import router as loan_router
from app.core.database import async_engine, Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    # This block runs when the app starts
    async with async_engine.begin() as conn:
        # This creates all tables defined in the SQLAlchemy models if they don't exist.
        await conn.run_sync(Base.metadata.create_all)

    yield


app = FastAPI(title="Location aware Loan Engine", lifespan=lifespan)

# Include the loan evaluation routes
app.include_router(loan_router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
