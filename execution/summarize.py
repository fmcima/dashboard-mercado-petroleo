import os
import argparse
import logging
from dotenv import load_dotenv
from google import genai
try:
    from execution.utils import load_json, save_json
except ImportError:
    from utils import load_json, save_json

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configure Gemini Client
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    logger.error("GEMINI_API_KEY not found in environment variables.")

def summarize_text(text):
    """Summarizes text using Google Gemini (via new google-genai SDK)."""
    if not api_key:
        return "⚠️ API Key do Gemini não configurada. Verifique o arquivo .env."

    try:
        client = genai.Client(api_key=api_key)
        prompt = f"Você é um analista experiente do mercado de óleo e gás. Resuma a notícia a seguir em 3 pontos-chave, em português do Brasil. Seja conciso e direto.\n\nNotícia: {text}"
        
        response = client.models.generate_content(
            model='gemini-flash-latest', 
            contents=prompt
        )
        return response.text.strip()
    except Exception as e:
        logger.error(f"Error during summarization with Gemini: {e}")
        return f"Erro ao conectar com a IA do Gemini: {e}"

def main():
    parser = argparse.ArgumentParser(description="Summarize specific news item.")
    parser.add_argument("--index", type=int, help="Index of the news item to summarize")
    parser.add_argument("--test", action="store_true", help="Run a test summarization")
    args = parser.parse_args()

    if args.test:
        print(summarize_text("Saudi Arabia is considering cutting oil production to stabilize prices."))
        return

    # In a real app, logic might differ (e.g., API endpoint calling this function)
    # For this CLI approach:
    # 1. Load data
    # 2. If index provided, summarize that item
    # 3. Save back (caching the summary)
    
    data = load_json()
    if not data or 'news' not in data:
        logger.error("No data found.")
        return

    if args.index is not None and 0 <= args.index < len(data['news']):
        item = data['news'][args.index]
        if 'ai_summary' not in item:
            logger.info(f"Summarizing item {args.index}: {item['title']}")
            summary = summarize_text(item['summary'] + " " + item['title'])
            data['news'][args.index]['ai_summary'] = summary
            save_json(data)
            print(summary)
        else:
            print(data['news'][args.index]['ai_summary'])
    else:
        logger.error("Invalid index.")

if __name__ == "__main__":
    main()
