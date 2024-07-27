from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CommandHandler, CallbackQueryHandler, CallbackContext

def start_with_inline_keyboard(update: Update, context: CallbackContext):
    try:
        user_id = update.message.from_user.id
        # Database interaction logic if needed
        # ...

        # Create an inline keyboard with buttons for each command
        keyboard = [
            [InlineKeyboardButton("/Account_Balance", callback_data='Account_Balance')],
            [InlineKeyboardButton("/Add_Balance", callback_data='Add_Balance')],
            [InlineKeyboardButton("/Play", callback_data='Play')]
            # Add more buttons for other commands as needed
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text('Select a command:', reply_markup=reply_markup)
    except Exception as e:
        update.message.reply_text("An error occurred while processing your request.")

def handle_inline_callback_query(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    if query.data == 'Account_Balance':
        context.bot.send_message(chat_id=query.message.chat_id, text="/Account_Balance")
    elif query.data == 'Add_Balance':
        context.bot.send_message(chat_id=query.message.chat_id, text="/Add_Balance")
    elif query.data == 'Play':
        context.bot.send_message(chat_id=query.message.chat_id, text="/Play")
    else:
        query.edit_message_text(text="Unknown command.")

def register_inline_handlers(dispatcher):
    dispatcher.add_handler(CommandHandler('start', start_with_inline_keyboard))
    dispatcher.add_handler(CallbackQueryHandler(handle_inline_callback_query))
