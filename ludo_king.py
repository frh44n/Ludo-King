import os
import psycopg2
import logging
from telegram import Update, Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Dispatcher, CommandHandler, CallbackContext, MessageHandler, Filters, CallbackQueryHandler
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

# Command to play match
def play_match(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    keyboard = [
        [InlineKeyboardButton("₹10 Entry, Win- ₹20", callback_data='play_10')],
        [InlineKeyboardButton("₹20 Entry, Win- ₹40", callback_data='play_20')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Choose your entry amount:", reply_markup=reply_markup)

# Handler for inline keyboard button press
def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()

    chat_id = query.message.chat.id
    c.execute("SELECT deposit_funds, withdrawal_funds FROM users WHERE chat_id = %s", (chat_id,))
    user = c.fetchone()

    if query.data == 'amount_paid':
        query.edit_message_text(text="Enter 12 digit UTR.")
        context.user_data['awaiting_utr'] = True
    elif query.data == 'play_10':
        if user and user[0] + user[1] >= 10:
            query.edit_message_text(text="You have joined the match with ₹10 entry fee.")
            c.execute("UPDATE users SET deposit_funds = deposit_funds - 10 WHERE chat_id = %s", (chat_id,))
            c.execute("UPDATE users SET match_played = match_played + 1 WHERE chat_id = %s", (chat_id,))
            conn.commit()
        else:
            query.edit_message_text(text="Insufficient Funds.")
    elif query.data == 'play_20':
        if user and user[0] + user[1] >= 20:
            query.edit_message_text(text="You have joined the match with ₹20 entry fee.")
            c.execute("UPDATE users SET deposit_funds = deposit_funds - 20 WHERE chat_id = %s", (chat_id,))
            c.execute("UPDATE users SET match_played = match_played + 1 WHERE chat_id = %s", (chat_id,))
            conn.commit()
        else:
            query.edit_message_text(text="Insufficient Funds.")

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
dispatcher = Dispatcher(bot, None, workers=0, use_context=True)

# Add command handlers to dispatcher
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("fundsinfo", funds_info))
dispatcher.add_handler(CommandHandler("matchinfo", match_info))
dispatcher.add_handler(CommandHandler("addfund", add_fund))
dispatcher.add_handler(CommandHandler("playmatch", play_match))
dispatcher.add_handler(CallbackQueryHandler(button))
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

# Vercel requires an `app` object to be exposed
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
