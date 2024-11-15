import os
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api_center.okx_api.okx_main_api import OKXAPIWrapper
from backend.controller.trade.trade_controller import router as trade_router
from backend.controller.strategy.strategy_controller import router as strategy_router
from backend.controller.settings import settings
import uvicorn

okx = OKXAPIWrapper()

app = FastAPI()

app.include_router(trade_router, prefix="/api/trade")
app.include_router(strategy_router, prefix="/api/strategy")

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:8080",
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def read_root():
    return {"message": "Hello, FastAPI!", "environment": settings.ENV}


@app.get("/get_account_balance")
def get_account_balance():
    try:
        return okx.account.get_account_balance()
    except Exception as e:
        print(f"Error getting OKX account: {e}")
        return None


if __name__ == "__main__":
    # Set the application import string for reload
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    uvicorn.run("main:app",  # Use the import string here
                host=settings.API_HOST,
                port=settings.API_PORT,
                reload=settings.DEBUG)
