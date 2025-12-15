import pandas as pd
import os

def calculate_macd(df, column, fast=12, slow=26, signal=9):
    """
    Calculate MACD (Moving Average Convergence Divergence)
    
    Parameters:
    - df: DataFrame with stock data
    - column: Column name to calculate MACD on (typically Close price)
    - fast: Fast EMA period (default 12)
    - slow: Slow EMA period (default 26)
    - signal: Signal line EMA period (default 9)
    
    Returns:
    - Tuple of (macd, signal_line, histogram)
    """
    ema_fast = df[column].ewm(span=fast, adjust=False).mean()
    ema_slow = df[column].ewm(span=slow, adjust=False).mean()
    macd = ema_fast - ema_slow
    signal_line = macd.ewm(span=signal, adjust=False).mean()
    histogram = macd - signal_line
    return macd, signal_line, histogram

def add_macd_to_file(csv_file, fast=12, slow=26, signal=9):
    """
    Add MACD indicators to a stock CSV file
    
    Parameters:
    - csv_file: Path to the CSV file
    - fast: Fast EMA period (default 12)
    - slow: Slow EMA period (default 26)
    - signal: Signal line EMA period (default 9)
    
    Returns:
    - DataFrame with MACD columns added
    """
    try:
        print(f"Calculating MACD for {os.path.basename(csv_file)}...")
        
        # Read the CSV file
        df = pd.read_csv(csv_file, header=[0, 1], index_col=0, parse_dates=True)
        
        # Get the ticker symbol
        ticker = df.columns[0][1]
        
        # Access the Close price column
        close_col = ('Price', ticker) if 'Price' in df.columns.levels[0] else ('Close', ticker)
        
        # Calculate MACD
        macd, signal_line, histogram = calculate_macd(df, close_col, fast, slow, signal)
        df[('MACD', ticker)] = macd
        df[('MACD_Signal', ticker)] = signal_line
        df[('MACD_Hist', ticker)] = histogram
        
        print(f"  ✓ MACD ({fast},{slow}) calculated")
        print(f"  ✓ MACD Signal Line ({signal}) calculated")
        print(f"  ✓ MACD Histogram calculated")
        
        # Save back to the same file
        df.to_csv(csv_file)
        print(f"✓ {os.path.basename(csv_file)}: MACD indicators saved\n")
        
        return df
        
    except Exception as e:
        print(f"✗ Error processing {os.path.basename(csv_file)}: {str(e)}\n")
        return None

# Example usage
if __name__ == "__main__":
    # Single file
    add_macd_to_file('stock_data/AAPL.csv', fast=12, slow=26, signal=9)
    
    # Or process multiple files
    # import json
    # with open('tickers.json', 'r') as f:
    #     tickers = json.load(f)
    # for ticker in tickers:
    #     add_macd_to_file(f'stock_data/{ticker}.csv')