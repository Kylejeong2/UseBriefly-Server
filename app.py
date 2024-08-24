import os
from dotenv import load_dotenv
from scrapegraphai.graphs import SmartScraperGraph
import openai
from flask import Flask, request, jsonify
from functools import wraps
from flask_cors import CORS

load_dotenv()

openai.api_key = os.getenv('OPENAI_API_KEY')
API_KEY = os.getenv('PYTHON_SERVER_API_KEY')

if not API_KEY:
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
            return jsonify({'error': 'Invalid or missing API key'}), 401
        return f(*args, **kwargs)
    return decorated_function

def scrape_website(url):
    smart_scraper_graph = SmartScraperGraph(
        prompt="You are an expert at summarizing and identifying key points in text. Locate the top 3 articles of the day on the website and summarize each of them. Make sure to capture only the key points and using only 3 sentences. Also, include the Full URL of each article (include prefix). The 'source' should be verbatim from the URL provided in the request which is the website that I'm giving you to scrape (!!!MUST BE THE URL with NO '/' at the end). The format of your summary response should look like this every time: {'top_articles': [{'title': '', 'summary': '', 'url': '', 'source': ''}, {'title': '', 'summary': '', 'url': '', 'source': ''}, {'title': '', 'summary': '', 'url': '', 'source': ''}]}",
        source=url, 
        config=graph_config,
    )
    result = smart_scraper_graph.run()
    return result

@app.route('/scrape-and-summarize', methods=['POST'])
@require_api_key
def scrape_and_summarize():
    data = request.json
    urls = data.get('urls')
    if not urls:
        return jsonify({'error': 'URLs are required'}), 400

    try:
        summaries = []
        for url in urls:
            summary = scrape_website(url)
            summaries.extend(summary.get('top_articles', []))
        return jsonify(summaries)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv("PORT"))
    app.run(host='0.0.0.0', port=port)