import pandas_datareader as web
import datetime as dt

START = dt.datetime(1960, 1, 1)
END = dt.datetime(2024, 12, 31)

# Function to get US inflation data YoY
def get_us_inflation_data_yoy():
    # Fetch CPI data from FRED
    cpi_data = web.DataReader("CPIAUCNS", "fred", START, END)

    # Calculate YoY inflation rate
    cpi_data['Inflation Rate YoY'] = cpi_data['CPIAUCNS'].pct_change(12) * 100

    # Drop NaN values
    cpi_data = cpi_data.dropna()

    return cpi_data


if __name__ == '__main__':
    print(get_us_inflation_data_yoy())
