import logging
import api

_coin_sticker = "CAADBQADMgADbc38AWOrA-yiyuDxFgQ"

def stats(update, context):
    if "auth" in context.user_data:
        status = api.get_status(context.user_data["auth"])
        if status != False:
            update.message.reply_sticker(_coin_sticker)
            update.message.reply_markdown(
                "Here are your stats:\n- HP: {}\n- Mana Points: {}\n- Exp: {}\n- Gold: {}\n- level: {}".format(
                    round(status["hp"], 1),
                    round(status["mp"], 1),
                    status["exp"],
                    round(status["gp"], 1),
                    status["lvl"],
                )
            )
        else:
            update.message.reply_markdown("Please login by using /start.")
    else:
        update.message.reply_markdown("Please login by using /start.")
