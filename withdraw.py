from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, Filters, CallbackContext
import logging
from ludo_king import GROUP_CHAT_ID

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def withdraw_command(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    context.user_data['withdraw_state'] = 'waiting_for_amount'
    context.user_data['withdraw_user_id'] = user_id
    update.message.reply_text("Enter Amount:")

def handle_withdraw_amount(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if context.user_data.get('withdraw_state') == 'waiting_for_amount' and context.user_data['withdraw_user_id'] == user_id:
        amount = update.message.text
        context.user_data['withdraw_amount'] = amount
        context.user_data['withdraw_state'] = 'waiting_for_upi'
        update.message.reply_text("Enter your UPI ID:")

def handle_withdraw_upi(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if context.user_data.get('withdraw_state') == 'waiting_for_upi' and context.user_data['withdraw_user_id'] == user_id:
        upi_id = update.message.text
        amount = context.user_data['withdraw_amount']
        context.bot.send_message(
            chat_id=GROUP_CHAT_ID,
            text=f"Withdraw request\nuser_id: {user_id}\namount: {amount}\nUPI: {upi_id}"
        )
        update.message.reply_text("Your withdraw request has been forwarded.")
        context.user_data['withdraw_state'] = None

def register_withdraw_handlers(dispatcher):
    dispatcher.add_handler(CommandHandler('Withdraw', withdraw_command))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_withdraw_amount))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_withdraw_upi))
