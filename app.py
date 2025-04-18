from flask import Flask, request, jsonify
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

NEWS_API_KEY = os.getenv("NEWS_API_KEY")

@app.route("/sentiment", methods=["POST"])
def get_sentiment():
    data = request.get_json()
    coin = data.get("coin_name", "BTC")

    reddit_sentiment = fetch_reddit_sentiment(coin)
    news_sentiment = fetch_news_sentiment(coin)

    combined_sentiment = f"Reddit: {reddit_sentiment}, News: {news_sentiment}"

    return jsonify({
        "sentiment": combined_sentiment
    })

def fetch_reddit_sentiment(coin):
    url = f"https://www.reddit.com/r/cryptocurrency/search.json?q={coin}&restrict_sr=on&limit=50"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        posts = response.json().get("data", {}).get("children", [])
        comments = [post["data"]["title"] for post in posts]
        score = sum([1 if any(word in comment.lower() for word in ["buy", "moon", "up", "bullish", "pump"])
                     else -1 for comment in comments])
        return "Positive" if score > 0 else "Negative" if score < 0 else "Neutral"
    except Exception as e:
        print(f"Reddit error: {e}")
        return "Neutral"

def fetch_news_sentiment(coin):
    url = f"https://newsapi.org/v2/everything?q={coin}&apiKey={NEWS_API_KEY}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        articles = response.json().get("articles", [])[:10]
        score = sum([1 if any(word in article["title"].lower() for word in ["rise", "surge", "gain", "bull"])
                     else -1 for article in articles])
        return "Positive" if score > 0 else "Negative" if score < 0 else "Neutral"
    except Exception as e:
        print(f"News error: {e}")
        return "Neutral"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
