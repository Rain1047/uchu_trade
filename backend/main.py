import os
import sys
from fastapi import FastAPI
from backend.service.okx_api.okx_main_api import OKXAPIWrapper
from backend.service.sche_api import main_processor
from backend.controller.trade_controller import router as trade_router
from config.middleware import setup_middleware
from config.settings import settings
import uvicorn


def create_app() -> FastAPI:
    app = FastAPI(
        title="Trading API",
        description="Trading system API",
        version="1.0.0",
        debug=settings.DEBUG
    )

    setup_middleware(app)
    app.include_router(trade_router)
    return app


app = create_app()
okx = OKXAPIWrapper()


@app.get("/")
async def read_root():
    return {"message": "Hello, FastAPI!", "environment": settings.ENV}


@app.get("/get_balance")
def get_balance():
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
