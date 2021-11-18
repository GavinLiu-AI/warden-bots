import utils
import discord


async def announce(ctx, channel, message, offense, emojis):
    try:
        if offense == 'Invasion':
            image_path = utils.IMAGE_INVASION
        else:
            image_path = utils.IMAGE_WAR

        msg = await channel.send(message, file=discord.File(image_path))
        for emoji in emojis:
            await msg.add_reaction(emoji)
    except:
        await ctx.send('Oops, please try again!')
