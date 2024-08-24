import os
import logging
from dotenv import load_dotenv
from scrapegraphai.graphs import SmartScraperGraph
import openai
from flask import Flask, request, jsonify
from functools import wraps
from flask_cors import CORS

# Configure logging
logging.basicConfig(level=logging.DEBUG,  # Changed to DEBUG for more detailed logs
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler("app.log"),
                        logging.StreamHandler()
                    ])
logger = logging.getLogger(__name__)

load_dotenv()

openai.api_key = os.getenv('OPENAI_API_KEY')
API_KEY = os.getenv('PYTHON_SERVER_API_KEY')

if not API_KEY:
    logger.error('PYTHON_SERVER_API_KEY is not set in the environment variables')
    raise ValueError('PYTHON_SERVER_API_KEY is not set in the environment variables')

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

graph_config = {
    "llm": {
        "api_key": os.getenv("OPENAI_API_KEY"),
        "model": "gpt-4o-mini",  
    },
    "verbose": True,
    "headless": True,
}

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        provided_api_key = request.headers.get('X-API-Key')
        if not provided_api_key or provided_api_key != API_KEY:
            logger.warning(f"Invalid API key attempt: {provided_api_key}")
            return jsonify({'error': 'Invalid or missing API key'}), 401
        logger.info("API key validation successful")
        return f(*args, **kwargs)
    return decorated_function

def scrape_website(url):
    logger.info(f"Scraping website: {url}")
    smart_scraper_graph = SmartScraperGraph(
        prompt="You are an expert at summarizing and identifying key points in text. Locate the top 3 articles of the day on the website and summarize each of them. Make sure to capture only the key points and using only 3 sentences. Also, include the Full URL of each article (include prefix). The 'source' should be verbatim from the URL provided in the request which is the website that I'm giving you to scrape (!!!MUST BE THE URL with NO '/' at the end). The format of your summary response should look like this every time: {'top_articles': [{'title': '', 'summary': '', 'url': '', 'source': ''}, {'title': '', 'summary': '', 'url': '', 'source': ''}, {'title': '', 'summary': '', 'url': '', 'source': ''}]}",
        source=url, 
        config=graph_config,
    )
    result = smart_scraper_graph.run()
    logger.info(f"Scraping completed for {url}")
    return result

@app.route('/scrape-and-summarize', methods=['POST'])
@require_api_key
def scrape_and_summarize():
    logger.info("Received request to /scrape-and-summarize")
    logger.info(f"Request headers: {request.headers}")
    logger.info(f"Request body: {request.get_data(as_text=True)}")
    data = request.json
    urls = data.get('urls')
    if not urls:
        logger.warning("Request received without URLs")
        return jsonify({'error': 'URLs are required'}), 400

    try:
        summaries = []
        for url in urls:
            logger.info(f"Processing URL: {url}")
            summary = scrape_website(url)
            summaries.extend(summary.get('top_articles', []))
        logger.info("Request processed successfully")
        return jsonify(summaries)
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    logger.info("Starting Flask server")
    app.run(host='0.0.0.0', port=8000, debug=True)