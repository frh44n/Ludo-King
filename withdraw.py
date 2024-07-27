from telegram import Update
from telegram.ext import CommandHandler, CallbackContext
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def withdraw_command(update: Update, context: CallbackContext):
    update.message.reply_text('Contact "@ludo_king_help", to withdraw money 🤑.')

def register_withdraw_handlers(dispatcher):
    dispatcher.add_handler(CommandHandler('Withdraw', withdraw_command))
