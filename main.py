from discord_components import Button, ComponentsBot
from selections import war_selection, war_declaration
import utils

import configs

bot = ComponentsBot('.')


@bot.event
async def on_ready():
    print('Logged on as', bot.user)


@bot.event
async def on_reaction_add(reaction, user):
    if user.bot:
        return
    if reaction.message.author.id != bot.user.id:
        return

    emoji = reaction.emoji
    # War selection
    if emoji == utils.WAR_CONFIRMED_EMOJI or emoji == utils.WAR_TENTATIVE_EMOJI:
        channel = bot.get_channel(utils.BOT_COMMANDS_CHANNEL_ID)
        await channel.send(user.id)
    else:
        return


# @bot.command()
# async def button(ctx):
#     await ctx.send("Buttons!", components=[Button(label="Button", custom_id="button1")])
#     interaction = await bot.wait_for(
#         "button_click", check=lambda inter: inter.custom_id == "button1"
#     )
#     await interaction.send(content="Button Clicked")


@bot.command()
async def declare(ctx):
    zone, offense, date, time = await war_selection.start(ctx, bot)

    emojis = [utils.WAR_CONFIRMED_EMOJI, utils.WAR_TENTATIVE_EMOJI, utils.WAR_DECLINED_EMOJI]
    message = "War/Invasion Sign up: {0} {1} at {2} PST on {3}! " \
              "\n\nClick on one of the reactions to let us know your availability." \
              "\n{4}: Attending\n{5}: Tentative\n{6}: Not Attending" \
        .format(zone, offense, time, date, utils.WAR_CONFIRMED_EMOJI, utils.WAR_TENTATIVE_EMOJI,
                utils.WAR_DECLINED_EMOJI)
    channel = bot.get_channel(utils.BOT_COMMANDS_CHANNEL_ID)
    await war_declaration.announce(ctx, channel, message, offense, emojis)


@bot.command()
async def test(ctx):
    channel = bot.get_channel(utils.BOT_COMMANDS_CHANNEL_ID)
    msg = await channel.send("something")
    await msg.add_reaction("✅")
    # await war_declaration.announce(ctx, bot, channel, " ", emojis)


@bot.command()
async def channel_id(ctx, given_name=None):
    try:
        channel_id = None
        for channel in ctx.guild.channels:
            if channel.name == given_name:
                channel_id = channel.id

        if channel_id:
            await ctx.send(channel_id)
        else:
            await ctx.send("Channel ID not found.")
    except:
        await ctx.send("Something went wrong.")


bot.run(configs.WAR_BOT_TOKEN)
