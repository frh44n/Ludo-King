# new_features.py
from telegram import Update, Bot
from telegram.ext import CommandHandler, MessageHandler, Filters, CallbackContext

ADMIN_USER_ID = 7090230279
TARGET_USER_ID = None  # Placeholder for the user ID to chat with

def start(update: Update, context: CallbackContext):
    if update.effective_user.id == ADMIN_USER_ID:
        update.message.reply_text('Hello Admin! Use /chat <user_id> to start chatting with a user.')
    else:
        update.message.reply_text('You are not authorized to use this bot.')

def chat(update: Update, context: CallbackContext):
    global TARGET_USER_ID
    if update.effective_user.id == ADMIN_USER_ID:
        try:
            TARGET_USER_ID = int(context.args[0])
            update.message.reply_text(f'Started chat with user {TARGET_USER_ID}.')
        except (IndexError, ValueError):
            update.message.reply_text('Usage: /chat <user_id>')
    else:
        update.message.reply_text('You are not authorized to use this command.')

def forward_message(update: Update, context: CallbackContext):
    global TARGET_USER_ID
    if update.effective_user.id == ADMIN_USER_ID:
        if TARGET_USER_ID:
            context.bot.send_message(chat_id=TARGET_USER_ID, text=update.message.text)
        else:
            update.message.reply_text('No user ID specified. Use /chat <user_id> to set a user ID.')
    elif update.effective_user.id == TARGET_USER_ID:
        context.bot.send_message(chat_id=ADMIN_USER_ID, text=update.message.text)
    else:
        update.message.reply_text('You are not authorized to use this bot.')

def register_new_handlers(dispatcher):
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('chat', chat, pass_args=True))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, forward_message))
