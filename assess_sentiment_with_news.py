from sentiment_score import *
from attempt_at_pulling_news_from_yfinance_api import *

def assess_sentiment(ticker):      
    news = get_ticker_news(ticker)
    if not news:
        print(f"No news found for {ticker}")
        return [0.5, "Neutral (No News)", []]

#failed when attempting to scrape so will skip these below        
    BLOCKED_DOMAINS = [
        "finance.yahoo.com",
        "wsj.com", 
        "barrons.com",
        "thestreet.com",
        "investopedia.com",
        "etf.com"
    ]

    sentiment_scores = []
    for i in news:
        link = i.get("link")
        if not link:
            continue
            
        # Check for blocked domains
        is_blocked = False
        for domain in BLOCKED_DOMAINS:
            if domain in link:
                #print(f"Skipping blocked domain: {domain} in {link}")
                is_blocked = True
                break
        if is_blocked:
            continue

        try:
            data = get_news_data(link)
            if data:
                score = positivity_score(data)
                sentiment_scores.append(score)
        except Exception as e:
            print(f"Error processing link {link}: {e}")

    if not sentiment_scores:
        print("No sentiment scores could be calculated.")
        return [0.5, "Neutral (No Data)", news]

    average_sentiment = sum(sentiment_scores) / len(sentiment_scores)
    print(f"Average sentiment score: {average_sentiment}")
    
    if average_sentiment > 0.7:
        label = "Super Positive"
    elif 0.6 < average_sentiment <= 0.7:
        label = "Slightly Positive"
    elif 0.4 <= average_sentiment <= 0.6:
        label = "Neutral"
    elif 0.3 < average_sentiment < 0.4:
        label = "Slightly Negative"
    else: #<= 0.3
        label = "Negative"

    print(label)
    return [average_sentiment, label, news]

if __name__ == "__main__":
    ticker = input("Enter a stock ticker (e.g., AAPL, TSLA): ").strip()
    if ticker:
        sentiment = assess_sentiment(ticker)
        print(f"The sentiment of {ticker} is {sentiment}")
    else:
        print("Please enter a valid ticker symbol.")