from telegram.ext import CommandHandler, MessageHandler, Filters, ConversationHandler
import api
import logging

SET_USER_ID, SET_USER_KEY = range(2)
_start_sticker = "CAADBQADLwADbc38AdU1wUDmBM3jFgQ"
_reward_sticker = "CAADBQADMwADbc38Ab8X1fBrA7qZFgQ"


def start(update, context):
    context.bot.send_sticker(chat_id=update.message.chat_id, sticker=_start_sticker)
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text="Hello! My name is *Rhabbit*. Welcome to Rhabbitica, an alternate universe of the *Habitica* world! Before we get started, could I trouble you to identify yourself?\nPlease key in your Habitica User ID"
        + "\n\n*To get your user ID:*\nFrom the website: User Icon > Settings > API.\nFrom iOS/Android App: Menu > Settings > API > User ID (tap on it to copy it to your clipboard).\n\n",
        parse_mode="Markdown",
    )
    return SET_USER_ID
    # schedule.every(_quote_time).seconds.do(quote_gen, update, context)
    # schedule.every(_quote_pic_time).seconds.do(quote_pic_gen, update, context)
    # ScheduleThread().start()


# Function linked to SET_USER_ID
def get_user_id(update, context):
    uid = update.message.text
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text="User Id set: *"
        + uid
        + "*.\n\nNext, please key in your Habitica User API key."
        + "\n\n*To get your API key:*\nFrom the website: User Icon > Settings > API \nFrom iOS/Android App: Menu > API > API Token (tap on it to copy it to your clipboard).\n\n"
        + "To restart: /restart",
        parse_mode="Markdown",
    )
    context.chat_data['user-id'] = uid
    return SET_USER_KEY


# Function linked to SET_USER_KEY
def get_user_key(update, context):
    key = update.message.text
    context.bot.send_sticker(chat_id=update.message.chat_id, sticker=_reward_sticker)
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text="API Key set: *"
        + key
        + "*.\n\n*Thank you! You may start enjoying Rhabbitica's functions now!*"
        + "\n\nTo get started: /help"
        + "\nTo reset your credentials: /start",
        parse_mode="Markdown",
    )
    api.set_user_data(context.chat_data['user-id'], key)
    return -1


# Add conversation for init basic data using start
start_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        SET_USER_ID: [MessageHandler(Filters.text, get_user_id)],
        SET_USER_KEY: [MessageHandler(Filters.text, get_user_key)],
    },
    fallbacks=[CommandHandler("restart", start)],
    allow_reentry=True,
)

