import os
import mysql.connector
import yfinance as yf
import matplotlib.pyplot as plt

def get_db_connection():
    try:
        return mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", ""),
            database=os.getenv("DB_NAME", "stock_alert_system"),
        )
    except mysql.connector.Error as err:
        print(f"Error connecting to database: {err}")
        return None

def get_watched_symbols():
    """Returns a dict: {ticker: symbol_id}"""
    print("Fetching list of symbols to watch from database...")
    conn = get_db_connection()
    if not conn:
        print("Failed to get DB connection for symbols.")
        return {}
    
    cursor = conn.cursor()
    try:
        query = "SELECT symbol_id, ticker FROM symbol"
        cursor.execute(query)
        symbols = cursor.fetchall()
        print(f"Successfully retrieved {len(symbols)} symbols from database.")
        return {row[1]: row[0] for row in symbols}
    except mysql.connector.Error as err:
        print(f"Error executing symbol fetch query: {err}")
        return {}
    finally:
        cursor.close()
        conn.close()

def fetch_stock_data_from_db(symbol_id, period="1mo", interval="1d"):
    """Fetches stock data from the database for a given symbol_id."""
    print(f"Fetching data for symbol_id {symbol_id} from database...")
    conn = get_db_connection()
    if not conn:
        print("Failed to get DB connection for data fetch.")
        return None
    
    cursor = conn.cursor()
    try:
        query = """
        SELECT timestamp, open, high, low, close, volume 
        FROM stock_price 
        WHERE symbol_id = %s 
        AND timestamp >= DATE_SUB(NOW(), INTERVAL %s) 
        AND interval = %s
        ORDER BY timestamp ASC
        """
        cursor.execute(query, (symbol_id, period, interval))
        rows = cursor.fetchall()
        
        if not rows:
            print(f"No data found in database for symbol_id {symbol_id} with period {period} and interval {interval}.")
            return None
        
        print(f"Successfully retrieved {len(rows)} records from database.")
        return rows
    except mysql.connector.Error as err:
        print(f"Error fetching stock data from database: {err}")
        return None
    finally:
        cursor.close()
        conn.close()

def plot_stock_data(symbol_id, ticker, data, period="1mo", interval="1d"):
    """Plots the stock data using matplotlib."""
    if not data:
        print("No data available to plot.")
        return
    
    # Separate the data into lists
    timestamps = [row[0] for row in data]
    opens = [row[1] for row in data]
    highs = [row[2] for row in data]
    lows = [row[3] for row in data]
    closes = [row[4] for row in data]
    volumes = [row[5] for row in data]
    
    # Create the plot
    plt.figure(figsize=(12, 6))
    
    # Plot the closing prices
    plt.plot(timestamps, closes, label='Close Price', color='blue')
    
    # Add more details if interval is small
    if interval in ["1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h"]:
        plt.plot(timestamps, opens, label='Open Price', color='orange', linestyle='--')
        plt.plot(timestamps, highs, label='High Price', color='green', linestyle='--')
        plt.plot(timestamps, lows, label='Low Price', color='red', linestyle='--')
    
    # Add volume if available
    if volumes:
        plt.bar(timestamps, volumes, label='Volume', color='gray', alpha=0.3)
    
    # Add titles and labels
    plt.title(f'{ticker} Stock Data ({period} - {interval})')
    plt.xlabel('Timestamp')
    plt.ylabel('Price / Volume')
    plt.legend()
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    # Show the plot
    plt.show()

def main():
    # Get connected to database
    conn = get_db_connection()
    if not conn:
        return
    
    # Look at the symbol table and see all saved stocks then return [symbol_id, ticker]
    symbol_map = get_watched_symbols()
    if not symbol_map:
        print("No symbols found in database.")
        return
    
    # Take in the symbols wanted by user
    print("\nAvailable symbols:")
    for ticker, symbol_id in symbol_map.items():
        print(f"  {symbol_id}: {ticker}")
    
    symbols_wanted = input("\nEnter the symbol IDs you want to view data for (comma separated): ")
    symbol_ids = [int(id.strip()) for id in symbols_wanted.split(',') if id.strip().isdigit()]
    
    # Get period and interval from user
    period = input("Enter the period (e.g., 1mo, 3mo, 1y): ")
    interval = input("Enter the interval (e.g., 1d, 1wk, 1mo): ")
    
    # Fetch and plot data for each symbol
    for symbol_id in symbol_ids:
        if symbol_id in symbol_map.values():
            ticker = [t for t, i in symbol_map.items() if i == symbol_id][0]
            
            # Fetch data from database
            data = fetch_stock_data_from_db(symbol_id, period, interval)
            
            # Plot the data
            if data:
                plot_stock_data(symbol_id, ticker, data, period, interval)
        else:
            print(f"Symbol ID {symbol_id} not found.")

if __name__ == "__main__":
    main() 