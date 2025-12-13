import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime, timedelta

# -----------------------------
# Parameters
# -----------------------------
ticker = "SPY"
start_date = "2015-01-01"
plot_years = 1

data_dir = Path("./data")
data_dir.mkdir(exist_ok=True)

csv_file = data_dir / "spy_daily.csv"
plot_file = data_dir / "spy_ema_last_1y.png"

price_col = "Close"
ema_periods = [8, 21, 50, 200]

# -----------------------------
# Load or fetch data
# -----------------------------
if csv_file.exists():
    print("CSV found. Loading existing data...")
    data = pd.read_csv(csv_file, index_col=0, parse_dates=True)

    last_date = data.index.max()
    fetch_start = last_date + timedelta(days=1)

    if fetch_start.date() <= datetime.today().date():
        print(f"Fetching new data from {fetch_start.date()} to today...")
        new_data = yf.download(
            ticker,
            start=fetch_start.strftime("%Y-%m-%d")
        )

        if not new_data.empty:
            new_data = new_data[[price_col]]
            data = pd.concat([data, new_data])
    else:
        print("Data already up to date.")
else:
    print("CSV not found. Fetching full history...")
    data = yf.download(ticker, start=start_date)
    data = data[[price_col]]

# Remove any duplicate dates (defensive)
data = data[~data.index.duplicated(keep="last")]

# -----------------------------
# Recalculate EMAs (FULL history)
# -----------------------------
for period in ema_periods:
    data[f"EMA_{period}"] = data[price_col].ewm(
        span=period, adjust=False
    ).mean()

# -----------------------------
# Save data to disk
# -----------------------------
data.to_csv(csv_file)
print(f"Data saved to {csv_file.resolve()}")

# -----------------------------
# Filter last 1 year for plotting
# -----------------------------
end_date = data.index.max()
start_plot_date = end_date - pd.DateOffset(years=plot_years)
plot_data = data.loc[data.index >= start_plot_date]

# -----------------------------
# Plot and save image
# -----------------------------
plt.figure(figsize=(14, 8))

plt.plot(
    plot_data.index,
    plot_data[price_col],
    label="SPY Close",
    linewidth=2
)

for period in ema_periods:
    plt.plot(
        plot_data.index,
        plot_data[f"EMA_{period}"],
        label=f"EMA {period}",
        linewidth=1.5
    )

plt.title("SPY Close with 8, 21, 50, 200 EMA (Last 1 Year)")
plt.xlabel("Date")
plt.ylabel("Price (USD)")
plt.legend()
plt.grid(True)
plt.tight_layout()

plt.savefig(plot_file, dpi=150)
plt.close()

print(f"Plot saved to {plot_file.resolve()}")
