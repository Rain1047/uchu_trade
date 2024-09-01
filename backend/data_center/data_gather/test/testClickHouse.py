from clickhouse_driver import Client
from datetime import datetime

# 连接到ClickHouse服务器
client = Client(host='localhost', user='default', password='', database='default')

# 创建K线数据表
create_table_query = """
CREATE TABLE IF NOT EXISTS kline_data (
    symbol String,
    interval String,
    open_time DateTime,
    open Float64,
    high Float64,
    low Float64,
    close Float64,
    volume Float64,
    close_time DateTime
) ENGINE = MergeTree()
ORDER BY (symbol, interval, open_time);
"""

client.execute(create_table_query)
print("Table created successfully.")

# 插入K线数据
data = [
    ('BTCUSDT', '15m', datetime(2023, 8, 25, 0, 0), 100.0, 102.0, 99.0, 101.0, 1000.0, datetime(2023, 8, 25, 0, 15)),
    ('BTCUSDT', '4h', datetime(2023, 8, 25, 0, 0), 100.0, 110.0, 98.0, 108.0, 5000.0, datetime(2023, 8, 25, 4, 0)),
    ('BTCUSDT', '1d', datetime(2023, 8, 25, 0, 0), 100.0, 120.0, 90.0, 115.0, 20000.0, datetime(2023, 8, 25, 23, 59, 59))
]

client.execute('INSERT INTO kline_data VALUES', data)
print("Data inserted successfully.")

# 查询K线数据
result = client.execute("SELECT * FROM kline_data WHERE interval = '15m'")

# 打印查询结果
print("15分钟K线数据：")
for row in result:
    print(row)

# 查询4小时K线数据
result_4h = client.execute("SELECT * FROM kline_data WHERE interval = '4h'")

# 打印4小时K线数据
print("4小时K线数据：")
for row in result_4h:
    print(row)

# 查询1天K线数据
result_1d = client.execute("SELECT * FROM kline_data WHERE interval = '1d'")

# 打印1天K线数据
print("1天K线数据：")
for row in result_1d:
    print(row)

# 关闭连接
client.disconnect()
print("Connection closed.")
