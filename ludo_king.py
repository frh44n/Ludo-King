from flask import Flask, request
from telegram import Update
from telegram.ext import CommandHandler, Dispatcher
from telegram.ext import CallbackContext
import psycopg2
import os
import logging

# Initialize Flask app
app = Flask(__name__)

# Initialize Telegram bot
from telegram import Bot
TOKEN = os.getenv('BOT_TOKEN')
bot = Bot(token=TOKEN)

# Replace with your PostgreSQL connection details
DATABASE_URL = os.getenv('DATABASE_URL')
ADMIN_ID = 6826870863  # Replace with the admin's Telegram user ID

def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL)
    return conn

def total_user(update: Update, context: CallbackContext):
    if update.effective_user.id != ADMIN_ID:
        context.bot.send_message(chat_id=update.effective_chat.id, text="You are not authorized to use this command.")
        return

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT chat_id FROM users")  # Replace 'users' with your table name
        chat_ids = cursor.fetchall()
        if chat_ids:
            chat_ids_text = "\n".join(str(chat_id[0]) for chat_id in chat_ids)
            context.bot.send_message(chat_id=update.effective_chat.id, text=f"User Chat IDs:\n{chat_ids_text}")
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text="No users found.")
    except Exception as e:
        context.bot.send_message(chat_id=update.effective_chat.id, text=f"An error occurred: {e}")
    finally:
        cursor.close()
        conn.close()

@app.route('/webhook', methods=['POST'])
def webhook():
    update = request.get_json()
    if 'message' in update:
        dispatcher.process_update(Update.de_json(update, bot))
    return 'ok'

def set_webhook():
    webhook_url = os.getenv('WEBHOOK_URL')  # This should be your public URL
    bot.set_webhook(url=webhook_url + '/webhook')

def main():
    global dispatcher
    dispatcher = Dispatcher(bot, None, workers=0)
    dispatcher.add_handler(CommandHandler('Total_user', total_user))

    # Set webhook URL
    set_webhook()

    # Run the Flask app
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))

if __name__ == '__main__':
    main()
