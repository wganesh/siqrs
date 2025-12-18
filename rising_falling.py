import pandas as pd
import matplotlib.pyplot as plt
import os
from pathlib import Path

def analyze_day_of_week_drops(csv_file, output_dir):
    """
    Analyze which day of the week the index falls most frequently.
    
    Args:
        csv_file: Path to the CSV file
        output_dir: Directory to save the output image
    """
    # Get the ticker name from filename
    ticker = Path(csv_file).stem
    
    try:
        # Read the data - first column is the index (Date)
        # Read first few rows to check structure
        df_check = pd.read_csv(csv_file, nrows=3)
        
        # Check if row 1 (index 0) contains ticker repeated across columns
        first_row_values = df_check.iloc[0].astype(str).values
        if any(ticker.upper() in val.upper() for val in first_row_values):
            # Ticker row exists, skip it
            df = pd.read_csv(csv_file, skiprows=[1], index_col=0)
        else:
            # No ticker row
            df = pd.read_csv(csv_file, index_col=0)
        
        # Remove any rows where the index is still "Date" (header got included)
        df = df[df.index != 'Date']
        
        # Convert index to datetime
        df.index = pd.to_datetime(df.index, errors='coerce')
        
        # Drop any rows with invalid dates
        df = df[df.index.notna()]
        
        # Convert Close to numeric
        df['Close'] = pd.to_numeric(df['Close'], errors='coerce')
        
        # Calculate daily returns (percentage change)
        df['Daily_Return'] = df['Close'].pct_change() * 100
        
        # Get day of week (0=Monday, 6=Sunday)
        df['Day_of_Week'] = df.index.dayofweek
        df['Day_Name'] = df.index.day_name()
        
        # Count falling days (negative returns) by day of week
        falling_days = df[df['Daily_Return'] < 0].groupby('Day_Name').size()
        
        # Count rising days (positive returns) by day of week
        rising_days = df[df['Daily_Return'] > 0].groupby('Day_Name').size()
        
        # Count total trading days by day of week
        total_days = df.groupby('Day_Name').size()
        
        # Calculate percentage of falling and rising days
        fall_percentage = (falling_days / total_days * 100).round(2)
        rise_percentage = (rising_days / total_days * 100).round(2)
        
        # Order days properly (Monday to Friday)
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        fall_percentage = fall_percentage.reindex([day for day in day_order if day in fall_percentage.index])
        rise_percentage = rise_percentage.reindex([day for day in day_order if day in rise_percentage.index])
        
        # Create the bar chart with 3 subplots
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 14))
        fig.suptitle(f'{ticker} - Day of Week Analysis', fontsize=16, fontweight='bold')
        
        # Chart 1: Percentage of falling days
        colors_fall = ['red' if x == fall_percentage.max() else 'steelblue' for x in fall_percentage]
        bars1 = ax1.bar(fall_percentage.index, fall_percentage.values, color=colors_fall, alpha=0.7, edgecolor='black')
        ax1.set_title('Percentage of Days with Price Decline by Day of Week', fontsize=14, pad=10)
        ax1.set_ylabel('Percentage (%)', fontsize=12)
        ax1.set_xlabel('Day of Week', fontsize=12)
        ax1.grid(True, alpha=0.3, axis='y')
        ax1.axhline(y=50, color='gray', linestyle='--', linewidth=1, alpha=0.5, label='50% baseline')
        
        # Add value labels on bars
        for bar in bars1:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.1f}%',
                    ha='center', va='bottom', fontsize=10, fontweight='bold')
        
        ax1.legend()
        
        # Chart 2: Percentage of rising days
        colors_rise = ['green' if x == rise_percentage.max() else 'lightgreen' for x in rise_percentage]
        bars2 = ax2.bar(rise_percentage.index, rise_percentage.values, color=colors_rise, alpha=0.7, edgecolor='black')
        ax2.set_title('Percentage of Days with Price Rise by Day of Week', fontsize=14, pad=10)
        ax2.set_ylabel('Percentage (%)', fontsize=12)
        ax2.set_xlabel('Day of Week', fontsize=12)
        ax2.grid(True, alpha=0.3, axis='y')
        ax2.axhline(y=50, color='gray', linestyle='--', linewidth=1, alpha=0.5, label='50% baseline')
        
        # Add value labels on bars
        for bar in bars2:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.1f}%',
                    ha='center', va='bottom', fontsize=10, fontweight='bold')
        
        ax2.legend()
        
        # Chart 3: Count of falling vs rising days
        falling_days_ordered = falling_days.reindex([day for day in day_order if day in falling_days.index], fill_value=0)
        rising_days_ordered = rising_days.reindex([day for day in day_order if day in rising_days.index], fill_value=0)
        
        x = range(len(falling_days_ordered))
        width = 0.35
        
        bars3 = ax3.bar([i - width/2 for i in x], falling_days_ordered.values, width, 
                        label='Falling Days', color='red', alpha=0.7, edgecolor='black')
        bars4 = ax3.bar([i + width/2 for i in x], rising_days_ordered.values, width,
                        label='Rising Days', color='green', alpha=0.7, edgecolor='black')
        
        ax3.set_title('Count of Rising vs Falling Days by Day of Week', fontsize=14, pad=10)
        ax3.set_ylabel('Number of Days', fontsize=12)
        ax3.set_xlabel('Day of Week', fontsize=12)
        ax3.set_xticks(x)
        ax3.set_xticklabels(falling_days_ordered.index)
        ax3.legend()
        ax3.grid(True, alpha=0.3, axis='y')
        
        # Add value labels
        for bars in [bars3, bars4]:
            for bar in bars:
                height = bar.get_height()
                ax3.text(bar.get_x() + bar.get_width()/2., height,
                        f'{int(height)}',
                        ha='center', va='bottom', fontsize=9)
        
        plt.tight_layout()
        
        # Save the figure
        output_path = os.path.join(output_dir, f'{ticker}_day_analysis.png')
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        # Print statistics
        print(f"\n{'='*60}")
        print(f"Day of Week Analysis for {ticker}")
        print(f"{'='*60}")
        print(f"\nPercentage of days with price decline:")
        for day, pct in fall_percentage.items():
            print(f"  {day:12s}: {pct:5.2f}%")
        print(f"\nPercentage of days with price rise:")
        for day, pct in rise_percentage.items():
            print(f"  {day:12s}: {pct:5.2f}%")
        print(f"\nMost likely to fall: {fall_percentage.idxmax()} ({fall_percentage.max():.2f}%)")
        print(f"Most likely to rise: {rise_percentage.idxmax()} ({rise_percentage.max():.2f}%)")
        print(f"\n✓ Chart saved as {ticker}_day_analysis.png")
        print(f"{'='*60}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error processing {ticker}: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function to analyze day of week patterns for SPY."""
    
    # Define directories and file
    input_dir = 'stock_data'
    output_dir = 'signals'
    spy_file = 'SPY.csv'
    
    # Check if input directory exists
    if not os.path.exists(input_dir):
        print(f"Error: '{input_dir}' directory not found!")
        return
    
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created '{output_dir}' directory")
    
    # Check if SPY.csv exists
    spy_path = os.path.join(input_dir, spy_file)
    if not os.path.exists(spy_path):
        print(f"Error: '{spy_file}' not found in '{input_dir}' directory!")
        return
    
    print(f"\nAnalyzing {spy_file}...\n")
    
    # Process SPY file
    analyze_day_of_week_drops(spy_path, output_dir)

if __name__ == "__main__":
    main()