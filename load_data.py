import yfinance as yf
import pandas as pd
import os
import json
from datetime import datetime, timedelta

def load_tickers_from_json(json_file='tickers.json'):
    """
    Load ticker symbols from a JSON file.
    
    Expected JSON format:
    ["AAPL", "GOOGL", "MSFT"]
    
    or
    
    {
        "tickers": ["AAPL", "GOOGL", "MSFT"]
    }
    """
    try:
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        # Handle both list format and dict format
        if isinstance(data, list):
            return data
        elif isinstance(data, dict) and 'tickers' in data:
            return data['tickers']
        else:
            raise ValueError("JSON file must contain a list of tickers or a dict with 'tickers' key")
    
    except FileNotFoundError:
        print(f"Error: {json_file} not found.")
        return []
    except json.JSONDecodeError:
        print(f"Error: {json_file} is not valid JSON.")
        return []

def fetch_and_store_ticker_data(tickers, data_dir='stock_data', years=10):
    """
    Fetch last N years of stock data and store incrementally in CSV files.
    
    Parameters:
    - tickers: list of ticker symbols (e.g., ['AAPL', 'GOOGL', 'MSFT'])
    - data_dir: directory to store CSV files
    - years: number of years of historical data to fetch
    """
    
    # Create directory if it doesn't exist
    os.makedirs(data_dir, exist_ok=True)
    
    # Calculate start date
    end_date = datetime.now()
    start_date = end_date - timedelta(days=years*365)
    
    for ticker in tickers:
        csv_file = os.path.join(data_dir, f'{ticker}.csv')
        
        try:
            # Check if CSV already exists
            if os.path.exists(csv_file):
                print(f"Loading existing data for {ticker}...")
                existing_data = pd.read_csv(csv_file, index_col=0, parse_dates=True)
                
                # Get the last date in existing data
                last_date = existing_data.index.max()
                
                # Fetch only new data from the day after last date
                fetch_start = last_date + timedelta(days=1)
                
                # Skip if data is already up to date
                if fetch_start.date() >= end_date.date():
                    print(f"{ticker}: Data is already up to date.")
                    continue
                
                print(f"{ticker}: Fetching data from {fetch_start.date()} to {end_date.date()}...")
                new_data = yf.download(ticker, start=fetch_start, end=end_date, progress=False)
                
                if not new_data.empty:
                    # Combine and remove duplicates
                    combined_data = pd.concat([existing_data, new_data])
                    combined_data = combined_data[~combined_data.index.duplicated(keep='last')]
                    combined_data.sort_index(inplace=True)
                    
                    # Save to CSV
                    combined_data.to_csv(csv_file)
                    print(f"{ticker}: Added {len(new_data)} new rows. Total: {len(combined_data)} rows.")
                else:
                    print(f"{ticker}: No new data available.")
            
            else:
                # Fetch full historical data
                print(f"{ticker}: Fetching full {years}-year history from {start_date.date()} to {end_date.date()}...")
                data = yf.download(ticker, start=start_date, end=end_date, progress=False)
                
                if not data.empty:
                    data.to_csv(csv_file)
                    print(f"{ticker}: Saved {len(data)} rows to {csv_file}")
                else:
                    print(f"{ticker}: No data available.")
        
        except Exception as e:
            print(f"Error processing {ticker}: {str(e)}")
            continue
    
    print("\nData fetch complete!")

# Example usage
if __name__ == "__main__":
    # Load tickers from JSON file
    tickers = load_tickers_from_json('config/tickers.json')
    
    if tickers:
        print(f"Loaded {len(tickers)} tickers: {tickers}\n")
        
        # Fetch and store data
        fetch_and_store_ticker_data(tickers, data_dir='stock_data', years=10)
    else:
        print("No tickers loaded. Please check your tickers.json file.")
    
    # To update data later, just run the same script again
    # It will only fetch new data since the last update