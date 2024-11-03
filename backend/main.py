import multiprocessing
from fastapi import FastAPI
from backend.service.okx_api.okx_main_api import OKXAPIWrapper
from multiprocessing import Process
from backend.service.sche_api import main_processor
from backend.controller.trade_controller import router as trade_router
from config.middleware import setup_middleware
from config.settings import settings


def create_app() -> FastAPI:
    app = FastAPI(
        title="Trading API",
        description="Trading system API",
        version="1.0.0",
        debug=settings.DEBUG
    )

    # 设置中间件
    setup_middleware(app)

    # 注册路由
    app.include_router(trade_router)

    return app


app = create_app()
okx = OKXAPIWrapper()


@app.get("/")
async def read_root():
    current_process_name = multiprocessing.current_process().name
    return {
        "message": f"Hello, FastAPI! I'm running in the {current_process_name} process.",
        "environment": settings.ENV
    }


@app.get("/get_balance")
def get_balance():
    try:
        return okx.account.get_account_balance()
    except Exception as e:
        print(f"Error getting OKX account: {e}")
        return None


def start_main_processor():
    print("Starting main processor...")
    main_processor()


def start_fastapi_app():
    import uvicorn
    uvicorn.run(
        app,
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG
    )


if __name__ == "__main__":
    api_process = Process(target=start_fastapi_app, name="api_process")
    api_process.start()
