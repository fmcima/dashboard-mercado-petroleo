import yfinance as yf
import feedparser
import logging
import socket
from datetime import datetime
try:
    from execution.utils import save_json
except ImportError:
    from utils import save_json

# Set default timeout for all socket operations (e.g. RSS feeds, yfinance)
socket.setdefaulttimeout(10)

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constants
BRENT_TICKER = "BZ=F"
RSS_FEEDS = {
    "Reuters Energy": "https://feeds.reuters.com/reuters/energyNews",
    "OilPrice.com": "https://oilprice.com/rss/main",
    "CNBC Energy": "https://www.cnbc.com/id/19836768/device/rss/rss.html",
    "Investing.com": "https://br.investing.com/rss/commodities/brent-oil" # PT-BR source if possible
}

def fetch_brent_price():
    """Fetches the latest Brent Crude Oil price and daily change."""
    try:
        ticker = yf.Ticker(BRENT_TICKER)
        # Fetch 1 year of history with hourly interval for better resolution
        history = ticker.history(period="1y", interval="1h")
        
        if len(history) < 1:
            logger.warning("No price data found for Brent.")
            return None

        # Calculate current metrics
        latest = history.iloc[-1]
        previous = history.iloc[-2] if len(history) > 1 else latest
        
        price = latest['Close']
        prev_price = previous['Close']
        change = price - prev_price
        pct_change = (change / prev_price) * 100

        # Prepare historical data for the chart
        # Reset index to make Date a column and convert to string for JSON serialization
        history_reset = history.reset_index()
        # Ensure column is named Date (yfinance with interval 1h usually names it 'Datetime' or index is datetime)
        # We rename it to Date for consistency with frontend
        if 'Datetime' in history_reset.columns:
            history_reset.rename(columns={'Datetime': 'Date'}, inplace=True)
            
        history_data = history_reset[['Date', 'Close']].to_dict(orient='records')
        
        # Helper string conversion for dates (include time for hourly precision)
        for item in history_data:
            item['Date'] = item['Date'].strftime("%Y-%m-%d %H:%M:%S")

        return {
            "current_price": round(price, 2),
            "change": round(change, 2),
            "pct_change": round(pct_change, 2),
            "history": history_data,
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    except Exception as e:
        logger.error(f"Error fetching Brent price: {e}")
        return None

def fetch_rss_news():
    """Fetches news from defined RSS feeds."""
    news_items = []
    
    for source, url in RSS_FEEDS.items():
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:5]: # Top 5 per source
                news_items.append({
                    "title": entry.title,
                    "link": entry.link,
                    "published": entry.get('published', datetime.now().strftime("%Y-%m-%d")),
                    "source": source,
                    "summary": entry.get('summary', 'No summary available.')
                })
        except Exception as e:
            logger.error(f"Error fetching RSS from {source}: {e}")
            
    # Sort by published date (naive sort, assumption on string format or recent fetch)
    # Ideally should parse date, but for MVP keeping it simple or relying on fetch order
    return news_items

def main():
    logger.info("Starting data fetch...")
    print("1/3: Buscando dados do Brent (5 anos)...")
    
    brent_data = fetch_brent_price()
    
    print("2/3: Buscando notícias RSS...")
    news_data = fetch_rss_news()
    
    data = {
        "brent": brent_data,
        "news": news_data,
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    print("3/3: Salvando dados...")
    save_json(data)
    logger.info("Data fetch completed.")
    print("Concluído!")

if __name__ == "__main__":
    main()
