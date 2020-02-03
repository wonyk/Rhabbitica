from telegram.ext import CommandHandler, MessageHandler, Filters, ConversationHandler
import api
import logging

SET_USERNAME, SET_USERPASS = range(2)
_start_sticker = "CAADBQADLwADbc38AdU1wUDmBM3jFgQ"
_reward_sticker = "CAADBQADMwADbc38Ab8X1fBrA7qZFgQ"


def start(update, context):
    context.bot.send_sticker(chat_id=update.message.chat_id, sticker=_start_sticker)
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text="Hello! My name is *Rhabbit*. Welcome to Rhabbitica, an alternate universe of the *Habitica* world! Before we get started, could I trouble you to identify yourself?"
        + "\n\nPlease key in your Habitica username or email:",
        parse_mode="Markdown",
    )
    return SET_USERNAME
    # schedule.every(_quote_time).seconds.do(quote_gen, update, context)
    # schedule.every(_quote_pic_time).seconds.do(quote_pic_gen, update, context)
    # ScheduleThread().start()


# Function linked to SET_USERNAME or redirect if login fails
def get_username(update, context):
    username = update.message.text
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text="Username / Email set: *"
        + username
        + "*\n\nNext, please key in your Habitica Password:"
        + "\n\nTo restart: /restart",
        parse_mode="Markdown",
    )
    context.chat_data["username"] = username
    return SET_USERPASS


# Function linked to SET_USERPASS
def get_userpass(update, context):
    password = update.message.text
    context.bot.delete_message(
        chat_id=update.message.chat_id, message_id=update.message.message_id,
    )
    context.bot.send_message(
        chat_id=update.message.chat_id,
        text="Password entered successfully. Logging you in...",
    )
    res = api.login(context.chat_data["username"], password)
    # res will return in the following formats:
    # 1. False - Server Error
    # 2. {'success': True, 'data': {...}} for correct logins
    # 3. {'success': False} for incorrect auth

    if res == False:
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text="The server encountered an error. Please try again later.",
        )
        return -1
    elif res["success"] == True:
        context.bot.send_sticker(
            chat_id=update.message.chat_id, sticker=_reward_sticker
        )
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text="Welcome to Rhabbitica, "
            + res["data"]["username"]
            + "\nYou may start enjoying Rhabbitica's functions now!"
            + "\n\nTo get started: /help"
            + "\nTo reset your credentials: /start",
        )
        context.user_data["auth"] = {
            "_uid": res["data"]["id"],
            "_key": res["data"]["apiToken"],
        }
        logging.info(context.user_data["auth"])
        return -1
    else:
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text="Your email address / username or password is incorrect. Please try again."
            + "\n\nPlease key in your Habitica username or email",
            parse_mode="Markdown",
        )
        # Remove the previous auth if user sends in wrong details
        if "auth" in context.user_data:
            context.user_data.pop("auth")
        return SET_USERNAME


# Add conversation for init basic data using start
start_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        SET_USERNAME: [MessageHandler(Filters.text, get_username)],
        SET_USERPASS: [MessageHandler(Filters.text, get_userpass)],
    },
    fallbacks=[CommandHandler("restart", start)],
    allow_reentry=True,
)

