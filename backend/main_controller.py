import os
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api_center.okx_api.okx_main import OKXAPIWrapper
from backend.controller_center.trade.trade_controller import router as trade_router
from backend.controller_center.strategy.strategy_controller import router as strategy_router
from backend.controller_center.balance.balance_controller import router as balance_router
from backend.controller_center.backtest.backtest_controller import router as backtest_router
from backend.controller_center.strategy_files.strategy_files_controller import router as strategy_files_router

okx = OKXAPIWrapper()

app = FastAPI()

app.include_router(trade_router, prefix="/api/trade")
app.include_router(strategy_router, prefix="/api/strategy")
app.include_router(balance_router, prefix="/api/balance")
app.include_router(backtest_router, prefix="/api/backtest")

app.include_router(strategy_files_router, prefix="/api/strategy-files")

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
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    import uvicorn
    from data_object_center.settings import settings
    uvicorn.run("main_controller:app",
                host=settings.API_HOST,
                port=settings.API_PORT,
                reload=settings.DEBUG)
