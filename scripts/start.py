from telegram.ext import CommandHandler, MessageHandler, Filters, ConversationHandler
import api
import logging

SET_USER_ID, SET_USER_KEY = range(2)
_start_sticker = "CAADBQADLwADbc38AdU1wUDmBM3jFgQ"


def start(update, context):
    context.bot.send_sticker(chat_id=update.effective_chat.id, sticker=_start_sticker)
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Hello! My name is *Rhabbit*. Welcome to Rhabbitica, an alternate universe of the *Habitica* world! Before we get started, could I trouble you to identify yourself?\n\n*Get your userID.*\nTo find your User ID:\n\t\tFrom the website: User Icon > Settings > API.\n\t\tFrom iOS/Android App: Menu > Settings > API > User ID (tap on it to copy it to your clipboard).\n\n"
        + "*Get your token Id* \n\t\tTo find your API Token,\nFrom the website: User Icon > Settings > API \n\t\tFrom iOS/Android App: Menu > API > API Token (tap on it to copy it to your clipboard).\n\n"
        + "*set userID and tokenId after with* /userid _userid here_ *and* /tokenid _tokenid here_ *respectively*",
        parse_mode="Markdown",
    )
    context.bot.send_message(
        chat_id=update.effective_chat.id, text="To get started: /help"
    )

    return SET_USER_ID
    # schedule.every(_quote_time).seconds.do(quote_gen, update, context)
    # schedule.every(_quote_pic_time).seconds.do(quote_pic_gen, update, context)
    # ScheduleThread().start()


# Init the basic user data at the start and save it


def get_user_id(update, context):
    uid = update.message.text
    context.bot.send_message(chat_id=update.message.chat_id, text="User Id set: " + uid)
    api.set_user_id(uid)
    return SET_USER_KEY


def get_user_key(update, context):
    key = update.message.text
    context.bot.send_message(
        chat_id=update.message.chat_id, text="Token Id set: " + key
    )
    api.set_user_key(key)
    return -1


def restart(update, context):
    logging.info("Unexpected command within conversation")
    return ConversationHandler.END


# Add conversation for init basic data using start
start_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        SET_USER_ID: [MessageHandler(Filters.text, get_user_id)],
        SET_USER_KEY: [MessageHandler(Filters.text, get_user_key)],
    },
    fallbacks=[CommandHandler("restart", restart)],
)

