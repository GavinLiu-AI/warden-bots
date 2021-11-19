from discord_components import ComponentsBot
from sys import exit
import configs
import utils
from survey import role_selection
from war_announcement import war_declaration

bot = ComponentsBot('.')
awake = True


@bot.event
async def on_ready():
    print(bot.user)


@bot.event
async def on_raw_reaction_add(payload):
    if not awake:
        return

    try:
        # Skip if bot added emoji
        if payload.user_id == bot.user.id:
            return

        # Skip if message/dm wasn't posted by bot
        message = await bot.get_channel(payload.channel_id).fetch_message(payload.message_id)

        emoji_name = payload.emoji.name
        # War signup
        if utils.WAR_SIGNUP_LABEL_MESSAGE in message.content:
            await utils.remove_other_reactions(bot, payload=payload, message=message, emoji_name=emoji_name)
            # War selection
            if emoji_name == utils.YES_EMOJI or emoji_name == utils.MAYBE_EMOJI:
                user = await bot.fetch_user(user_id=payload.user_id)
                await role_selection.send_dm(bot, user)
            else:
                return

    except:
        await utils.log_in_channel(bot, "Error during on_raw_reaction_add")


@bot.command(brief='(Admin) Declare war and make war announcements',
             description='(Admin) Declare war and make war announcements')
async def declare(ctx, *args):
    if not awake:
        return

    if not await utils.is_admin(ctx):
        return

    try:
        zone, offense, date, time = await war_declaration.start(ctx, bot)

        custom_msg = ''
        if args:
            custom_msg = '\n\n' + ' '.join(args)

        emojis = [utils.YES_EMOJI, utils.MAYBE_EMOJI, utils.NO_EMOJI]
        message = utils.WAR_SIGNUP_LABEL_MESSAGE + "{0} {1} at {2} PST on {3}!**".format(zone, offense, time, date) + \
                  custom_msg + \
                  "\n\nClick on one of the reactions to let us know your availability. " \
                  "\n{0}: Attending\n{1}: Tentative\n{2}: Not Attending".format(utils.YES_EMOJI,
                                                                                utils.MAYBE_EMOJI,
                                                                                utils.NO_EMOJI)
        channel = bot.get_channel(utils.BOT_COMMANDS_CHANNEL_ID)
        await war_declaration.announce(ctx, channel, message, offense, emojis)
    except:
        await ctx.send('Error during war declaration')


@bot.command(brief='(Dev) Feature testing',
             description='(Dev) Feature testing')
async def test(ctx):
    if not awake:
        return

    if not await utils.is_dev(ctx):
        return


@bot.command(brief='(Dev) Get channel ID',
             description='(Dev) Get channel ID')
async def channel_id(ctx, channel_name=None):
    if not awake:
        return

    if not await utils.is_dev(ctx):
        return

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


@bot.command(brief='Get bot status',
             description='Get bot status')
async def status(ctx):
    try:
        if awake:
            await ctx.send('{0} is online'.format(bot.user.name))
        else:
            await ctx.send('{0} is online but deactivated. Type ".activate" command for activation.'.format(bot.user.name))
    except:
        await ctx.send('Error checking bot status')


@bot.command(brief='(Admin) Deactivate bot',
             description='(Admin) Deactivate bot')
async def deactivate(ctx):
    if not await utils.is_admin(ctx):
        return

    try:
        await utils.log_in_channel(bot, 'Bot is now deactivated. Type command ".activate" for activation')
        global awake
        awake = False
    except:
        await ctx.send('Error during deactivation')


@bot.command(brief='(Admin) Activate bot',
             description='(Admin) Activate bot')
async def activate(ctx):
    if not await utils.is_admin(ctx):
        return

    try:
        await utils.log_in_channel(bot, "Bot is now online.")
        global awake
        awake = True
    except:
        await ctx.send('Error during activation')


bot.run(configs.WAR_BOT_TOKEN)
