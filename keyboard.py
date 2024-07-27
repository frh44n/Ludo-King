from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def main_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("Account Balance", callback_data='Account_Balance')],
        [InlineKeyboardButton("Add Balance", callback_data='Add_Balance')],
        [InlineKeyboardButton("Play", callback_data='Play')],
        [InlineKeyboardButton("Withdraw", callback_data='Withdraw')],
    ]
    return InlineKeyboardMarkup(keyboard)

def back_button_keyboard():
    keyboard = [
        [InlineKeyboardButton("Back", callback_data='back')]
    ]
    return InlineKeyboardMarkup(keyboard)
