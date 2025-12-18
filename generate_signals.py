import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


# ---------------------------
# Configuration
# ---------------------------
STOCK_DATA_DIR = "stock_data"
SIGNALS_DIR = "signals"
LOOKBACK_DAYS = 365


os.makedirs(SIGNALS_DIR, exist_ok=True)


# ---------------------------
# Helper: Load & clean CSV
# ---------------------------
def load_stock_csv(filepath):
    raw = pd.read_csv(filepath)

    df = raw.iloc[2:].copy()

    df.rename(
        columns={
            "Price": "Date",
            "MACD_Hist": "MACD_Histogram",
        },
        inplace=True,
    )

    df["Date"] = pd.to_datetime(df["Date"])
    numeric_cols = df.columns.drop("Date")
    df[numeric_cols] = df[numeric_cols].astype(float)

    return df.sort_values("Date").reset_index(drop=True)


# ---------------------------
# EMA crossover detection
# ---------------------------
def detect_ema_crossovers(df):
    diff = df["EMA_12"] - df["EMA_26"]
    prev_diff = diff.shift(1)

    bullish = (diff > 0) & (prev_diff <= 0)
    bearish = (diff < 0) & (prev_diff >= 0)

    return bullish, bearish


# ---------------------------
# Main loop
# ---------------------------
today = pd.Timestamp.today().normalize()
start_date = today - pd.Timedelta(days=LOOKBACK_DAYS)

for filename in os.listdir(STOCK_DATA_DIR):
    if not filename.endswith(".csv"):
        continue

    ticker = filename.replace(".csv", "")
    filepath = os.path.join(STOCK_DATA_DIR, filename)

    df = load_stock_csv(filepath)
    df = df[df["Date"] >= start_date]

    if df.empty:
        continue

    bullish, bearish = detect_ema_crossovers(df)

    # Determine latest signal
    latest_signal = "Neutral"
    if bullish.any() or bearish.any():
        last_bullish_date = df.loc[bullish, "Date"].max()
        last_bearish_date = df.loc[bearish, "Date"].max()

        if pd.notna(last_bullish_date) and (
            pd.isna(last_bearish_date) or last_bullish_date > last_bearish_date
        ):
            latest_signal = "Bullish"
        elif pd.notna(last_bearish_date):
            latest_signal = "Bearish"

    # ---------------------------
    # Plot
    # ---------------------------
    fig, axes = plt.subplots(
        3, 1, figsize=(14, 10), sharex=True,
        gridspec_kw={"height_ratios": [3, 2, 2]},
    )

    # === EMA + Price ===
    axes[0].plot(df["Date"], df["Close"], label="Close", linewidth=2)
    axes[0].plot(df["Date"], df["EMA_12"], label="EMA 12")
    axes[0].plot(df["Date"], df["EMA_26"], label="EMA 26")
    axes[0].plot(df["Date"], df["EMA_50"], label="EMA 50")
    axes[0].plot(df["Date"], df["EMA_200"], label="EMA 200")

    axes[0].scatter(
        df.loc[bullish, "Date"],
        df.loc[bullish, "Close"],
        marker="^",
        s=80,
        label="Bullish EMA Cross",
    )

    axes[0].scatter(
        df.loc[bearish, "Date"],
        df.loc[bearish, "Close"],
        marker="v",
        s=80,
        label="Bearish EMA Cross",
    )

    axes[0].set_title(f"{ticker} — Price, EMA & Signals (Last 1 Year)")
    axes[0].set_ylabel("Price")
    axes[0].legend(loc="upper left")
    axes[0].grid(alpha=0.3)

    axes[0].text(
        0.01,
        0.95,
        f"Signal: {latest_signal}",
        transform=axes[0].transAxes,
        fontsize=12,
        fontweight="bold",
        verticalalignment="top",
    )

    # === MACD ===
    axes[1].plot(df["Date"], df["MACD"], label="MACD")
    axes[1].plot(df["Date"], df["MACD_Signal"], label="Signal")
    axes[1].bar(df["Date"], df["MACD_Histogram"], alpha=0.4)
    axes[1].axhline(0, linewidth=1)
    axes[1].set_ylabel("MACD")
    axes[1].legend(loc="upper left")
    axes[1].grid(alpha=0.3)

    # === RSI ===
    axes[2].plot(df["Date"], df["RSI_14"])
    axes[2].axhline(70, linestyle="--", linewidth=1)
    axes[2].axhline(30, linestyle="--", linewidth=1)
    axes[2].set_ylabel("RSI")
    axes[2].set_ylim(0, 100)
    axes[2].grid(alpha=0.3)

    # X-axis formatting
    axes[2].xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))
    axes[2].xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
    fig.autofmt_xdate()

    # Save
    output_path = os.path.join(SIGNALS_DIR, f"{ticker}_signals.png")
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close(fig)

    print(f"{ticker}: {latest_signal} → saved to {output_path}")