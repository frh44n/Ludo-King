from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram import Update
from telegram.ext import CallbackContext

def main_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("Account Balance", callback_data='Account_Balance')],
        [InlineKeyboardButton("Add Balance", callback_data='Add_Balance')],
        [InlineKeyboardButton("Play", callback_data='Play')],
        [InlineKeyboardButton("Withdraw", callback_data='Withdraw')],
    ]
    return InlineKeyboardMarkup(keyboard)

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

        # Send the inline keyboard with all commands
        update.message.reply_text("Choose an option:", reply_markup=main_menu_keyboard())

        cur.close()
        conn.close()
    except Exception as e:
        logger.error(f"Error in start command: {e}")
        update.message.reply_text("An error occurred while processing your request.")
