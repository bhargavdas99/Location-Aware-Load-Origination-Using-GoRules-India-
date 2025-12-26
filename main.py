import uvicorn
from fastapi import FastAPI
from app.api.loan import router as loan_router

app = FastAPI(title="Location aware Loan Engine")
app.include_router(loan_router)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
