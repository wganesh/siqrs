import yfinance as yf
from datetime import datetime, timedelta

# Define the ticker
ticker_symbol = "TQQQ"

# Yahoo Finance limit for 1h data is exactly 730 days back
start_date = (datetime.now() - timedelta(days=729)).strftime('%Y-%m-%d')
end_date = datetime.now().strftime('%Y-%m-%d')

print(f"Fetching 1h data from {start_date} to {end_date}...")

# Download the data
data = yf.download(
    tickers=ticker_symbol,
    start=start_date,
    end=end_date,
    interval="1h",
    auto_adjust=True
)

# Display the first few rows
print(data.head())

data.to_csv("stock_data/hourly_data_1y_tqqq.csv")

# Optional: Save to CSV
# data.to_csv("TQQQ_2y_hourly.csv")
