import setup_database
import stock_data_pulling
import mysql.connector
from querys import get_user_id, get_symbol_id

def link_user_to_ticker(email, ticker):
    user_id = get_user_id(email)
    symbol_id = get_symbol_id(ticker)
    
    if not user_id:
        print(f"User with email {email} not found.")
        return False
    if not symbol_id:
        print(f"Symbol {ticker} not found.")
        return False

    conn = setup_database.get_db_connection()
    if not conn:
        return False
    
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT IGNORE INTO userSymbol (user_id, symbol_id) VALUES (%s, %s)", (user_id, symbol_id))
        conn.commit()
        print(f"Successfully linked {ticker} to {email}.")
        return True
    except mysql.connector.Error as err:
        print(f"Database error linking ticker: {err}")
        return False
    finally:
        cursor.close()
        conn.close()

def add_ticker(ticker): #ticker should be a string 
    conn = setup_database.get_db_connection()
    if not conn:
        return
    
    cursor = conn.cursor()

    try:
        setup_database.populate_symbols(conn, cursor, [ticker])
        print(f"Successfully added {ticker} to database.")
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
    finally:
        cursor.close()
        conn.close()

def main():
    add_ticker(input("Enter ticker to add: ").upper())  #asks for user input and uppercases it
    stock_data_pulling.fetch_stock_data()

if __name__ == "__main__":
    main()
