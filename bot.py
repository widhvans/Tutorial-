# bot.py
import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from config import BOT_TOKEN, LINK_URL

def start(update, context):
    send_link(update, context)

def send_link(update, context):
    # Create a button with the link
    keyboard = [[InlineKeyboardButton("Open Link", url=LINK_URL)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Send the message with the button
    update.message.reply_text("Click the button below:", reply_markup=reply_markup)

def main():
    # Initialize the bot
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    # Add handlers
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, send_link))

    # Start the bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
