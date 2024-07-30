def start(update, context):
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
        
        # Show inline keyboard
        keyboard = [
            [InlineKeyboardButton("Play Match", callback_data='play')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text("Choose an option:", reply_markup=reply_markup)
    except Exception as e:
        logger.error(f"Error in start command: {e}")
        update.message.reply_text("An error occurred while processing your request.")

def play_callback(update, context):
    query = update.callback_query
    query.answer()
    
    # Show the two options for playing a match
    keyboard = [
        [InlineKeyboardButton("₹10 Entry, Winner- ₹20", callback_data='entry_10')],
        [InlineKeyboardButton("₹20 Entry, Winner- ₹40", callback_data='entry_20')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text("Select your entry fee:", reply_markup=reply_markup)

def entry_callback(update, context):
    query = update.callback_query
    user_id = query.from_user.id
    entry_fee = 10 if query.data == 'entry_10' else 20
    
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT deposit_balance, withdrawal_balance FROM users WHERE user_id = %s", (user_id,))
    user = cur.fetchone()
    
    if user:
        deposit_balance, withdrawal_balance = user
        available_balance = deposit_balance - withdrawal_balance
        
        if available_balance >= entry_fee:
            cur.execute("UPDATE users SET available_balance = available_balance - %s WHERE user_id = %s", (entry_fee, user_id))
            conn.commit()
            
            # Show the Play Match and Cancel buttons
            keyboard = [
                [InlineKeyboardButton("Play Match", callback_data='play_match')],
                [InlineKeyboardButton("Cancel ❌", callback_data='cancel')],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            query.edit_message_text(f"Selected entry fee: ₹{entry_fee}\nChoose an option:", reply_markup=reply_markup)
            
            # Forward message to the group
            context.bot.send_message(chat_id=GROUP_CHAT_ID, text=f"Match started by:\nChatid: {user_id}\nEntry: ₹{entry_fee}\nLudo_Id: {user_id}")
        else:
            query.edit_message_text("Insufficient Balance. Please /Add_Balance.")
    else:
        query.edit_message_text("You don't have an account yet. Send /start to create one.")
    
    cur.close()
    conn.close()

def play_match_callback(update, context):
    query = update.callback_query
    query.answer()
    query.edit_message_text("Match started. Good luck!")

def cancel_callback(update, context):
    query = update.callback_query
    query.answer()
    query.edit_message_text("Match cancelled.")

def main():
    create_table()
    
    global dispatcher
    dispatcher = Dispatcher(bot, None, use_context=True)

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("Account_Balance", account_balance))
    dispatcher.add_handler(CommandHandler("Add_Balance", add_balance))
    dispatcher.add_handler(CallbackQueryHandler(handle_paid, pattern='paid'))
    dispatcher.add_handler(CallbackQueryHandler(play_callback, pattern='play'))
    dispatcher.add_handler(CallbackQueryHandler(entry_callback, pattern='entry_10|entry_20'))
    dispatcher.add_handler(CallbackQueryHandler(play_match_callback, pattern='play_match'))
    dispatcher.add_handler(CallbackQueryHandler(cancel_callback, pattern='cancel'))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    bot.set_webhook(WEBHOOK_URL)
    logger.info(f"Webhook set to {WEBHOOK_URL}")

if __name__ == '__main__':
    main()
    app.run(host='0.0.0.0', port=5000)
