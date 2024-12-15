from binance.spot import Spot

from backend._utils import ConfigUtils

client = Spot()

if __name__ == '__main__':
    # Get server timestamp
    print(client.time())
    # Get klines of BTCUSDT at 1m interval
    print(client.klines("BTCUSDT", "1m"))
    # Get last 10 klines of BNBUSDT at 1h interval
    print(client.klines("BNBUSDT", "1h", limit=10))

    config = ConfigUtils.get_config()
    print(config)

    # API key/secret are required for user data endpoints
    client = Spot(api_key=config['binance_api_key'], api_secret=config['binance_secret_key'])

    # Get account and balance information
    print(client.account())
    #
    # Post a new order
    params = {
        'symbol': 'BTCUSDT',
        'side': 'SELL',
        'type': 'LIMIT',
        'timeInForce': 'GTC',
        'quantity': 0.002,
        'price': 9500
    }
    #
    response = client.new_order(**params)
    print(response)