# Telegram Bot Generative AI using Google Cloud Functions

This is a simple Telegram bot that runs on Google Cloud Functions. It uses the following libraries:

* Flask
* Requests
* Google API Python Client
* waitress
* google-generativeai
* python-telegram-bot

## Installation

1. Install the required packages: `pip install -r requirements.txt`
2. Deploy the code to Google Cloud Functions.
3. Setup webhook URL from generated cloud function url. 
   - Once deployed, your Cloud Function will have a unique URL. You need to tell Telegram to send updates to this URL.
   - Use the following cURL command, replacing `<YOUR_BOT_TOKEN>` with your bot token and `<YOUR_CLOUD_FUNCTION_URL>` with your function's URL:
     ```bash
     curl -X POST "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook" -H "Content-Type: application/json" -d '{"url": "<YOUR_CLOUD_FUNCTION_URL>"}'
     ```
    - **Example:**
      ```bash
      curl "https://api.telegram.org/bot6212855663:AAGJF62WT0JpJDkV_MoDf4nsFS-H5vXQwR0/setWebhook?url=https://us-central1-awanmasterpiece.cloudfunctions.net/telegram-bot-gcf-prd"
      ```
4. Make sure to setup cloud function to unauthenticated user

## Usage

1. Start a conversation with your bot on Telegram.
2. Send a message to the bot.

## Environment Variables

Set the following environment variables:

* `TELEGRAM_BOT_TOKEN`: Your Telegram bot token.
* `GOOGLE_APPLICATION_CREDENTIALS`: Path to your Google Cloud service account key file.

## Buy me a coffee

[https://buymeacoffee.com/addhewarman](https://buymeacoffee.com/addhewarman)

## License

This project is licensed under the MIT License - see the [LICENSE](https://opensource.org/license/mit) file for details.
