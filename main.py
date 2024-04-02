from fastapi import FastAPI
from _service_center.account_okx import AccountAPI
from _service_center.trade_okx import TradeAPI
from fastapi.middleware.cors import CORSMiddleware


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


@app.get("/")
async def read_root():
    return {"message": "Hello, FastAPI!"}


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
async def place_order(order: OrderOkx):
    # 此处，你可以添加处理订单逻辑，例如将订单信息保存到数据库等
    # 但是在这个简单的例子中，我们只返回一个假的成功响应
    print("order class: {}".format(order))
    result = trade_okx.post_order(order)

    # 这里模拟订单处理，可以在这里插入将订单信息保存到数据库的代码
    # 返回假的成功响应
    return result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)


# @app.get("/data/basic_info/jeffCox")
# async def get_jeffCox():
#     fed_news_list = get_fed_news(url, div_class)
#     check_and_process_fed_news(fed_news_list, target_date)
# 
#     # You can return a JSON response or customize it based on your needs.
#     return JSONResponse(content={"message": "Jeff Cox data retrieved and processed successfully."})


# @app.post("")
# async def

