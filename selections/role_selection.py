import discord
import utils


async def introduction(user):
    return


async def send_dm(bot, user):
    try:
        await introduction(user)
        await user.send("test")
    except:
        channel = bot.get_channel(utils.BOT_COMMANDS_CHANNEL_ID)
        await channel.send("Error sending dm to " + user.name)
