import os
import telegram
from flask import Flask, request
import google.generativeai as genai
import asyncio

BOT_TOKEN = os.environ.get('BOT_TOKEN')
GOOGLE_GEMINI_API_KEY = os.environ.get('GOOGLE_GEMINI_API_KEY')
GEMINI_MODEL_ID = "gemini-1.5-pro"

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

@app.route(f'/{BOT_TOKEN}', methods=['POST'])
def webhook(request):
    """Handles incoming Telegram updates via webhook."""
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    if update.message:
        asyncio.run(handle_message(update.message))
    return 'ok'

async def handle_message(message):
    chat_id = message.chat.id
    text = message.text

    # Get or create chat session
    chat_session = chat_sessions.setdefault(chat_id, genai.GenerativeModel(
        model_name="gemini-1.5-pro",
        generation_config=generation_config,
    ).start_chat())

    # Send message to Gemini and get response
    response = chat_session.send_message(text)

    async with bot:
        await bot.sendMessage(chat_id=chat_id, text=response.text)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
