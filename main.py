from fastapi import FastAPI, BackgroundTasks
from _service_center.account_okx import AccountAPI
from _service_center.trade_okx import TradeAPI
from fastapi.middleware.cors import CORSMiddleware
from _sche_processor.schedule_processor import *
from _data_center.data_object.req.post_order_req import *
from multiprocessing import Process
import logging

app = FastAPI()
account_okx = AccountAPI()
trade_okx = TradeAPI()

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有 HTTP 方法
    allow_headers=["*"],  # 允许所有 HTTP 头部
)


def start_celery_worker():
    from celery_app import celery_app
    argv = [
        'worker',
        '--loglevel=info',
        '-E',
    ]
    celery_app.worker_main(argv)


@app.get("/")
async def read_root():
    current_process_name = multiprocessing.current_process().name
    return {"message": f"Hello, FastAPI! I'm running in the {current_process_name} process."}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


@app.get("/get_balance")
def get_account_api():
    try:
        balance = account_okx.get_balance()
        return balance
    except Exception as e:
        print(f"Error getting OKX account: {e}")
        return None


@app.get("/get_positions")
def get_account_api():
    try:
        balance = account_okx.get_balance()
        return balance
    except Exception as e:
        print(f"Error getting OKX account: {e}")
        return None


@app.post("/place_order")
async def place_order(order: PostOrderReq):
    # 此处，你可以添加处理订单逻辑，例如将订单信息保存到数据库等
    # 但是在这个简单的例子中，我们只返回一个假的成功响应
    print("order class: {}".format(order))
    result = trade_okx.post_order(order)

    # 这里模拟订单处理，可以在这里插入将订单信息保存到数据库的代码
    # 返回假的成功响应
    return result


def start_main_processor():
    print("Starting main processor1...")
    # 在后台任务中调用sche_processor中的任务
    main_processor()


# 启动 FastAPI Web应用
def start_fastapi_app():
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)


if __name__ == "__main__":
    # 分别在不同的进程中启动 FastAPI 应用和后台任务
    api_process = Process(target=start_fastapi_app, name="api_process")
    background_process = Process(target=start_main_processor, name="background_process")

    api_process.start()
    background_process.start()

    api_process.join()  # 等待 FastAPI 应用进程结束
    background_process.join()  # 等待后台任务进程结束

# @app.get("/data/basic_info/jeffCox")
# async def get_jeffCox():
#     fed_news_list = get_fed_news(url, div_class)
#     check_and_process_fed_news(fed_news_list, target_date)
# 
#     # You can return a JSON response or customize it based on your needs.
#     return JSONResponse(content={"message": "Jeff Cox data retrieved and processed successfully."})