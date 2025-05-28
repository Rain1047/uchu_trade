import os
import sys

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.controller_center.settings import settings
from backend._utils import LogConfig

from api_center.okx_api.okx_main import OKXAPIWrapper
from backend.controller_center.trade.trade_controller import router as trade_router
from backend.controller_center.strategy.strategy_controller import router as strategy_router
from backend.controller_center.balance.balance_controller import router as balance_router
from backend.controller_center.backtest.backtest_controller import router as backtest_router
from backend.controller_center.strategy_files.strategy_files_controller import router as strategy_files_router
from backend.controller_center.record.record_controller import router as record_router
from backend.controller_center.agent.agent_controller import router as agent_router
from backend.controller_center.agent.chat_controller import router as chat_router
from backend.api_center.universal_backtest_api import router as universal_backtest_router
from backend.controller_center.backtest.enhanced_backtest_controller import router as enhanced_backtest_router
from backend.controller_center.strategy.llm_strategy_controller import router as llm_strategy_router
from backend.controller.strategy_instance_controller import router as strategy_instance_router
from backend.data_object_center.base import Base, engine

# 导入所有模型类以确保表被创建
from backend.data_object_center.agent.system_prompt import SystemPrompt
from backend.data_object_center.agent.upload_file import UploadFile
from backend.data_object_center.agent.strategy_job import StrategyJob
from backend.data_object_center.strategy_instance import StrategyInstance
from backend.data_object_center.strategy_execution_record import StrategyExecutionRecord

# 导入策略调度器
from backend.schedule_center.strategy_scheduler import strategy_scheduler

import uvicorn

# 初始化日志配置
LogConfig.setup()

logger = LogConfig.get_logger(__name__)

# 创建数据库表
try:
    # 确保所有模型都被导入
    logger.info("开始创建数据库表...")
    Base.metadata.create_all(bind=engine)
    logger.info("数据库表创建完成")
except Exception as e:
    logger.error(f"创建数据库表时出错: {e}")
    raise

okx = OKXAPIWrapper()

app = FastAPI()

app.include_router(trade_router, prefix="/api/trade", tags=["trade"])
app.include_router(strategy_router, prefix="/api/strategy", tags=["strategy"])
app.include_router(balance_router, prefix="/api/balance", tags=["balance"])
app.include_router(backtest_router, prefix="/api/backtest", tags=["backtest"])
app.include_router(strategy_files_router, prefix="/api/strategy-files", tags=["strategy-files"])
app.include_router(record_router, prefix="/api/record", tags=["record"])
app.include_router(agent_router, prefix="/api/agent", tags=["agent"])
app.include_router(chat_router, prefix="/api/agent", tags=["agent-chat"])
app.include_router(universal_backtest_router, tags=["universal-backtest"])
app.include_router(enhanced_backtest_router, tags=["enhanced-backtest"])
app.include_router(llm_strategy_router, tags=["llm-strategy"])
app.include_router(strategy_instance_router, tags=["strategy-instance"])

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """应用启动时执行"""
    logger.info("启动策略调度器...")
    strategy_scheduler.start()
    logger.info("策略调度器启动完成")


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时执行"""
    logger.info("停止策略调度器...")
    strategy_scheduler.stop()
    logger.info("策略调度器已停止")


@app.get("/")
async def read_root():
    return {"message": "Hello, FastAPI!", "environment": settings.ENV}


@app.get("/get_account_balance")
def get_account_balance():
    try:
        return okx.account.get_account_balance()
    except Exception as e:
        logger.error(f"获取OKX账户余额时出错: {e}")
        return None


if __name__ == "__main__":
    logger.info(f"启动FastAPI服务器 - 主机: {settings.API_HOST}, 端口: {settings.API_PORT}")
    uvicorn.run("main_controller:app",
                host=settings.API_HOST,
                port=settings.API_PORT,
                reload=settings.DEBUG)
