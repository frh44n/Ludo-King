import logging
from telegram.ext import Updater, CommandHandler, MessageHandler
import psycopg2
from flask import Flask, request

# Enable logging
logging.basicConfig(level=logging.INFO)

# Telegram Bot Token
TOKEN = '7299082317:AAFIOD97Ny8ng-sXgOh7BBxcgKB6tSK4ZPM'

# Supabase credentials
SUPABASE_URL = 'postgresql://postgres.hlakdepwuqvdrzeodqsn:[farhan@786786123]@aws-0-ap-south-1.pooler.supabase.com:6543/postgres'
SUPABASE_DB = 'postgres'
SUPABASE_USER = 'postgres.hlakdepwuqvdrzeodqsn'
SUPABASE_PASSWORD = 'farhan@786786123'

# Connect to Supabase
conn = psycopg2.connect(
    host=SUPABASE_URL,
    database=SUPABASE_DB,
    user=SUPABASE_USER,
    password=SUPABASE_PASSWORD
)
cursor = conn.cursor()

# Create a table to store user data if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        telegram_id INTEGER,
        username TEXT
    )
''')
conn.commit()

# Define a function to check if a user exists in the database
def user_exists(telegram_id):
    cursor.execute('''
        SELECT 1 FROM users
        WHERE telegram_id = %s
    ''', (telegram_id,))
    return cursor.fetchone() is not None

# Define a function to handle the /start command
def start(update, context):
    telegram_id = update.effective_user.id
    if user_exists(telegram_id):
        context.bot.send_message(chat_id=update.effective_chat.id, text='Hello, sir!')
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text='Please Sign Up')

# Create a Flask app to handle Webhook requests
app = Flask(__name__)

@app.route('/' + TOKEN, methods=['POST'])
def webhook():
    update = Updater(TOKEN, use_context=True).update_ejson(request.get_json())
    dp = updater.dispatcher
    dp.process_update(update)
    return 'ok'

# Set up the Webhook
updater = Updater(TOKEN, use_context=True)
updater.start_webhook(listen='0.0.0.0', port=8443, url_path=TOKEN)
updater.bot.set_webhook('https://supabas.onrender.com/' + TOKEN)

# Add a handler for the /start command
dp = updater.dispatcher
dp.add_handler(CommandHandler('start', start))

# Run the Flask app
if __name__ == '__main__':
    app.run()
