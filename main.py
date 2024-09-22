import os
import asyncio
import json
from urllib.parse import urlencode
from datetime import datetime

import google.generativeai as genai
import requests
import telegram
from flask import Flask, request

BOT_TOKEN = os.environ.get('BOT_TOKEN')
GOOGLE_GEMINI_API_KEY = os.environ.get('GOOGLE_GEMINI_API_KEY')
GEMINI_MODEL_ID = "gemini-1.5-pro"
SEARCH_ENGINE_URL = os.getenv(
    "SEARCH_ENGINE_URL", "https://search.hbubli.cc/search"
)

bot = telegram.Bot(token=BOT_TOKEN)
app = Flask(__name__)

# Store chat sessions
chat_sessions = {}

genai.configure(api_key=GOOGLE_GEMINI_API_KEY)

generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}


def search_web(query, categories=None, engines=None, language=None, pageno=1):
    """Searches the web using the provided search engine URL.

    Args:
        query (str): The search query.
        categories (list, optional): A list of categories to filter results.
            Defaults to None.
        engines (list, optional): A list of search engines to use. Defaults to
            None.
        language (str, optional): The language to use for the search. Defaults
            to None.
        pageno (int, optional): The page number of results to retrieve. Defaults
            to 1.

    Returns:
        list: A list of dictionaries containing search result information, or
            an error message.
    """

    params = {
        'q': query,
        'format': 'json',
        'categories': ','.join(categories) if categories else None,
        'engines': ','.join(engines) if engines else None,
        'language': language,
        'pageno': pageno
    }

    url = f"{SEARCH_ENGINE_URL}?{urlencode({k: v for k, v in params.items() if v is not None})}"
    response = requests.get(url)

    if response.status_code == 200:
        try:
            data = response.json()
            return data.get('results', [])
        except (ValueError, KeyError) as e:
            return f"Error parsing search results: {e}"
    else:
        return f"Error accessing search engine. Status code: {response.status_code}"


@app.route(f'/{BOT_TOKEN}', methods=['POST'])
def webhook(request):
    """Handles incoming Telegram updates via webhook."""
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    if update.message:
        asyncio.run(handle_message(update.message))
    return 'ok'


async def handle_message(message):
    """Handles incoming messages, interacts with Gemini, and fetches search
    results.

    Args:
        message: The incoming message object.
    """

    chat_id = message.chat.id
    text = message.text

    # Get or create chat session
    chat_session = chat_sessions.setdefault(
        chat_id,
        genai.GenerativeModel(
            model_name="gemini-1.5-pro",
            generation_config=generation_config,
        ).start_chat(),
    )

    # Add current date and time to the message
    text = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {text}"

    # Fetch and process search results
    try:
        search_results = search_web(text)
        search_summary = _format_search_results(search_results)
        response = chat_session.send_message(
            f"{text}\n---search result---\n{search_summary}"
        )
        response_text = response.text
    except Exception as e:
        response_text = f"Error: {e}"

    # Send the final response
    async with bot:
        await bot.sendMessage(chat_id=chat_id, text=response_text)


def _format_search_results(search_results):
    """Formats the search results into a string for Gemini."""
    if isinstance(search_results, list):  # Check if it's a list
        return "\n".join([
            f"**{result.get('title', '')}**\n{result.get('content', '')}\n"
            for result in search_results
        ])
    else:
        return f"Search Error: {search_results}"  # Return error message 

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
