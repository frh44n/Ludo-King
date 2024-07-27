import psycopg2
import logging
from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, CallbackContext
from flask import Flask, request

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

# Initialize Flask app
app = Flask(__name__)

# Database setup (replace with your PostgreSQL database credentials)
DATABASE_URL = 'postgresql://frh44n:ev0Hhs09Gc7hSGm5y2CfKPXKZrjN1ewf@dpg-cqi4anks1f4s73cgo9r0-a.oregon-postgres.render.com/ludoking'
conn = psycopg2.connect(DATABASE_URL)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS users (chat_id BIGINT PRIMARY KEY)''')
conn.commit()

# Your bot token and group chat ID
BOT_TOKEN = '7256179302:AAEDk58-AphBlxcey5DYgFGMyh2yuNr_17U'
GROUP_CHAT_ID = '1002156476121'

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

# Function to set webhook
@app.route('/set_webhook', methods=['GET', 'POST'])
def set_webhook():
    webhook_url = f"https://ludo-king.onrender.com/{BOT_TOKEN}"
    bot.set_webhook(url=webhook_url)
    return "Webhook set successfully"

# Function to handle webhook
@app.route(f'/{BOT_TOKEN}', methods=['POST'])
def webhook_handler():
    update = Update.de_json(request.get_json(), bot)
    dispatcher.process_update(update)
    return "ok"

# Initialize the dispatcher
updater = Updater(token=BOT_TOKEN, use_context=True)
dispatcher = updater.dispatcher

# Add command handler to dispatcher
dispatcher.add_handler(CommandHandler("start", start))

# Start the Flask app
if __name__ == "__main__":
    app.run(port=5000)
