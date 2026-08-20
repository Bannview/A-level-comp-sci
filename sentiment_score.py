from transformers import pipeline
import requests
from bs4 import BeautifulSoup

'''
# This downloads a default pre-trained sentiment model automatically
sentiment_pipeline = pipeline("sentiment-analysis")

data = ["I love this product!", "The shipping was terrible."]
results = sentiment_pipeline(data)

print(results)
# Output: [{'label': 'POSITIVE', 'score': 0.99}, {'label': 'NEGATIVE', 'score': 0.99}]
'''

sentiment = pipeline("sentiment-analysis", model="spacesedan/sentiment-analysis-longformer", tokenizer="spacesedan/sentiment-analysis-longformer", truncation=True)

def positivity_score(text: str) -> float: #output --> {"label":Positive/Negative, "score":probability}
    text = (text or "").strip()
    if not text:
        return 0.5  #default

    output = sentiment(text)[0]  
    if output["label"].upper() == "POSITIVE":
        return float(output["score"])
    else:
        return 1.0 - float(output["score"])


def get_news_data(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    } #attempting to not look like a bot scraping
    try:
        response = requests.get(url, headers=headers, timeout=10)
    except requests.RequestException as e:
        print(f"Request failed for {url}: {e}")
        return None

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        headline = soup.find('h1').text
        
        paragraphs = [p.text for p in soup.find_all('p')]
        full_text = " ".join(paragraphs)

        return full_text
    else:
        return None

if __name__ == "__main__":
    while True:
        url = input("Enter a URL: ").strip()
        if url:
            get_news_data(url)
        else:
            print("Please enter a valid URL.")
