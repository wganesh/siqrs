import pandas as pd
import os

def calculate_rsi(df, column, period=14):
    """
    Calculate Relative Strength Index (RSI)
    
    Parameters:
    - df: DataFrame with stock data
    - column: Column name to calculate RSI on (typically Close price)
    - period: Number of periods for RSI calculation (default 14)
    
    Returns:
    - Series with RSI values
    """
    delta = df[column].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def add_rsi_to_file(csv_file, period=14):
    """
    Add RSI indicator to a stock CSV file
    
    Parameters:
    - csv_file: Path to the CSV file
    - period: Number of periods for RSI calculation (default 14)
    
    Returns:
    - DataFrame with RSI column added
    """
    try:
        print(f"Calculating RSI for {os.path.basename(csv_file)}...")
        
        # Read the CSV file
        df = pd.read_csv(csv_file, header=[0, 1], index_col=0, parse_dates=True)
        
        # Get the ticker symbol
        ticker = df.columns[0][1]
        
        # Access the Close price column
        close_col = ('Price', ticker) if 'Price' in df.columns.levels[0] else ('Close', ticker)
        
        # Calculate RSI
        df[(f'RSI_{period}', ticker)] = calculate_rsi(df, close_col, period)
        
        print(f"  ✓ RSI_{period} calculated")
        
        # Save back to the same file
        df.to_csv(csv_file)
        print(f"✓ {os.path.basename(csv_file)}: RSI indicator saved\n")
        
        return df
        
    except Exception as e:
        print(f"✗ Error processing {os.path.basename(csv_file)}: {str(e)}\n")
        return None

# Example usage
if __name__ == "__main__":
    # Single file
    add_rsi_to_file('stock_data/AAPL.csv', period=14)
    
    # Or process multiple files
    # import json
    # with open('tickers.json', 'r') as f:
    #     tickers = json.load(f)
    # for ticker in tickers:
    #     add_rsi_to_file(f'stock_data/{ticker}.csv')