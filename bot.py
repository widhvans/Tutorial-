# bot.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from config import BOT_TOKEN, LINK_URL

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_link(update, context)

async def send_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Create a button with the link
    keyboard = [[InlineKeyboardButton("Open Link", url=LINK_URL)]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Send the message with the button
    await update.message.reply_text("Click the button below:", reply_markup=reply_markup)

def main():
    # Initialize the bot
    application = Application.builder().token(BOT_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, send_link))

    # Start the bot
    application.run_polling()

if __name__ == '__main__':
    main()
