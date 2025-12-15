import json
import os
from ema_calc import add_ema_to_file
from macd_calc import add_macd_to_file
from rsi_calc import add_rsi_to_file

def process_all_tickers(data_dir='stock_data',
                       ema_periods=[12, 26, 50, 200],
                       macd_fast=12, macd_slow=26, macd_signal=9,
                       rsi_period=14):
    """
    Process all CSV files in the data directory and add technical indicators
    
    Parameters:
    - data_dir: Directory containing CSV files
    - ema_periods: List of EMA periods to calculate
    - macd_fast: MACD fast EMA period
    - macd_slow: MACD slow EMA period
    - macd_signal: MACD signal line period
    - rsi_period: RSI period
    """
    # Get all CSV files in the directory
    if not os.path.exists(data_dir):
        print(f"Error: Directory '{data_dir}' not found.")
        return
    
    csv_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
    
    if not csv_files:
        print(f"No CSV files found in '{data_dir}' directory.")
        return
    
    print(f"\n{'#'*60}")
    print(f"TECHNICAL INDICATORS CALCULATOR")
    print(f"{'#'*60}")
    print(f"Found {len(csv_files)} CSV files in '{data_dir}' directory")
    print(f"\nIndicators to calculate:")
    print(f"  - EMA: {', '.join(map(str, ema_periods))}")
    print(f"  - MACD: ({macd_fast}, {macd_slow}, {macd_signal})")
    print(f"  - RSI: {rsi_period}")
    print(f"{'#'*60}\n")
    
    # Process each file
    success_count = 0
    failed_files = []
    
    for csv_file in csv_files:
        file_path = os.path.join(data_dir, csv_file)
        ticker_name = csv_file.replace('.csv', '')
        
        print(f"{'='*60}")
        print(f"Processing: {csv_file}")
        print(f"{'='*60}")
        
        try:
            # Add EMA indicators
            add_ema_to_file(file_path, periods=ema_periods)
            
            # Add MACD indicators
            add_macd_to_file(file_path, fast=macd_fast, slow=macd_slow, signal=macd_signal)
            
            # Add RSI indicator
            add_rsi_to_file(file_path, period=rsi_period)
            
            print(f"✓ {csv_file}: All indicators calculated successfully!\n")
            success_count += 1
            
        except Exception as e:
            print(f"✗ {csv_file}: Error - {str(e)}\n")
            failed_files.append(csv_file)
    
    # Summary
    print(f"\n{'='*60}")
    print(f"PROCESSING COMPLETE")
    print(f"{'='*60}")
    print(f"Successfully processed: {success_count}/{len(csv_files)} files")
    
    if failed_files:
        print(f"Failed files: {', '.join(failed_files)}")
    
    print(f"{'='*60}\n")

# Example usage
if __name__ == "__main__":
    # Process all CSV files in stock_data directory
    process_all_tickers(
        data_dir='stock_data',
        ema_periods=[12, 26, 50, 200],
        macd_fast=12,
        macd_slow=26,
        macd_signal=9,
        rsi_period=14
    )