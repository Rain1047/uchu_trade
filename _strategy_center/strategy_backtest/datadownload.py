import yfinance as yf

if __name__ == '__main__':
    data = yf.download('AAPL', start='2020-01-01', end='2021-01-01')
    data.to_csv('AAPL.csv')
