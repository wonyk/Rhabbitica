from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Updater,
    InlineQueryHandler,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackQueryHandler,
    ConversationHandler
)
import logging
import requests
import re
import api
import env

uid = None
tid = None

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

TYPE, TITLE = range(2)


def start(update, context):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Hi! please do a few things first.\n\n*Get your userID.*\nTo find your User ID:\n\t\tFor the website: User Icon > Settings > API.\n\t\tFor iOS/Android App: Menu > Settings > API > User ID (tap on it to copy it to your clipboard).\n\n"
        + "*Get your token Id* \n\t\tTo find your API Token,\nFor the website: User Icon > Settings > API \n\t\tFor iOS/Android App: Menu > API > API Token (tap on it to copy it to your clipboard).\n\n"
        + "*set userID and tokenId after with* /userid _userid here_ *and* /tokenid _tokenid here_ *respectively*",
        parse_mode="Markdown",
    )


def user_id(update, context):
    uid = update.effective_message.text.split()[1]
    if len(uid) != 0:
        context.bot.send_message(
            chat_id=update.effective_chat.id, text="User Id set: " + uid
        )
        api.set_id(uid, tid)
    else:
        context.bot.send_message(
            chat_id=update.effective_chat.id, text="User Id Not set"
        )


def token_id(update, context):
    tid = update.effective_message.text.split()[1]
    if len(tid) != 0:
        context.bot.send_message(
            chat_id=update.effective_chat.id, text="Token Id set: " + tid
        )
        api.set_id(uid, tid)
    else:
        context.bot.send_message(
            chat_id=update.effective_chat.id, text="Token Id Not set"
        )


def create_tasks(update, context):
    reply_keyboard = [[InlineKeyboardButton("Habit", callback_data='habit'),
                 InlineKeyboardButton("Daily", callback_data='daily')],
                [InlineKeyboardButton("Todo", callback_data='todo'),
                InlineKeyboardButton("Reward", callback_data='reward')]]

    # reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text('Please choose:', ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return TYPE

def create_title(update, context):
    user = update.message.from_user
    logger.info("Type of %s:%s", user, update.message.text)
    update.message.reply_text('I see! Please send me a photo of yourself, '
        'so I know what you look like, or send /skip if you don\'t want to.')

    # task_type = update.effective_message.text.split()[1]
    # text = " ".join([str(elem) for elem in update.effective_message.text.split()[2:]])
    # resp = api.create_task(text, task_type)

    # if resp.status_code != 201:
    #     context.bot.send_message(
    #         chat_id=update.effective_chat.id,
    #         text="Cannot create task: {} {}".format(resp.status_code, resp.json()),
    #     )

    # context.bot.send_message(
    #     chat_id=update.effective_chat.id,
    #     text="Created task. ID: {}".format(resp.json()),
    # )


def get_tasks(update, context):
    resp = api.get_tasks()
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Task: {} {}".format(resp.status_code, resp.json()),
    )


def command_handle(update, context):
    create = "#create"
    get = "#get"
    if create in update.message.text:
        create_tasks(update, context)
    elif get in update.message.text:
        get_tasks(update, context)
    else:
        context.bot.send_message(
            chat_id=update.effective_chat.id, text="I don't understand that command"
        )

def cancel(update, context):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text('Bye! I hope we can talk again some day.',
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


def main():
    updater = Updater(
        token=env.api_key, use_context=True
    )
    dp = updater.dispatcher

    createConvo = ConversationHandler(
        entry_points=[MessageHandler(Filters.text, command_handle)],

        states={
            TYPE: [MessageHandler(Filters.regex('^(habit|daily|todo|reward)$'), create_tasks)],
            TITLE: [MessageHandler(Filters.text, create_title)]
        },
         fallbacks=[CommandHandler('cancel', cancel)]
    )


    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("userid", user_id))
    dp.add_handler(CommandHandler("tokenid", token_id))
    # dp.add_handler(CallbackQueryHandler(button))
    dp.add_handler(createConvo)
    # handler = MessageHandler(Filters.text, command_handle)
    # dp.add_handler(handler)

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
