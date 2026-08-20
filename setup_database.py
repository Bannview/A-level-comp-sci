import mysql.connector
import yfinance as yf

import os

DATABASE_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "stock_alert_system"),
}

INITIAL_TICKERS = ['AAPL', 'GOOGL', 'MSFT', 'TSLA']

def get_db_connection():
    try:
        conn = mysql.connector.connect(**DATABASE_CONFIG)
        return conn
    except mysql.connector.Error as err:
        print(f"Error connecting to database: {err}")
        return None

def create_tables(cursor):
    # Create symbol table
    symbol_table_query = """
    CREATE TABLE IF NOT EXISTS symbol (
        symbol_id INT AUTO_INCREMENT PRIMARY KEY,
        ticker VARCHAR(10) UNIQUE NOT NULL,
        name VARCHAR(255)
    )
    """
    cursor.execute(symbol_table_query)
    print("Table 'symbol' checked/created.")

    # Create stock_price table
    stock_price_table_query = """
    CREATE TABLE IF NOT EXISTS stock_price (
        id INT AUTO_INCREMENT PRIMARY KEY,
        symbol_id INT,
        timestamp DATETIME,
        open DECIMAL(10, 2),
        high DECIMAL(10, 2),
        low DECIMAL(10, 2),
        close DECIMAL(10, 2),
        volume BIGINT,
        FOREIGN KEY (symbol_id) REFERENCES symbol(symbol_id),
        UNIQUE KEY unique_price (symbol_id, timestamp)
    )
    """
    user_table_query = """
    CREATE TABLE IF NOT EXISTS users(
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    password_salt VARCHAR(255) NOT NULL,
    role ENUM('Standard','Admin','Owner') DEFAULT 'Standard',
    failed_login_attempts INT DEFAULT 0,
    lock_until DATETIME DEFAULT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP);
    """
    cursor.execute(stock_price_table_query)
    print("Table 'stock_price' checked/created.")
    cursor.execute(user_table_query)
    print("Table 'users' checked/created.")

    userSymbol_table_query = '''
    CREATE TABLE IF NOT EXISTS userSymbol (
    user_id INT,
    symbol_id INT,
    PRIMARY KEY (user_id, symbol_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (symbol_id) REFERENCES symbol(symbol_id)
    )
'''
    cursor.execute(userSymbol_table_query)
    print("Table 'userSymbol' checked/created.")

def populate_symbols(conn, cursor, tickers_to_populate):
    print("Populating initial symbols...")
    
    for ticker in tickers_to_populate:
        # Check if exists
        cursor.execute("SELECT symbol_id FROM symbol WHERE ticker = %s", (ticker,))
        result = cursor.fetchone()
        
        if result:
            print(f"Ticker {ticker} already exists.")
            continue
            
        print(f"Fetching data for {ticker}...")
        try:
            # Fetch company name from yfinance
            tkr = yf.Ticker(ticker)
            # Try to get the long name, fall back to short name, or just use ticker
            company_name = tkr.info.get('longName', tkr.info.get('shortName', ticker))
            
            cursor.execute(
                "INSERT INTO symbol (ticker, name) VALUES (%s, %s)",
                (ticker, company_name)
            )
            print(f"Added {ticker} ({company_name}) to database.")
            conn.commit()
            
        except Exception as e:
            print(f"Failed to fetch/add {ticker}: {e}")
            # Fallback insert if yfinance fails but we want the ticker anyway? 
            # ideally we retry or skip. For now, let's skip.


def setup_database_main():
    conn = get_db_connection()
    if not conn:
        return
    
    cursor = conn.cursor()
    
    try:
        create_tables(cursor)
        populate_symbols(conn, cursor, INITIAL_TICKERS)
        print("Database setup completed successfully.")
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    setup_database_main()
