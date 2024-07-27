import os
import psycopg2
import logging
from telegram import Update, Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters, CallbackQueryHandler
from flask import Flask, request
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

# Initialize Flask app
app = Flask(__name__)

# Database setup using environment variables
DATABASE_URL = os.getenv('DATABASE_URL')
conn = psycopg2.connect(DATABASE_URL)
c = conn.cursor()
c.execute('''
CREATE TABLE IF NOT EXISTS users (
    chat_id BIGINT PRIMARY KEY,
    deposit_funds NUMERIC DEFAULT 0,
    withdrawal_funds NUMERIC DEFAULT 0,
    match_played INT DEFAULT 0,
    total_win INT DEFAULT 0,
    total_loss INT DEFAULT 0,
    total_withdrawn NUMERIC DEFAULT 0
)
''')
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

# Command to view funds info
def funds_info(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    c.execute("SELECT deposit_funds, withdrawal_funds, total_withdrawn FROM users WHERE chat_id = %s", (chat_id,))
    user = c.fetchone()
    if user:
        update.message.reply_text(
            f"Deposit Funds: ₹{user[0]}\n"
            f"Withdrawal Funds: ₹{user[1]}\n"
            f"Total Withdrawn: ₹{user[2]}"
        )
    else:
        update.message.reply_text("You are not registered. Use /start to register.")

# Command to view match info
def match_info(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    c.execute("SELECT match_played, total_win, total_loss FROM users WHERE chat_id = %s", (chat_id,))
    user = c.fetchone()
    if user:
        update.message.reply_text(
            f"Match Played: {user[0]}\n"
            f"Total Wins: {user[1]}\n"
            f"Total Losses: {user[2]}"
        )
    else:
        update.message.reply_text("You are not registered. Use /start to register.")

# Command to add funds
def add_fund(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    keyboard = [
        [InlineKeyboardButton("Amount Paid", callback_data='amount_paid')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(
        "Send money on this UPI id 9931071170@fam",
        reply_markup=reply_markup
    )

# Handler for inline keyboard button press
def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    if query.data == 'amount_paid':
        query.edit_message_text(text="Enter 12 digit UTR.")
        context.user_data['awaiting_utr'] = True

# Handler for user messages
def handle_message(update: Update, context: CallbackContext) -> None:
    if context.user_data.get('awaiting_utr'):
        utr = update.message.text
        # Here, you can add logic to verify the UTR and update the database
        update.message.reply_text("After verification, funds will be added to your ID.")
        context.user_data['awaiting_utr'] = False
    else:
        update.message.reply_text("Unrecognized command or message.")

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
updater = Updater(bot=bot, use_context=True)
dispatcher = updater.dispatcher

# Add command handlers to dispatcher
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("Funds Info", funds_info))
dispatcher.add_handler(CommandHandler("Match Info", match_info))
dispatcher.add_handler(CommandHandler("Add Fund", add_fund))
dispatcher.add_handler(CallbackQueryHandler(button))
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

# Vercel requires an `app` object to be exposed
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
