import os
import psycopg2
import logging
from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, CallbackContext
from flask import Flask

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

# Initialize Flask app
app = Flask(__name__)

# Database setup using environment variables
DATABASE_URL = os.getenv('DATABASE_URL')
conn = psycopg2.connect(DATABASE_URL)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS users (chat_id BIGINT PRIMARY KEY)''')
conn.commit()

# Your bot token and group chat ID from environment variables
BOT_TOKEN = os.getenv('BOT_TOKEN')
GROUP_CHAT_ID = os.getenv('GROUP_CHAT_ID')

# Initialize the bot
bot = Bot(token=BOT_TOKEN)

# Function to start the bot
def start(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    c.execute("SELECT * FROM users WHERE chat_id = %s", (chat_id,))
    user = c.fetchone()
    
    if user is None:
        c.execute("INSERT INTO users (chat_id) VALUES (%s)", (chat_id,))
        conn.commit()
        update.message.reply_text("Welcome to Ludo King Tournament")
        bot.send_message(chat_id=GROUP_CHAT_ID, text=f"New user registered with chat_id: {chat_id}")
    else:
        update.message.reply_text("Welcome! Start Playing Matches.")

# Initialize the dispatcher
updater = Updater(token=BOT_TOKEN, use_context=True)
dispatcher = updater.dispatcher

# Add command handler to dispatcher
dispatcher.add_handler(CommandHandler("start", start))

# Start polling
def run_bot():
    updater.start_polling()
    updater.idle()

# Vercel requires an `app` object to be exposed
if __name__ == "__main__":
    run_bot()
