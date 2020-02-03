import logging
import api

_coin_sticker = "CAADBQADMgADbc38AWOrA-yiyuDxFgQ"


def stats(update, context):
    if "auth" in context.user_data:
        status = api.get_status(context.user_data["auth"])
        logging.info(status)
        if (status != False):
            update.message.reply_sticker(_coin_sticker)
            update.message.reply_markdown(
                "Here are your stats: \n"
                + "- HP: {} \n".format(status["hp"])
                + "- Mana Points: {} \n".format(round(status["mp"], 1))
                + "- Exp: {}\n".format(status["exp"])
                + "- Gold: {}\n".format(round(status["gp"], 1))
                + "- level: {}\n".format(status["lvl"]),
            )
        else:
            update.message.reply_markdown("Please login by using /start.")
    else:
        update.message.reply_markdown("Please login by using /start.")
