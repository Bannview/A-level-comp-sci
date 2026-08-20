import time
import mysql.connector
import yfinance as yf
from datetime import datetime

import os

DATABASE_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "stock_alert_system"),
}

# Configuration for data fetching
# Valid periods: [1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max]
FETCH_PERIOD = "1mo" 
# Valid intervals: [1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo]
FETCH_INTERVAL = "30m"

def get_db_connection():
    try:
        # print("Attempting to connect to database...") # left commented as it will clog up the logs.
        conn = mysql.connector.connect(**DATABASE_CONFIG)
        return conn
    except mysql.connector.Error as err:
        print(f"CRITICAL ERROR: Could not connect to database: {err}")
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

def save_stock_price(symbol_id, price_data):
    """Inserts price data into the database."""
    print(f"   -> Saving {len(price_data)} records for symbol_id {symbol_id}...")
    conn = get_db_connection()
    if not conn:
        print("   -> Failed to connect to DB for saving prices.")
        return

    cursor = conn.cursor()
    inserted_count = 0
    skipped_count = 0
    
    query = """
    INSERT IGNORE INTO stock_price 
    (symbol_id, timestamp, open, high, low, close, volume) 
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    
    try:
        if price_data.empty:
            print("   -> Dataframe is empty, nothing to save.")
            return

        # Clean the data by dropping any rows with NaN values
        price_data = price_data.dropna()
        
        if price_data.empty:
            print("   -> Dataframe is empty after dropping NaNs, nothing to save.")
            return

        # Iterate through the DataFrame
        for index, row in price_data.iterrows():
            # index is the timestamp
            ts = index.to_pydatetime()
            
            values = (
                symbol_id,
                ts,
                float(row['Open']),
                float(row['High']),
                float(row['Low']),
                float(row['Close']),
                int(row['Volume'])
            )
            cursor.execute(query, values)
            if cursor.rowcount > 0:
                inserted_count += 1
            else:
                skipped_count += 1
        
        conn.commit()
        print(f"   -> SUCCESS: Inserted {inserted_count} new records. (Skipped {skipped_count} duplicates)")
        
    except mysql.connector.Error as err:
        print(f"   -> MEMORY ERROR: Database error saving prices: {err}")
    except Exception as e:
        print(f"   -> PROCESS ERROR: Error processing data for save: {e}")
    finally:
        cursor.close()
        conn.close()

def fetch_stock_data():
    print("="*50)
    print(f"[{datetime.now()}] STARTING DATA FETCH CYCLE")
    print("="*50)
    
    symbol_map = get_watched_symbols()
    
    if not symbol_map:
        print("WARNING: No symbols found in database to watch. Exiting cycle.")
        return

    tickers = list(symbol_map.keys())
    print(f"Target Tickers: {tickers}")
    
    try:
        # Download data for all tickers at once
        print(f"Initiating YFinance Download (Period: {FETCH_PERIOD}, Interval: {FETCH_INTERVAL})...")
        start_time = time.time()
        data = yf.download(tickers=tickers, period=FETCH_PERIOD, interval=FETCH_INTERVAL, group_by='ticker', threads=True, progress=False)
        duration = time.time() - start_time
        print(f"Download completed in {duration:.2f} seconds.")
        
        if data.empty:
            print("WARNING: YFinance returned empty data. Check internet connection or market hours.")
            return

        print("Processing downloaded data...")
        for ticker, symbol_id in symbol_map.items():
            print(f"\nProcessing symbol: {ticker} (ID: {symbol_id})")
            try:
                if len(tickers) == 1:
                    ticker_data = data
                else:
                    # yfinance returns MultiIndex if multiple tickers
                    if ticker in data.columns.levels[0]: 
                         ticker_data = data[ticker]
                    else:
                         print(f"   -> No data found in response for {ticker}")
                         continue
                
                # Check if data is empty or all NaN
                if ticker_data.empty or ticker_data.dropna().empty:
                     print(f"   -> Data for {ticker} is empty or all NaNs.") #yfinance will return Nan for trading holidays or glitches so we remove.
                     continue
                
                save_stock_price(symbol_id, ticker_data)
                
            except Exception as e:
                print(f"   -> ERROR processing {ticker}: {e}")

    except Exception as e:
        print(f"FATAL ERROR during YFinance download: {e}")
            
    print("\n" + "="*50)
    print("CYCLE COMPLETE")
    print("="*50 + "\n")

def main():
    fetch_stock_data()

if __name__ == "__main__":
    main()