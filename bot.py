# bot.py
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from config import BOT_TOKEN, LINK_URL
from googlesearch import search
from bs4 import BeautifulSoup
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),  # Save logs to bot.log
        logging.StreamHandler()  # Print logs to console
    ]
)
logger = logging.getLogger(__name__)

# In-memory storage
started_users = set()  # Tracks users who have used /start
user_modes = {}  # Tracks user modes: 'love' or 'playstore'

# Default mode
DEFAULT_MODE = 'love'

def get_app_poster(app_name):
    """Search for the app's feature graphic on Google Play."""
    logger.info(f"Searching for poster of app: {app_name}")
    try:
        query = f"{app_name} google play store app"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        search_results = list(search(query, num_results=3))  # Get up to 3 results for better reliability
        logger.info(f"Search results for {app_name}: {search_results}")
        
        for url in search_results:
            if "play.google.com" in url and "/store/apps/details" in url:
                logger.info(f"Fetching Play Store page: {url}")
                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for images that could be the feature graphic
                img_tags = soup.find_all('img', attrs={'src': True})
                for img in img_tags:
                    src = img['src']
                    # Check for feature graphic (often 1024x500 or marked as key visual)
                    if src and ('1024x500' in src or 'feature' in src.lower() or 'promo' in src.lower()):
                        logger.info(f"Found potential poster: {src}")
                        return src if src.startswith('http') else f"https://play.google.com{src}"
                
                # Fallback: Look for meta tags with og:image (often used for app preview)
                meta_image = soup.find('meta', attrs={'property': 'og:image'})
                if meta_image and meta_image.get('content'):
                    logger.info(f"Found og:image: {meta_image['content']}")
                    return meta_image['content']
                
                logger.warning(f"No poster found in page: {url}")
        
        logger.warning(f"No valid Play Store URL found for {app_name}")
        return None
    except Exception as e:
        logger.error(f"Error fetching poster for {app_name}: {str(e)}")
        return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message is None:
        logger.warning("Received update with no message in start")
        return
    user_id = update.message.from_user.id
    logger.info(f"User {user_id} sent /start")
    if user_id not in started_users:
        started_users.add(user_id)
        user_modes[user_id] = DEFAULT_MODE
        await send_mode_buttons(update, context, "Welcome! Choose a mode:")
    else:
        await send_mode_buttons(update, context, "You've already started! Choose a mode:")

async def send_mode_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
    if update.message is None:
        logger.warning("Received update with no message in send_mode_buttons")
        return
    keyboard = [
        [
            InlineKeyboardButton("I Love U Mode", callback_data='love'),
            InlineKeyboardButton("Play Store Mode", callback_data='playstore')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(text, reply_markup=reply_markup)
    logger.info(f"Sent mode buttons to user {update.message.from_user.id}")

async def send_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message is None:
        logger.warning("Received update with no message in send_link")
        return
    keyboard = [[InlineKeyboardButton("Open Link", url=LINK_URL)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Click the button below:", reply_markup=reply_markup)
    logger.info(f"Sent link button to user {update.message.from_user.id}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message is None:
        logger.warning("Received update with no message in handle_message")
        return
    user_id = update.message.from_user.id
    text = update.message.text.lower()
    logger.info(f"User {user_id} sent message: {text}")
    
    # Initialize mode if not set
    if user_id not in user_modes:
        user_modes[user_id] = DEFAULT_MODE
        await send_mode_buttons(update, context, "Mode not set. Choose a mode:")
        logger.info(f"Initialized mode to {DEFAULT_MODE} for user {user_id}")
        return

    mode = user_modes[user_id]
    
    if mode == 'love':
        if text == "i love u":
            await update.message.reply_text("I love you too ❤️")
            logger.info(f"Replied 'I love you too' to user {user_id}")
        else:
            await send_link(update, context)
    elif mode == 'playstore':
        app_name = update.message.text.strip()
        logger.info(f"Processing app name {app_name} in Play Store mode for user {user_id}")
        poster_url = get_app_poster(app_name)
        if poster_url:
            await update.message.reply_photo(photo=poster_url, caption=f"Poster for {app_name}")
            logger.info(f"Sent poster for {app_name} to user {user_id}")
        else:
            await update.message.reply_text(f"Could not find a poster for {app_name}. Try a different app name.")
            logger.warning(f"Failed to find poster for {app_name} for user {user_id}")
        # Show mode buttons again
        await send_mode_buttons(update, context, "Current mode: Play Store. Choose a mode:")

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query is None or query.message is None:
        if query:
            await query.answer()
        logger.warning("Received callback with no query or message")
        return
    user_id = query.from_user.id
    mode = query.data
    
    user_modes[user_id] = mode
    await query.answer(f"Switched to {mode.capitalize()} mode!")
    logger.info(f"User {user_id} switched to {mode} mode")
    
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
    logger.info(f"Updated mode message for user {user_id}")

def main():
    logger.info("Starting bot")
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CallbackQueryHandler(button_callback))

    application.run_polling()
    logger.info("Bot stopped")

if __name__ == '__main__':
    main()
