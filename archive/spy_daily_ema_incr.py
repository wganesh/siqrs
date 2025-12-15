import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime, timedelta
import matplotlib.dates as mdates


# -----------------------------
# Parameters
# -----------------------------
ticker = "SPY"
start_date = "2015-01-01"
plot_years = 1

data_dir = Path("./data")
data_dir.mkdir(exist_ok=True)

csv_file = data_dir / "spy_daily_indicators.csv"
plot_file = data_dir / "spy_ema_rsi_macd_last_1y.png"

price_col = "Close"
ema_periods = [12, 26, 50, 200]


# -----------------------------
# Load or fetch data (incremental)
# -----------------------------
if csv_file.exists():
    data = pd.read_csv(csv_file, index_col=0, parse_dates=True)
    last_date = data.index.max()
    last_date_dt = datetime.strptime(last_date, '%Y-%m-%d')
    fetch_start = last_date + timedelta(days=1)

    if fetch_start.date() <= datetime.today().date():
        new_data = yf.download(
            ticker,
            start=fetch_start.strftime("%Y-%m-%d")
        )
        if not new_data.empty:
            data = pd.concat([data, new_data[[price_col]]])
else:
    data = yf.download(ticker, start=start_date)
    data = data[[price_col]]

# Defensive cleanup
data = data[~data.index.duplicated(keep="last")]

# -----------------------------
# EMA calculations (FULL history)
# -----------------------------
for period in ema_periods:
    data[f"EMA_{period}"] = data[price_col].ewm(
        span=period, adjust=False
    ).mean()

# -----------------------------
# RSI (14)
# -----------------------------
rsi_period = 14
delta = data[price_col].diff()

gain = delta.where(delta > 0, 0.0)
loss = -delta.where(delta < 0, 0.0)

avg_gain = gain.ewm(alpha=1 / rsi_period, adjust=False).mean()
avg_loss = loss.ewm(alpha=1 / rsi_period, adjust=False).mean()

rs = avg_gain / avg_loss
data["RSI_14"] = 100 - (100 / (1 + rs))

# -----------------------------
# MACD (12, 26, 9)
# -----------------------------
data["MACD"] = data["EMA_12"] - data["EMA_26"]
data["MACD_Signal"] = data["MACD"].ewm(
    span=9, adjust=False
).mean()
data["MACD_Hist"] = data["MACD"] - data["MACD_Signal"]

# -----------------------------
# Save data
# -----------------------------
data.to_csv(csv_file)

# -----------------------------
# Filter last 1 year for plotting
# -----------------------------
end_date = data.index.max()
start_plot_date = end_date - pd.DateOffset(years=plot_years)
plot_data = data.loc[data.index >= start_plot_date]

def label_last_value(ax, x, y, label, color, y_offset=0):
    """Label the last value of a time series on the right edge"""
    x_val = mdates.date2num(x[-1])
    ax.text(
        x_val,
        y[-1] + y_offset,
        f"{label}: {y[-1]:.2f}",
        color=color,
        fontsize=9,
        va="center"
    )

# -----------------------------
# Plot (3 panels)
# -----------------------------
fig, axes = plt.subplots(
    3, 1, figsize=(14, 12), sharex=True,
    gridspec_kw={"height_ratios": [3, 1, 1]}
)

# ---- Price + EMA panel ----
# ---- Price + EMA panel ----
axes[0].plot(plot_data.index, plot_data[price_col],
             color="black", linewidth=2)

axes[0].plot(plot_data.index, plot_data["EMA_12"], color="blue")
axes[0].plot(plot_data.index, plot_data["EMA_26"], color="orange")
axes[0].plot(plot_data.index, plot_data["EMA_50"], color="green")
axes[0].plot(plot_data.index, plot_data["EMA_200"], color="red")

# Label last values
label_last_value(axes[0], plot_data.index, plot_data[price_col], "Close", "black")
label_last_value(axes[0], plot_data.index, plot_data["EMA_12"], "EMA 12", "blue")
label_last_value(axes[0], plot_data.index, plot_data["EMA_26"], "EMA 26", "orange")
label_last_value(axes[0], plot_data.index, plot_data["EMA_50"], "EMA 50", "green")
label_last_value(axes[0], plot_data.index, plot_data["EMA_200"], "EMA 200", "red")

axes[0].set_title("SPY Price with EMA (Last 1 Year)")
axes[0].set_ylabel("Price (USD)")
axes[0].grid(True)


# ---- RSI panel ----
axes[1].plot(plot_data.index, plot_data["RSI_14"], color="purple")

axes[1].axhline(70, color="red", linestyle="--", linewidth=1)
axes[1].axhline(30, color="green", linestyle="--", linewidth=1)

label_last_value(axes[1], plot_data.index, plot_data["RSI_14"], "RSI 14", "purple")

axes[1].set_ylabel("RSI")
axes[1].set_ylim(0, 100)
axes[1].grid(True)


# ---- MACD panel ----
axes[2].plot(plot_data.index, plot_data["MACD"], color="blue")
axes[2].plot(plot_data.index, plot_data["MACD_Signal"], color="orange")

axes[2].bar(plot_data.index, plot_data["MACD_Hist"], alpha=0.4)

label_last_value(axes[2], plot_data.index, plot_data["MACD"], "MACD", "blue")
label_last_value(axes[2], plot_data.index, plot_data["MACD_Signal"], "Signal", "orange", y_offset=-0.5)

axes[2].set_ylabel("MACD")
axes[2].grid(True)


plt.tight_layout()
plt.savefig(plot_file, dpi=150)
plt.close()

print(f"Data saved to: {csv_file.resolve()}")
print(f"Plot saved to: {plot_file.resolve()}")


