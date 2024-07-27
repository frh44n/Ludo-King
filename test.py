# test.py
from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, Filters, CallbackContext

ADMIN_USER_ID = 7090230279
TARGET_USER_ID = None

def start_admin_chat(update: Update, context: CallbackContext):
    if update.effective_user.id == ADMIN_USER_ID:
        update.message.reply_text('Hello Admin! Use /chat <user_id> to start chatting with a user.')
    else:
        update.message.reply_text('You are not authorized to use this bot.')

def chat(update: Update, context: CallbackContext):
    global TARGET_USER_ID
    if update.effective_user.id == ADMIN_USER_ID:
        try:
            TARGET_USER_ID = int(context.args[0])
            initial_message = ' '.join(context.args[1:])  # Get the initial message
            update.message.reply_text(f'Started chat with user {TARGET_USER_ID}.')
            if initial_message:
                context.bot.send_message(chat_id=TARGET_USER_ID, text=initial_message)
        except (IndexError, ValueError):
            update.message.reply_text('Usage: /chat <user_id> <message>')
    else:
        update.message.reply_text('You are not authorized to use this command.')

def forward_message(update: Update, context: CallbackContext):
    global TARGET_USER_ID
    user_id = update.effective_user.id
    message_text = update.message.text

    if user_id == ADMIN_USER_ID and TARGET_USER_ID:
        context.bot.send_message(chat_id=TARGET_USER_ID, text=message_text)
    elif user_id == TARGET_USER_ID:
        context.bot.send_message(chat_id=ADMIN_USER_ID, text=message_text)

def register_new_handlers(dispatcher):
    dispatcher.add_handler(CommandHandler('start_chat', start_admin_chat))
    dispatcher.add_handler(CommandHandler('chat', chat, pass_args=True))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, forward_message))
