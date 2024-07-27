import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters, CallbackContext
from sqlalchemy import create_engine, Column, BigInteger, Numeric, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# SQLAlchemy setup
DATABASE_URL = 'postgres://default:gaFjrs9b4oLK@ep-ancient-smoke-a1pliqaw.ap-southeast-1.aws.neon.tech:5432/verceldb?sslmode=require'
Base = declarative_base()
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

class User(Base):
    __tablename__ = 'users'
    user_id = Column(BigInteger, primary_key=True)
    available_balance = Column(Numeric, default=0)
    deposit_balance = Column(Numeric, default=0)
    withdrawal_balance = Column(Numeric, default=0)

Base.metadata.create_all(engine)

# Bot token
TOKEN = '7256179302:AAEKIqy4U--JL6pypx47YsNhuTVRrNO2j4k'

def start(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if not session.query(User).filter_by(user_id=user_id).first():
        new_user = User(user_id=user_id)
        session.add(new_user)
        session.commit()
        update.message.reply_text("Welcome! Your account has been created.")
    else:
        update.message.reply_text("Welcome back!")

def account_balance(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    user = session.query(User).filter_by(user_id=user_id).first()
    if user:
        update.message.reply_text(
            f"Available Balance: {user.available_balance}\n"
            f"Deposit Balance: {user.deposit_balance}\n"
            f"Withdrawal Balance: {user.withdrawal_balance}"
        )
    else:
        update.message.reply_text("You don't have an account yet. Send /start to create one.")

def add_balance(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Pay minimum ₹10 on UPI [9931071170@fam].",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("PAID", callback_data='paid')]
        ])
    )

def handle_paid(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    query.message.reply_text("Enter 12-digit UTR.")
    context.user_data['waiting_for_utr'] = True

def handle_message(update: Update, context: CallbackContext):
    if context.user_data.get('waiting_for_utr'):
        user_id = update.message.from_user.id
        utr = update.message.text
        context.bot.send_message(chat_id='1002156476121', text=f"user_id: {user_id}, UTR: {utr}")
        update.message.reply_text("Your UTR has been forwarded.")
        context.user_data['waiting_for_utr'] = False

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("Account_Balance", account_balance))
    dp.add_handler(CommandHandler("Add_Balance", add_balance))
    dp.add_handler(CallbackQueryHandler(handle_paid, pattern='paid'))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
