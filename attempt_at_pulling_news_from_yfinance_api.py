import yfinance as yf
from datetime import datetime
from sentiment_score import *
import csv

def get_ticker_news(ticker_symbol):
    """
    Fetches and displays news for a given stock ticker using yfinance.
    """
    try:
        ticker = yf.Ticker(ticker_symbol)
        news_list = ticker.news   
        if not news_list:
            print(f"No news found for {ticker_symbol}.")
            return
        print(f"\n--- News for {ticker_symbol.upper()} ---\n")
        news = []
        for item in news_list:
            content = item.get('content', {})
            if not content:
                continue
            
            title = content.get('title', 'No Title')
            
            provider = content.get('provider', {})
            publisher = provider.get('displayName', 'Unknown Publisher')
            
            pub_date_str = content.get('pubDate', 'Unknown Date')
            
            try:
                dt = datetime.strptime(pub_date_str, '%Y-%m-%dT%H:%M:%SZ')
                publish_date = dt.strftime('%Y-%m-%d %H:%M:%S')
            except ValueError:
                 publish_date = pub_date_str

            temp_url = content.get('canonicalUrl', {})
            link = temp_url.get('url', 'No Link')

            news.append({"title":title, "publisher":publisher, "publish_date":publish_date, "link":link})
        return news
    except Exception as e:
        print(f"An error occurred while fetching news: {e}")

def main():
    tickers = [
    "NVDA", "MSFT", "AAPL", "AMZN", "GOOGL", "TSLA",
    "JPM", "CAT", "WMT", "KO", "LLY", "LMT",
    "RKLB", "GEV", "QBTS", "NBIS", "AUR",
    "SPY", "QQQ", "DIA"
]
    failed_urls = []
    accepted_urls = []
    for ticker in tickers:
#    ticker_input = input("Enter a stock ticker (e.g., AAPL, TSLA): ").strip()
    
        if ticker:
            ticker_data = get_ticker_news(ticker)
            
            if ticker_data:
                print(ticker_data)
                for i in ticker_data:
                    # news items might lack 'link', handle gracefully? 
                    # The current code assumes 'link' key exists. 
                    # Based on get_ticker_news implementation, it should exist.
                    if get_news_data(i["link"]):
                        print("Data retrieved")
                        accepted_urls.append(i["link"])
                    else:
                        failed_urls.append(i["link"])
                        print("Data not retrieved")
                print(failed_urls)
                # Avoid division by zero if len(ticker_data) is 0 (though if ticker_data is true, likely > 0)
                total = len(ticker_data)
                if total > 0:
                    print(f"Number of accepted urls: {len(accepted_urls)}")
                    print(f"Number of failed urls: {len(failed_urls)}")
                    print(f"Total number of urls: {total}")
                    print(f"Percentage of accepted urls: {len(accepted_urls)/total*100}%")
                    print(f"Percentage of failed urls: {len(failed_urls)/total*100}%")

                # Write to files as requested
                with open("accepted_urls.txt", "a") as f:
                    for url in accepted_urls:
                        f.write(url + "\n")
                
                with open("failed_urls.txt", "a") as f:
                    for url in failed_urls:
                        f.write(url + "\n")

                print("\n\n\n")
                print("Accepted urls:")
                for i in accepted_urls:
                    print(i + "\n")
                print("\n\n\n")
                print("Failed urls:")
                for i in failed_urls:
                    print(i + "\n")
            else:
                 print(f"No data returned for {ticker}")
        else:
            print("Please enter a valid ticker symbol.")

if __name__ == "__main__":
        main()