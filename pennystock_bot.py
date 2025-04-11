import requests
from bs4 import BeautifulSoup
from textblob import TextBlob
import praw

# --- Reddit API Setup ---
reddit = praw.Reddit(
    client_id="bM8tQtBcpv4ZoLcWqTx3ug",
    client_secret="IqU9vfQuLdSnLWfz-e6slg1AyxzzLw",
    user_agent="penny_stock_bot by u/0ccamChainsaw"
)

# --- Discord Webhook ---
DISCORD_WEBHOOK = "https://discordapp.com/api/webhooks/1360244154738671656/C4jBt7yLfRBHHS7i1gVZZJrFJbk9Kh3KEc0RAkvjlTXDcQ1VrUCIC-xK7ZISsawmhG0u"

# --- Google News Scraper ---
def get_google_news(ticker):
    url = f'https://news.google.com/search?q={ticker}%20stock&hl=en-US&gl=US&ceid=US:en'
    headers = {'User-Agent': 'Mozilla/5.0'}
    soup = BeautifulSoup(requests.get(url, headers=headers).text, 'html.parser')
    headlines = [a.text for a in soup.select('article h3')]
    return headlines[:5]

# --- Reddit Sentiment Analyzer ---
def get_reddit_sentiment(ticker):
    subreddit = reddit.subreddit('pennystocks')
    results = []
    for post in subreddit.search(ticker, limit=10):
        sentiment = TextBlob(post.title).sentiment.polarity
        results.append((post.title, sentiment))
    return sorted(results, key=lambda x: x[1], reverse=True)

# --- Discord Notification ---
def send_discord_alert(message):
    data = {"content": message}
    response = requests.post(DISCORD_WEBHOOK, json=data)
    if response.status_code == 204:
        print("✅ Discord alert sent!")
    else:
        print("❌ Failed to send alert:", response.text)

# --- Main Execution ---
if __name__ == "__main__":
    ticker = input("Enter a ticker symbol (e.g., HUSA, CEI): ").upper()

    print(f"\n📰 Top News for {ticker}:")
    headlines = get_google_news(ticker)
    for h in headlines:
        print(f"- {h}")
    if headlines:
        send_discord_alert(f"📰 **Top news for ${ticker}:**\n" + "\n".join(f"- {h}" for h in headlines))

    print(f"\n💬 Reddit Sentiment for {ticker}:")
    reddit_posts = get_reddit_sentiment(ticker)
    for post, sentiment in reddit_posts:
        print(f"{round(sentiment, 2)}: {post}")
        if sentiment > 0.5:
            send_discord_alert(f"🚨 **Bullish Reddit Post on ${ticker}:**\n> {post}\n👍 Sentiment: {round(sentiment, 2)}")
