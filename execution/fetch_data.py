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
    """Fetches the latest Brent Crude Oil price and historical data.
    Fetches both:
    - Hourly data (1 year) for short-term views (1D, 5D, 1M, 6M, YTD, 1Y)
    - Daily data (5 years) for long-term view (5Y)
    """
    try:
        ticker = yf.Ticker(BRENT_TICKER)
        
        # Fetch hourly data for short-term (max ~730 days, we use 1 year)
        logger.info("Fetching 1 year of hourly data...")
        history_hourly = ticker.history(period="1y", interval="1h")
        
        # Fetch daily data for long-term (5 years)
        logger.info("Fetching 5 years of daily data...")
        history_daily = ticker.history(period="5y", interval="1d")
        
        if len(history_hourly) < 1 and len(history_daily) < 1:
            logger.warning("No price data found for Brent.")
            return None

        # Use hourly data for current price metrics (more recent)
        if len(history_hourly) >= 2:
            latest = history_hourly.iloc[-1]
            previous = history_hourly.iloc[-2]
        else:
            latest = history_daily.iloc[-1]
            previous = history_daily.iloc[-2] if len(history_daily) > 1 else latest
        
        price = latest['Close']
        prev_price = previous['Close']
        change = price - prev_price
        pct_change = (change / prev_price) * 100

        # Process hourly history
        hourly_data = []
        if len(history_hourly) > 0:
            history_reset = history_hourly.reset_index()
            if 'Datetime' in history_reset.columns:
                history_reset.rename(columns={'Datetime': 'Date'}, inplace=True)
            hourly_data = history_reset[['Date', 'Close']].to_dict(orient='records')
            for item in hourly_data:
                item['Date'] = item['Date'].strftime("%Y-%m-%d %H:%M:%S")
        
        # Process daily history
        daily_data = []
        if len(history_daily) > 0:
            history_reset = history_daily.reset_index()
            if 'Datetime' in history_reset.columns:
                history_reset.rename(columns={'Datetime': 'Date'}, inplace=True)
            daily_data = history_reset[['Date', 'Close']].to_dict(orient='records')
            for item in daily_data:
                item['Date'] = item['Date'].strftime("%Y-%m-%d %H:%M:%S")

        return {
            "current_price": round(price, 2),
            "change": round(change, 2),
            "pct_change": round(pct_change, 2),
            "history": hourly_data,  # Default for backward compatibility
            "history_hourly": hourly_data,  # Hourly for short-term views
            "history_daily": daily_data,  # Daily for 5Y view
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
