import logging
import api
_coin_sticker = "CAADBQADMgADbc38AWOrA-yiyuDxFgQ"


def stats(update, context):
    status = api.get_status()
    logging.info(status)
    update.message.reply_sticker(_coin_sticker)
    update.message.reply_markdown(
        "Here are your stats: \n"
        + "- HP: {} \n".format(status["hp"])
        + "- Mana Points: {} \n".format(round(status["mp"], 1))
        + "- Exp: {}\n".format(status["exp"])
        + "- Gold: {}\n".format(round(status["gp"], 1))
        + "- level: {}\n".format(status["lvl"]),
    )
