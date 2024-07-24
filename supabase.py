import os
import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import psycopg2
from flask import Flask, request

# Load environment variables from .env file
TOKEN = os.getenv('TOKEN')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = int(os.getenv('DB_PORT'))
DB_USERNAME = os.getenv('DB_USERNAME')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_DATABASE = os.getenv('DB_DATABASE')
WEBHOOK_URL = os.getenv('WEBHOOK_URL')

# Enable logging
logging.basicConfig(level=logging.INFO)

# Establish a connection to TiDB Cloud
conn = psycopg2.connect(
    host=DB_HOST,
    port=DB_PORT,
    database=DB_DATABASE,
    user=DB_USERNAME,
    password=DB_PASSWORD,
    sslmode="disable"
)

# Create a cursor object to execute queries
cur = conn.cursor()

app = Flask(__name__)

@app.route('/' + TOKEN, methods=['POST'])
def webhook():
    update = Updater(TOKEN, use_context=True).update_ejson(request.get_json())
    dp = update.dispatcher
    dp.process_update(update)
    return 'ok'

def start(update, context):
    cur.execute("SELECT * FROM users WHERE telegram_id = %s", (update.effective_user.id,))
    if cur.fetchone() is None:
        cur.execute("INSERT INTO users (telegram_id, username) VALUES (%s, %s)",
                    (update.effective_user.id, update.effective_user.username))
        conn.commit()
    update.message.reply_text("Hello! I'm your Telegram bot.")

def echo(update, context):
    cur.execute("SELECT * FROM users WHERE telegram_id = %s", (update.effective_user.id,))
    user = cur.fetchone()
    if user:
        update.message.reply_text(f"Hello, {user[1]}!")

def main():
    dp = Updater(TOKEN, use_context=True).dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text, echo))

    app.run(webhook_url=WEBHOOK_URL)

if __name__ == '__main__':
    main()
