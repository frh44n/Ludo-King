from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, Filters, CallbackContext
import logging
from ludo_king import get_db_connection, GROUP_CHAT_ID

def withdraw_command(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    update.message.reply_text("Enter Amount:")
    context.user_data['withdraw_state'] = 'waiting_for_amount'
    context.user_data['withdraw_user_id'] = user_id

def handle_withdraw_amount(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if context.user_data.get('withdraw_state') == 'waiting_for_amount' and context.user_data['withdraw_user_id'] == user_id:
        try:
            amount = float(update.message.text)
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("SELECT available_balance FROM users WHERE user_id = %s", (user_id,))
            user = cur.fetchone()

            if user and user[0] >= amount:
                context.user_data['withdraw_amount'] = amount
                update.message.reply_text("Enter your UPI ID:")
                context.user_data['withdraw_state'] = 'waiting_for_upi'
            else:
                update.message.reply_text("Insufficient Balance. Add Balance by pressing this button 🔘 /Add_Balance")
                context.user_data['withdraw_state'] = None
            cur.close()
            conn.close()
        except ValueError:
            update.message.reply_text("Please enter a valid amount.")
            context.user_data['withdraw_state'] = 'waiting_for_amount'

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
