from discord_components import ComponentsBot
from selections import war_selection, war_declaration, role_selection
import utils

import configs

bot = ComponentsBot('.')


@bot.event
async def on_ready():
    print('Logged on as', bot.user)


@bot.event
async def on_raw_reaction_add(payload):
    try:
        # Skip if bot added emoji
        if payload.user_id == bot.user.id:
            return

        # Skip if message wasn't posted by bot
        message = await bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
        if message.author.id != bot.user.id:
            return

        emoji = payload.emoji.name
        # War selection
        if emoji == utils.WAR_CONFIRMED_EMOJI or emoji == utils.WAR_TENTATIVE_EMOJI:
            user = await bot.fetch_user(user_id=payload.user_id)
            await role_selection.send_dm(bot, user)
        else:
            return
    except:
        channel = bot.get_channel(utils.BOT_COMMANDS_CHANNEL_ID)
        await channel.send("Error during raw reaction add")


@bot.command()
async def declare(ctx, *args):
    if not set([role.name for role in ctx.author.roles]).intersection(set(utils.ADMIN_ROLES)):
        await ctx.send('Not authorized for this command.')
        await ctx.send('Roles that can .declare: Moderator, War-Lead, Squad Lead, Grand Master Warden, Master Warden')
        return

    try:
        zone, offense, date, time = await war_selection.start(ctx, bot)

        custom_msg = ''
        if args:
            custom_msg = '\n\n' + ' '.join(args)

        emojis = [utils.WAR_CONFIRMED_EMOJI, utils.WAR_TENTATIVE_EMOJI, utils.WAR_DECLINED_EMOJI]
        message = "War/Invasion Sign up: {0} {1} at {2} PST on {3}!".format(zone, offense, time, date) + \
                  custom_msg + \
                  "\n\nClick on one of the reactions to let us know your availability. " \
                  "\n{0}: Attending\n{1}: Tentative\n{2}: Not Attending".format(utils.WAR_CONFIRMED_EMOJI,
                                                                                utils.WAR_TENTATIVE_EMOJI,
                                                                                utils.WAR_DECLINED_EMOJI)
        channel = bot.get_channel(utils.BOT_COMMANDS_CHANNEL_ID)
        await war_declaration.announce(ctx, channel, message, offense, emojis)
    except:
        channel = bot.get_channel(utils.BOT_COMMANDS_CHANNEL_ID)
        await channel.send("Error during war declaration")


@bot.command()
async def test(ctx):
    channel = bot.get_channel(utils.BOT_COMMANDS_CHANNEL_ID)
    msg = await channel.send("something")
    await msg.add_reaction("✅")
    # await war_declaration.announce(ctx, bot, channel, " ", emojis)


@bot.command()
async def channel_id(ctx, channel_name=None):
    try:
        channel_id = None
        for channel in ctx.guild.channels:
            if channel.name == channel_name:
                channel_id = channel.id

        if channel_id:
            await ctx.send(channel_id)
        else:
            await ctx.send('Channel ID not found.')
    except:
        await ctx.send('Error fetching channel id')

# @bot.command()
# async def chat(ctx, *args):
#     try:
#         channel = bot.get_channel(utils.GENERAL_CHANNEL_ID)
#         msg = await channel.send(' '.join(args))
#     except:
#         ctx.send("Error sending message")


bot.run(configs.WAR_BOT_TOKEN)
