import pandas as pd
import os

def calculate_ema(df, column, period):
    """
    Calculate Exponential Moving Average
    
    Parameters:
    - df: DataFrame with stock data
    - column: Column name to calculate EMA on (typically Close price)
    - period: Number of periods for EMA calculation
    
    Returns:
    - Series with EMA values
    """
    return df[column].ewm(span=period, adjust=False).mean()

def add_ema_to_file(csv_file, periods=[12, 26, 50, 200]):
    """
    Add EMA indicators to a stock CSV file
    
    Parameters:
    - csv_file: Path to the CSV file
    - periods: List of EMA periods to calculate
    
    Returns:
    - DataFrame with EMA columns added
    """
    try:
        print(f"Calculating EMA for {os.path.basename(csv_file)}...")
        
        # Read the CSV file
        df = pd.read_csv(csv_file, header=[0, 1], index_col=0, parse_dates=True)
        
        # Get the ticker symbol
        ticker = df.columns[0][1]
        
        # Access the Close price column
        close_col = ('Price', ticker) if 'Price' in df.columns.levels[0] else ('Close', ticker)
        
        # Calculate EMAs for each period
        for period in periods:
            df[(f'EMA_{period}', ticker)] = calculate_ema(df, close_col, period)
            print(f"  ✓ EMA_{period} calculated")
        
        # Save back to the same file
        df.to_csv(csv_file)
        print(f"✓ {os.path.basename(csv_file)}: EMA indicators saved\n")
        
        return df
        
    except Exception as e:
        print(f"✗ Error processing {os.path.basename(csv_file)}: {str(e)}\n")
        return None

# Example usage
if __name__ == "__main__":
    # Single file
    add_ema_to_file('stock_data/AAPL.csv', periods=[12, 26, 50, 200])
    
    # Or process multiple files
    # import json
    # with open('tickers.json', 'r') as f:
    #     tickers = json.load(f)
    # for ticker in tickers:
    #     add_ema_to_file(f'stock_data/{ticker}.csv')