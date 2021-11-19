import discord
import utils
import uuid
import asyncio


async def introduction(bot, user):
    try:
        message = await user.send("Hello! 👋 You have indicated that you might be attending war/invasion."
                                  "\n\n**__Please complete the following questions to be considered in our roster.__**")
        # await utils.add_emojis(message, emojis=[utils.YES_EMOJI, utils.NO_EMOJI])
        custom_id = uuid.uuid4().hex
        options = ['Yes', 'No']
        title = utils.DM_INTRODUCTION_LABEL_MESSAGE + \
                '\n(Select no if it is your first time interacting with this bot or you are unsure.)'
        await utils.set_selections(user, title=title, options=options, custom_id=custom_id)
        interaction = await utils.wait_for_input(bot, custom_id)
        await utils.send_interation_message(interaction)

        return interaction.values[0]

    except:
        await utils.log_in_channel(bot, "Error during DM introduction")


async def send_dm(bot, user):
    try:
        is_new = await introduction(bot, user)
    except:
        await utils.log_in_channel(bot, "Error during DM with {0}".format(user.name))
