# Stock Alert System

An A-level Computer Science NEA project by Daniel Grimason. This Python desktop application lets users create an account, build a stock watchlist, retrieve market data, view candlestick charts and assess the sentiment of recent financial news.

## Features

- Tkinter desktop interface
- Registration and login with bcrypt password hashing
- Email-based one-time password verification
- MySQL-backed user accounts, watchlists and price history
- Market data retrieved with `yfinance`
- Candlestick charts using `mplfinance`
- News sentiment analysis using a Hugging Face transformer model

## Technology

Python, Tkinter, MySQL, pandas, yfinance, matplotlib, mplfinance, bcrypt, Beautiful Soup and Transformers.

## Running the project

1. Install Python 3.11 or later and MySQL.
2. Create and activate a virtual environment.
3. Install the dependencies:

```bash
pip install -r requirements.txt
```

4. Set the database environment variables shown in `.env.example`.
5. To enable email OTP, set `SMTP_SENDER` and `SMTP_APP_PASSWORD`.
6. Create the database tables:

```bash
python setup_database.py
```

7. Start the desktop application:

```bash
python using_tkinter_for_gui.py
```

## Project structure

- `using_tkinter_for_gui.py`: desktop interface and navigation
- `setup_database.py`: database creation and initial ticker setup
- `querys.py`: database queries
- `stock_data_pulling.py`: market-data retrieval and storage
- `otp_management.py`: email OTP generation and validation
- `assess_sentiment_with_news.py`: financial-news sentiment workflow
- `schema.sql`: clean database schema with no user records

## Privacy and security

This public version has been cleaned before publication. Personal email addresses, credentials, authentication bypasses and database records from the original school submission have been removed. The original database dump is deliberately excluded.

## Academic context

Developed independently as an AQA A-level Computer Science non-exam assessment at Methodist College Belfast. The repository is retained as a portfolio record of the completed project.
