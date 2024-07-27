import logging
import psycopg2
from flask import Flask, request
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Dispatcher, CommandHandler, CallbackQueryHandler, MessageHandler, Filters, CallbackContext
import test
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
                withdrawal_balance NUMERIC DEFAULT 0
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
            cur.execute("INSERT INTO users (user_id) VALUES (%s)", (user_id,))
            conn.commit()
            update.message.reply_text("Welcome! Your account has been created.")
        else:
            update.message.reply_text("Welcome back!")
        
        cur.close()
        conn.close()
    except Exception as e:
        logger.error(f"Error in start command: {e}")
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
                f"Available Balance: {available_balance}"
                
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

def handle_paid(update: Update, context: CallbackContext):
    try:
        query = update.callback_query
        query.answer()
        query.message.reply_text("Enter 12-digit UTR.")
        context.user_data['waiting_for_utr'] = True
    except Exception as e:
        logger.error(f"Error in handle_paid callback: {e}")
        query.message.reply_text("An error occurred while processing your request.")

def handle_message(update: Update, context: CallbackContext):
    try:
        user_id = update.message.from_user.id

        if context.user_data.get('waiting_for_utr'):
            utr = update.message.text
            context.bot.send_message(chat_id=GROUP_CHAT_ID, text=f"user_id: {user_id}, UTR: {utr}")
            update.message.reply_text("After verification money will be added in your Accoun. Please check after few minutes. Press /Account_Balance to check balance.")
            context.user_data['waiting_for_utr'] = False

        elif context.user_data.get('waiting_for_ludo_id'):
            ludo_id = update.message.text
            entry_amount = context.user_data.get('entry_amount')

            # Forward the message to the GROUP_CHAT_ID
            context.bot.send_message(
                chat_id=GROUP_CHAT_ID,
                text=f"Match Start 👑\nchat_id: {user_id}\nEntry amount: ₹{entry_amount}\nLudo_id: {ludo_id}"
            )

            # Deduct the entry amount from the user's balance
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("UPDATE users SET available_balance = available_balance - %s WHERE user_id = %s", (entry_amount, user_id))
            conn.commit()
            cur.close()
            conn.close()

            # Notify the user
            update.message.reply_text(f"Room Code will be available to you when all members will join!\n₹{entry_amount} has been deducted from your balance.")
            context.user_data['waiting_for_ludo_id'] = False

        else:
            # Handle other messages if necessary
            pass

    except Exception as e:
        logger.error(f"Error in handle_message: {e}")
        update.message.reply_text("An error occurred while processing your request.")

def play(update: Update, context: CallbackContext):
    try:
        keyboard = [
            [InlineKeyboardButton("₹10 Entry, Winner- ₹20", callback_data='entry_10')],
            [InlineKeyboardButton("₹20 Entry, Winner- ₹40", callback_data='entry_20')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text("Choose your entry:", reply_markup=reply_markup)
    except Exception as e:
        logger.error(f"Error in play command: {e}")
        update.message.reply_text("An error occurred while processing your request.")

def handle_entry_selection(update: Update, context: CallbackContext):
    try:
        query = update.callback_query
        query.answer()
        user_id = query.from_user.id
        data = query.data

        entry_amount = 10 if data == 'entry_10' else 20 if data == 'entry_20' else None
        
        if entry_amount is None:
            query.edit_message_text(text="Invalid selection.")
            return
        
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT available_balance FROM users WHERE user_id = %s", (user_id,))
        result = cur.fetchone()

        if result:
            available_balance = result[0]

            if available_balance < entry_amount:
                query.edit_message_text(text="Insufficient Balance. Please /Add_Balance.")
            else:
                keyboard = [
                    [InlineKeyboardButton("Confirm Entry", callback_data=f'confirm_entry_{entry_amount}')],
                    [InlineKeyboardButton("Cancel ❌", callback_data='cancel')]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                query.edit_message_text(text=f"You have selected an entry fee of ₹{entry_amount}. Confirm your choice:", reply_markup=reply_markup)

        cur.close()
        conn.close()
    except Exception as e:
        logger.error(f"Error in handle_entry_selection: {e}")
        query.edit_message_text(text="An error occurred while processing your request.")

def confirm_action(update: Update, context: CallbackContext):
    try:
        query = update.callback_query
        query.answer()
        user_id = query.from_user.id
        data = query.data

        if data.startswith('confirm_entry_'):
            entry_amount = int(data.split('_')[-1])
            context.user_data['entry_amount'] = entry_amount
            query.edit_message_text("Enter your Ludo ID:")
            context.user_data['waiting_for_ludo_id'] = True
        elif data == 'cancel':
            query.edit_message_text("Action cancelled.")
    except Exception as e:
        logger.error(f"Error in confirm_action: {e}")
        query.edit_message_text("An error occurred while processing your request.")

def main():
    create_table()
    
    global dispatcher
    dispatcher = Dispatcher(bot, None, use_context=True)

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("Account_Balance", account_balance))
    dispatcher.add_handler(CommandHandler("Add_Balance", add_balance))
    dispatcher.add_handler(CommandHandler("Play", play))
    dispatcher.add_handler(CallbackQueryHandler(handle_paid, pattern='paid'))
    dispatcher.add_handler(CallbackQueryHandler(handle_entry_selection, pattern='entry_'))
    dispatcher.add_handler(CallbackQueryHandler(confirm_action, pattern='confirm_entry_|cancel'))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    bot.set_webhook(WEBHOOK_URL)
    logger.info(f"Webhook set to {WEBHOOK_URL}")

if __name__ == '__main__':
    main()
    app.run(host='0.0.0.0', port=5000)
