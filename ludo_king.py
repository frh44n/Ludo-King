import logging
import psycopg2
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters, CallbackContext

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database connection setup
DATABASE_URL = "postgres://default:gaFjrs9b4oLK@ep-ancient-smoke-a1pliqaw.ap-southeast-1.aws.neon.tech:5432/verceldb?sslmode=require"

def get_db_connection():
    return psycopg2.connect(DATABASE_URL, sslmode='require')

# Bot token
TOKEN = '7256179302:AAEKIqy4U--JL6pypx47YsNhuTVRrNO2j4k'

def start(update: Update, context: CallbackContext):
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

def account_balance(update: Update, context: CallbackContext):
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

def add_balance(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Pay minimum ₹10 on UPI [9931071170@fam].",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("PAID", callback_data='paid')]
        ])
    )

def handle_paid(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    query.message.reply_text("Enter 12-digit UTR.")
    context.user_data['waiting_for_utr'] = True

def handle_message(update: Update, context: CallbackContext):
    if context.user_data.get('waiting_for_utr'):
        user_id = update.message.from_user.id
        utr = update.message.text
        context.bot.send_message(chat_id='1002156476121', text=f"user_id: {user_id}, UTR: {utr}")
        update.message.reply_text("Your UTR has been forwarded.")
        context.user_data['waiting_for_utr'] = False

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("Account_Balance", account_balance))
    dp.add_handler(CommandHandler("Add_Balance", add_balance))
    dp.add_handler(CallbackQueryHandler(handle_paid, pattern='paid'))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
