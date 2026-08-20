import os

DATABASE_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "stock_alert_system"),
}

def get_db_connection():
    try:
        import mysql.connector
        # get and return connection to database 
        #using ** before DATABASE_CONFIG unpacks the dictionary
        connection = mysql.connector.connect(**DATABASE_CONFIG)
        return connection
    except mysql.connector.Error as err:
        print(f"Error connecting to database: {err}")
        return 

def get_watched_symbols():
    # get all ticker symbols from the db

    conn = get_db_connection()
    if not conn:
        return
    
    cursor = conn.cursor()
    query = "SELECT symbol_id, ticker FROM symbol"
    cursor.execute(query)
    symbols = cursor.fetchall()
    cursor.close()
    conn.close()

    #return as a dict... {ticker: symbol_id}
    return {row[1]: row[0] for row in symbols}

def fetch_stock_data():
    print("in fetch_stock_data filename pulling_down_ticker_data_from_yfinance_api.py")

    symbol_map = get_watched_symbols()
    print(f"symbol_map --> {symbol_map}")
    if not symbol_map:
        print("No symbols to watch.")
        return
    
    tickers = list(symbol_map.keys())
    print(f"Fetching data for tickers: {tickers}")
    
    import yfinance as yf

    try:
        data = yf.download(tickers=tickers, period="1d", interval="1m", group_by='ticker', threads=True, progress=False)
    except Exception as e:
        print(f"YFinance data download error: {e}")

    conn = get_db_connection()
    if not conn:
        return
    cursor = conn.cursor()

    for ticker_name, symbol_id in symbol_map.items():
        if len(tickers) == 1:
            ticker_data = data  
        else:
            if ticker_name not in data:
                print(f"No data for ticker: {ticker_name}")
                continue #skip storing this tickers data and move to next
            ticker_data = data[ticker_name]

        if ticker_data.empty == True:
            continue
        
        last_row = ticker_data.iloc[-1] #iloc gets row by index
        # yfinance has its first colum as the timestamp e.g. 09.32.00
        # timestamp--open--high--low--close--volume
        # therefore we take the .name of said last row and turn it into a python datetime variable to store.
        timestamp = last_row.name.to_pydatetime()