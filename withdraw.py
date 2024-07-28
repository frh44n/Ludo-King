from telegram import Update
from telegram.ext import CommandHandler, CallbackContext
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def withdraw_command(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    update.message.reply_text(
        f"👉Withdrawal Request👈\n"
        f"Your user id: {user_id}\n"
        f"Amount :-\n"
        f"UPI id :-\n\n"
        f"Copy this message and enter details, send to @ludo_king_help."
    )

def register_withdraw_handlers(dispatcher):
    dispatcher.add_handler(CommandHandler('Withdraw', withdraw_command))
