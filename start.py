import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

ticker = "SPY"
start_date = "2015-01-01"

data = yf.download(ticker, start=start_date)

data["Close"] = data["Close"]

ema_periods = [8, 21, 50, 200]

for period in ema_periods:
    data[f"EMA_{period}"] = data["Close"].ewm(span=period, adjust=False).mean()


plt.figure(figsize=(14, 8))

plt.plot(data.index, data["Close"], label="SPY Close", linewidth=2)

for period in ema_periods:
    plt.plot(
        data.index,
        data[f"EMA_{period}"],
        label=f"EMA {period}",
        linewidth=1.5
    )

plt.title("SPY Adjusted Close with 8, 21, 50, 200 EMA")
plt.xlabel("Date")
plt.ylabel("Price (USD)")
plt.legend()
plt.grid(True)
plt.tight_layout()

plt.show()