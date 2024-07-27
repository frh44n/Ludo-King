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

def create_table():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id BIGINT PRIMARY KEY,
                available_balance NUMERIC DEFAULT 0,
                deposit_balance NUMERIC DEFAULT 0,
                withdrawal_balance NUMERIC DEFAULT 0,
                ludo_id VARCHAR
            )
        """)
        conn.commit()
        cur.close()
        conn.close()
        logger.info("Table created successfully.")
    except Exception as e:
        logger.error(f"Error creating table: {e}")

# Bot token and webhook URL
TOKEN = '7256179302:AAEKIqy4U--JL6pypx47YsNhuTVRrNO2j4k'
WEBHOOK_URL = 'https://ludo-king.onrender.com/7256179302:AAEKIqy4U--JL6pypx47YsNhuTVRrNO2j4k'
GROUP_CHAT_ID = '7090230279'

bot = Bot(TOKEN)

app = Flask(__name__)

@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    try:
        update_json = request.get_json(force=True)
        logger.info(f"Webhook received: {update_json}")
        update = Update.de_json(update_json, bot)
        dispatcher.process_update(update)
        return 'ok'
    except Exception as e:
        logger.error(f"Error in webhook: {e}")
        return 'error'

def start(update: Update, context: CallbackContext):
    try:
        user_id = update.message.from_user.id
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
        user = cur.fetchone()
        
        if not user:
            update.message.reply_text("Welcome! Enter your Ludo ID.")
            context.user_data['waiting_for_ludo_id'] = True
        else:
            update.message.reply_text("Welcome back!")
        
        cur.close()
        conn.close()
    except Exception as e:
        logger.error(f"Error in start command: {e}")
        update.message.reply_text("An error occurred while processing your request.")

def handle_message(update: Update, context: CallbackContext):
    try:
        user_id = update.message.from_user.id
        
        if context.user_data.get('waiting_for_ludo_id'):
            ludo_id = update.message.text
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("INSERT INTO users (user_id, ludo_id) VALUES (%s, %s) ON CONFLICT (user_id) DO UPDATE SET ludo_id = EXCLUDED.ludo_id", (user_id, ludo_id))
            conn.commit()
            cur.close()
            conn.close()
            update.message.reply_text("Ludo ID saved. Your account has been created.")
            context.user_data['waiting_for_ludo_id'] = False
            return
        
        if context.user_data.get('waiting_for_utr'):
            utr = update.message.text
            context.bot.send_message(chat_id=GROUP_CHAT_ID, text=f"user_id: {user_id}, UTR: {utr}")
            update.message.reply_text("Your UTR has been forwarded.")
            context.user_data['waiting_for_utr'] = False
            
    except Exception as e:
        logger.error(f"Error in handle_message: {e}")
        update.message.reply_text("An error occurred while processing your request.")

def account_balance(update: Update, context: CallbackContext):
    try:
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
    except Exception as e:
        logger.error(f"Error in account_balance command: {e}")
        update.message.reply_text("An error occurred while processing your request.")

def add_balance(update: Update, context: CallbackContext):
    try:
        update.message.reply_text(
            "Pay minimum ₹10 on UPI [9931071170@fam].",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("PAID", callback_data='paid')]
            ])
        )
    except Exception as e:
        logger.error(f"Error in add_balance command: {e}")
        update.message.reply_text("An error occurred while processing your request.")

def play(update: Update, context: CallbackContext):
    try:
        user_id = update.message.from_user.id
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT available_balance FROM users WHERE user_id = %s", (user_id,))
        user = cur.fetchone()

        if user:
            available_balance = user[0]
            keyboard = [
                [InlineKeyboardButton("₹10 Entry, Winner- ₹20", callback_data='entry_10')],
                [InlineKeyboardButton("₹20 Entry, Winner- ₹40", callback_data='entry_20')]
            ]
            update.message.reply_text("Choose an entry option:", reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            update.message.reply_text("You don't have an account yet. Send /start to create one.")
        
        cur.close()
        conn.close()
    except Exception as e:
        logger.error(f"Error in play command: {e}")
        update.message.reply_text("An error occurred while processing your request.")

def handle_paid(update: Update, context: CallbackContext):
    try:
        query = update.callback_query
        query.answer()
        query.message.reply_text("Enter 12-digit UTR.")
        context.user_data['waiting_for_utr'] = True
    except Exception as e:
        logger.error(f"Error in handle_paid callback: {e}")
        query.message.reply_text("An error occurred while processing your request.")

def handle_entry_selection(update: Update, context: CallbackContext):
    try:
        query = update.callback_query
        data = query.data
        user_id = query.from_user.id
        entry_amount = 0
        
        if data == 'entry_10':
            entry_amount = 10
        elif data == 'entry_20':
            entry_amount = 20
        
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT available_balance, ludo_id FROM users WHERE user_id = %s", (user_id,))
        result = cur.fetchone()
        
        if result:
            available_balance, ludo_id = result
            
            if available_balance >= entry_amount:
                # Deduct the balance
                new_balance = available_balance - entry_amount
                cur.execute("UPDATE users SET available_balance = %s WHERE user_id = %s", (new_balance, user_id))
                conn.commit()
                
                # Forward the message to the group
                context.bot.send_message(
                    chat_id=GROUP_CHAT_ID,
                    text=f"Match started by:\nChatid: {user_id}\nEntry: ₹{entry_amount}\nLudo_Id: {ludo_id}"
                )
                
                query.edit_message_text("Match has started! Good luck!")
            else:
                query.edit_message_text("Insufficient balance. Please /Add_Balance.")
        
        cur.close()
        conn.close()
    except Exception as e:
        logger.error(f"Error in handle_entry_selection callback: {e}")
        query.edit_message_text("An error occurred while processing your request.")

def confirm_action(update: Update, context: CallbackContext):
    try:
        query = update.callback_query
        data = query.data
        
        if data == 'play':
            query.edit_message_text("Match started!")
        elif data == 'cancel':
            query.edit_message_text("Action canceled.")
    except Exception as e:
        logger.error(f"Error in confirm_action callback: {e}")
        query.edit_message_text("An error occurred while processing your request.")

def main():
    create_table()
    
    global dispatcher
    dispatcher = Dispatcher(bot, None, use_context=True)

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('account_balance', account_balance))
    dispatcher.add_handler(CommandHandler('add_balance', add_balance))
    dispatcher.add_handler(CommandHandler('play', play))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    dispatcher.add_handler(CallbackQueryHandler(handle_paid, pattern='paid'))
    dispatcher.add_handler(CallbackQueryHandler(handle_entry_selection, pattern='entry_'))
    dispatcher.add_handler(CallbackQueryHandler(confirm_action))

    bot.set_webhook(WEBHOOK_URL)
    logger.info(f"Webhook set to {WEBHOOK_URL}")


if __name__ == '__main__':
    main()
    app.run(host='0.0.0.0', port=5000)
