# bot.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from config import BOT_TOKEN, LINK_URL

# In-memory set to track users who have used /start
started_users = set()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message is None:
        return
    user_id = update.message.from_user.id
    if user_id not in started_users:
        # Add user to started_users set
        started_users.add(user_id)
        # Send the link with button
        await send_link(update, context)
    else:
        # Inform user they've already started
        await update.message.reply_text("You've already started! Send any message or 'i love u' for a response.")

async def send_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message is None:
        return
    # Create a button with the link
    keyboard = [[InlineKeyboardButton("Open Link", url=LINK_URL)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    # Send the message with the button
    await update.message.reply_text("Click the button below:", reply_markup=reply_markup)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message is None:
        return
    text = update.message.text.lower()
    if text == "i love u":
        await update.message.reply_text("I love you too ❤️")
    else:
        # Send the link for any other message
        await send_link(update, context)

def main():
    # Initialize the bot
    application = Application.builder().token(BOT_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start the bot
    application.run_polling()

if __name__ == '__main__':
    main()
