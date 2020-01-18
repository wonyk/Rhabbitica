from telegram.ext import (
    Updater,
    InlineQueryHandler,
    CommandHandler,
    MessageHandler,
    Filters,
)
import logging
import requests
import re
import api

uid = None
tid = None


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
    task_type = update.effective_message.text.split()[1]
    text = " ".join([str(elem) for elem in update.effective_message.text.split()[2:]])
    resp = api.create_task(text, task_type)

    if resp.status_code != 201:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Cannot create task: {} {}".format(resp.status_code, resp.json()),
        )

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Created task. ID: {}".format(resp.json()),
    )


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


def main():
    updater = Updater(
        token="845289799:AAGynfA8Y3WmzK0oTDFMM92z6ADM04pVyIc", use_context=True
    )
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("userid", user_id))
    dp.add_handler(CommandHandler("tokenid", token_id))

    handler = MessageHandler(Filters.text, command_handle)
    dp.add_handler(handler)

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
