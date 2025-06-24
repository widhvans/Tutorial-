# bot.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from config import BOT_TOKEN, LINK_URL
from googlesearch import search
from bs4 import BeautifulSoup
import requests
import re

# In-memory storage
started_users = set()  # Tracks users who have used /start
user_modes = {}  # Tracks user modes: 'love' or 'playstore'

# Default mode
DEFAULT_MODE = 'love'

def get_app_poster(app_name):
    """Search for the app's feature graphic on Google Play."""
    try:
        query = f"{app_name} site:play.google.com feature graphic"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        for url in search(query, num_results=1):
            if "play.google.com" in url:
                response = requests.get(url, headers=headers)
                soup = BeautifulSoup(response.text, 'html.parser')
                # Look for images that might be the feature graphic
                img_tags = soup.find_all('img')
                for img in img_tags:
                    src = img.get('src')
                    if src and ('1024x500' in src or 'feature' in src.lower()):
                        return src if src.startswith('http') else f"https://play.google.com{src}"
        return None
    except Exception as e:
        print(f"Error fetching poster: {e}")
        return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message is None:
        return
    user_id = update.message.from_user.id
    if user_id not in started_users:
        started_users.add(user_id)
        user_modes[user_id] = DEFAULT_MODE
        await send_mode_buttons(update, context, "Welcome! Choose a mode:")
    else:
        await send_mode_buttons(update, context, "You've already started! Choose a mode:")

async def send_mode_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
    if update.message is None:
        return
    keyboard = [
        [
            InlineKeyboardButton("I Love U Mode", callback_data='love'),
            InlineKeyboardButton("Play Store Mode", callback_data='playstore')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(text, reply_markup=reply_markup)

async def send_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message is None:
        return
    keyboard = [[InlineKeyboardButton("Open Link", url=LINK_URL)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Click the button below:", reply_markup=reply_markup)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message is None:
        return
    user_id = update.message.from_user.id
    text = update.message.text.lower()
    
    # Initialize mode if not set
    if user_id not in user_modes:
        user_modes[user_id] = DEFAULT_MODE
        await send_mode_buttons(update, context, "Mode not set. Choose a mode:")
        return

    mode = user_modes[user_id]
    
    if mode == 'love':
        if text == "i love u":
            await update.message.reply_text("I love you too ❤️")
        else:
            await send_link(update, context)
    elif mode == 'playstore':
        app_name = update.message.text.strip()
        poster_url = get_app_poster(app_name)
        if poster_url:
            await update.message.reply_photo(photo=poster_url, caption=f"Poster for {app_name}")
        else:
            await update.message.reply_text(f"Could not find a poster for {app_name}. Try a different app name.")
        # Show mode buttons again
        await send_mode_buttons(update, context, "Current mode: Play Store. Choose a mode:")

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.message is None:
        await query.answer()
        return
    user_id = query.from_user.id
    mode = query.data
    
    user_modes[user_id] = mode
    await query.answer(f"Switched to {mode.capitalize()} mode!")
    
    # Update the message with the new mode
    text = f"Current mode: {'I Love U' if mode == 'love' else 'Play Store'}. Choose a mode:"
    keyboard = [
        [
            InlineKeyboardButton("I Love U Mode", callback_data='love'),
            InlineKeyboardButton("Play Store Mode", callback_data='playstore')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text=text, reply_markup=reply_markup)

def main():
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CallbackQueryHandler("button_callback", button_callback=button_callback))

    application.run_polling()

__name__ == '__main__':
    main()
