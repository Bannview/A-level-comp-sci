from pulling_down_ticker_data_from_yfinance_api import get_db_connection
from setup_database import *
from login import *

def sql_login(raw_email, raw_password):
    #print("STARTING sql_login")
    conn = get_db_connection()
    if not conn:
        print("Connection failed")
        return False
    cursor = conn.cursor()
    query = "SELECT * FROM users WHERE email = %s"
    cursor.execute(query, (raw_email,))
    result = cursor.fetchone()
    if result:
        salt = result[3]
        hashed_password = result[2]
        if check_password(raw_password, salt, hashed_password):
            print("LOGIN DETAILS ARE CORRECT")
            return True
        else:
            return False
    else:
        return False

def get_symbol_id(ticker):
    conn = get_db_connection()
    if not conn:
        return None
    cursor = conn.cursor()
    query = "SELECT symbol_id FROM symbol WHERE ticker = %s"
    cursor.execute(query, (ticker,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    if result:
        return result[0]
    else:
        return None

def show_stock_data(symbol_id):
    print("in show_stock_data")
    conn = get_db_connection()
    if not conn:
        print('connection failed')
        return None
    cursor = conn.cursor()
    query = "SELECT * FROM stock_price WHERE symbol_id = %s ORDER BY timestamp DESC LIMIT 1"
    cursor.execute(query, (symbol_id,))
    result = cursor.fetchone()
    print(f"result --> {result}")
    if result:
        return result
    else:
        return None

def get_user_id(email):
    conn = get_db_connection()
    if not conn:
        return None
    cursor = conn.cursor()
    query = "SELECT user_id FROM users WHERE email = %s"
    cursor.execute(query, (email,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    if result:
        return result[0]
    else:
        return None

def check_user_watchlist_for_symbol_id(user_id, symbol_id):
    conn = get_db_connection()
    if not conn:
        return None
    cursor = conn.cursor()
    query = "SELECT * FROM userSymbol WHERE user_id = %s AND symbol_id = %s"
    cursor.execute(query, (user_id, symbol_id))
    result = cursor.fetchone()
    if result:
        return True
    else:
        return False

def get_user_symbolids(email):
    user_id = get_user_id(email)
    if not user_id:
        return []
    
    conn = get_db_connection()
    if not conn:
        return []
    
    cursor = conn.cursor()
    query = "SELECT symbol_id FROM userSymbol WHERE user_id = %s"
    try:
        cursor.execute(query, (user_id,))
        result = cursor.fetchall() # Get all rows
        if result:
            # Flatten list of tuples [(1,), (2,)] -> [1, 2]
            return [row[0] for row in result]
        else:
            return []
    except Exception as e:
        print(f"Error fetching user symbols: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

def get_ticker_company_from_symbol_id(symbol_ids):
    if not symbol_ids:
        return []
        
    return_list = []
    conn = get_db_connection()
    if not conn:
        return []
    
    cursor = conn.cursor()
    try:
        query = "SELECT ticker, name FROM symbol WHERE symbol_id = %s"
        for symbol_id in symbol_ids:
            cursor.execute(query, (symbol_id,))
            result = cursor.fetchone()
            if result:
                return_list.append(result) # tuple (ticker, name)
    except Exception as e:
        print(f"Error fetching ticker info: {e}")
    finally:
        cursor.close()
        conn.close()
        
    return return_list

def get_stock_data_with_ticker(ticker, email):
    print("in get_stock_data_with_ticker")
    symbol_id = get_symbol_id(ticker)
    user_id = get_user_id(email)
    print(f"symbol_id --> {symbol_id}")
    print(f"user_id --> {user_id}")
    in_users_watchlist = check_user_watchlist_for_symbol_id(user_id, symbol_id)
    print(f"in_users_watchlist --> {in_users_watchlist}")
    if in_users_watchlist:
        stock_data = show_stock_data(symbol_id)
        return stock_data
    else:
        return None

def get_company_name(ticker):
    conn = get_db_connection()
    if not conn:
        return None
    cursor = conn.cursor()
    query = "SELECT name FROM symbol WHERE ticker = %s"
    cursor.execute(query, (ticker,))
    result = cursor.fetchone()
    if result:
        print(f"DEBUG company name result[0] --> {result[0]}")
        return result[0]
    else:
        return None

def sql_register(email, hashed_password, salt):
    conn = get_db_connection()
    if not conn:
        return False
    cursor = conn.cursor()
    query = "INSERT INTO users (email, password_hash, password_salt) VALUES (%s, %s, %s)"
    cursor.execute(query, (email, hashed_password, salt))
    conn.commit()
    cursor.close()
    conn.close()
    return True

def check_if_user_registered(email):
    conn = get_db_connection()
    if not conn:
        return False
    cursor = conn.cursor()
    query = "SELECT * FROM users WHERE email = %s"
    cursor.execute(query, (email,))
    result = cursor.fetchone()
    if result:
        return True
    else:
        return False
    cursor.close()
    conn.close()

def update_password(email, hashed_password, salt):
    conn = get_db_connection()
    if not conn:
        return False
    cursor = conn.cursor()
    query = "UPDATE users SET password_hash = %s, password_salt = %s WHERE email = %s"
    try:
        cursor.execute(query, (hashed_password, salt, email))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error updating password: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def get_stock_history_with_ticker(ticker, email, limit=60):
    symbol_id = get_symbol_id(ticker)
    user_id = get_user_id(email)

    if not symbol_id or not user_id:
        return []
    
    if not check_user_watchlist_for_symbol_id(user_id, symbol_id):
        return []
    
    conn = get_db_connection()
    if not conn:
        return []
    
    cursor = conn.cursor()
    query = """
    SELECT
        timestamp,
        open,
        high,
        low,
        close,
        volume
    FROM stock_price
    WHERE symbol_id = %s
    ORDER BY timestamp DESC
    limit %s
    """

    try:
        cursor.execute(query, (symbol_id, limit))
        rows = cursor.fetchall()
        return list(reversed(rows))
    except Exception as e:
        print(f"Error fetching stock history: {e}")
    finally:
        cursor.close()
        conn.close()