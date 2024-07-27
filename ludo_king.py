import logging
import psycopg2
from flask import Flask, request
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Dispatcher, CommandHandler, CallbackQueryHandler, MessageHandler, Filters, CallbackContext

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database connection setup
DATABASE_URL = "postgres://default:gaFjrs9b4oLK@ep-ancient-smoke-a1pliqaw.ap-southeast-1.aws.neon.tech:5432/verceldb?sslmode=require"

def get_db_connection():
    return psycopg2.connect(DATABASE_URL, sslmode='require')

# Bot token and webhook URL
TOKEN = '7256179302:AAEKIqy4U--JL6pypx47YsNhuTVRrNO2j4k'
WEBHOOK_URL = 'https://ludo-king.onrender.com/7256179302:AAEKIqy4U--JL6pypx47YsNhuTVRrNO2j4k'
GROUP_CHAT_ID = '1002156476121'

bot = Bot(TOKEN)

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(), bot)
    dispatcher.process_update(update)
    return 'ok'

def start(update, context):
    user_id = update.message.from_user.id
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
    user = cur.fetchone()
    
    if not user:
        cur.execute("INSERT INTO users (user_id) VALUES (%s)", (user_id,))
        conn.commit()
        update.message.reply_text("Welcome! Your account has been created.")
    else:
        update.message.reply_text("Welcome back!")
    
    cur.close()
    conn.close()

def account_balance(update, context):
    user_id = update.message.from_user.id
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT available_balance, deposit_balance, withdrawal_balance FROM users WHERE user_id = %s", (user_id,))
    user = cur.fetchone()
    
    if user:
        available_balance, deposit_balance, withdrawal_balance = user
        update.message.reply_text(
            f"Available Balance: {available_balance}\n"
            f"Deposit Balance: {deposit_balance}\n"
            f"Withdrawal Balance: {withdrawal_balance}"
        )
    else:
        update.message.reply_text("You don't have an account yet. Send /start to create one.")
    
    cur.close()
    conn.close()

def add_balance(update, context):
    update.message.reply_text(
        "Pay minimum ₹10 on UPI [9931071170@fam].",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("PAID", callback_data='paid')]
        ])
    )

def handle_paid(update, context):
    query = update.callback_query
    query.answer()
    query.message.reply_text("Enter 12-digit UTR.")
    context.user_data['waiting_for_utr'] = True

def handle_message(update, context):
    if context.user_data.get('waiting_for_utr'):
        user_id = update.message.from_user.id
        utr = update.message.text
        context.bot.send_message(chat_id=GROUP_CHAT_ID, text=f"user_id: {user_id}, UTR: {utr}")
        update.message.reply_text("Your UTR has been forwarded.")
        context.user_data['waiting_for_utr'] = False

def main():
    global dispatcher
    dispatcher = Dispatcher(bot, None, use_context=True)

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("Account_Balance", account_balance))
    dispatcher.add_handler(CommandHandler("Add_Balance", add_balance))
    dispatcher.add_handler(CallbackQueryHandler(handle_paid, pattern='paid'))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    bot.set_webhook(WEBHOOK_URL)

if __name__ == '__main__':
    main()
    app.run(host='0.0.0.0', port=5000)
