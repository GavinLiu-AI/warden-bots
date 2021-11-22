from discord_components import ComponentsBot

import configs
import spreadsheet
import utils
from survey import role_selection
from war_announcement import war_declaration

bot = ComponentsBot('/')
awake = True
cmd_prefix = bot.command_prefix

@bot.event
async def on_ready():
    print(bot.user)


@bot.event
async def on_raw_reaction_add(payload):
    if not awake:
        return

    try:
        if cmd_prefix != '.' and payload.user_id != utils.X_ID:
            return

        # Skip if bot added emoji
        if payload.user_id == bot.user.id:
            return

        # Skip if message/dm wasn't posted by bot
        message = await bot.get_channel(payload.channel_id).fetch_message(payload.message_id)

        emoji_name = payload.emoji.name
        # War signup
        war_content = war_declaration.get_war_content(message.content, emoji_name)
        if utils.WAR_SIGNUP_LABEL_MESSAGE in message.content:
            user = await bot.fetch_user(user_id=payload.user_id)
            await utils.remove_other_reactions(bot, payload=payload, message=message, emoji_name=emoji_name)
            # War selection
            if emoji_name == utils.YES_EMOJI or emoji_name == utils.MAYBE_EMOJI:
                await role_selection.send_dm(bot, user, war_content=war_content)
            else:
                all_data = spreadsheet.read(_range=utils.TAB_DATA)
                player_data = all_data[spreadsheet.find_user_row(_range=utils.TAB_DATA, user_id=user.id)] + war_content
                spreadsheet.upload_war_signup(data=player_data)
    except:
        await utils.log_in_channel(bot, "Error during on_raw_reaction_add")


@bot.command(brief='Update player information and loadout',
             description='Update player information and loadout')
async def update(ctx):
    if not awake:
        return

    try:
        user = await bot.fetch_user(user_id=ctx.author.id)
        await role_selection.send_dm(bot, user, war_content=None)
    except:
        await ctx.send('Error during war declaration')


@bot.command(brief='(Admin) Declare war and make war announcements',
             description='(Admin) Declare war and make war announcements')
async def declare(ctx, *args):
    if not awake:
        return

    if not await utils.is_admin(ctx):
        return

    try:
        zone, offense, date, time, confirm = await war_declaration.start(ctx, bot)

        if confirm == utils.YES:
            custom_msg = ''
            if args:
                custom_msg = '\n\n' + ' '.join(args)

            emojis = [utils.YES_EMOJI, utils.MAYBE_EMOJI, utils.NO_EMOJI]
            message = war_declaration.get_announcement_message(cmd_prefix=cmd_prefix, zone=zone, offense=offense,
                                                               time=time, date=date, custom_msg=custom_msg)

            channel = bot.get_channel(utils.WAR_SIGNUP_CHANNEL_ID) if cmd_prefix == '.' \
                else bot.get_channel(utils.BOT_COMMANDS_CHANNEL_ID)
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
            await ctx.send(utils.get_online_msg(bot))
        else:
            await ctx.send(utils.get_deactivation_msg(bot))
    except:
        await ctx.send('Error checking bot status')


@bot.command(brief='(Admin) Deactivate bot',
             description='(Admin) Deactivate bot')
async def deactivate(ctx):
    if not await utils.is_admin(ctx):
        return

    try:
        await ctx.send(utils.get_deactivation_msg(bot))
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
        await ctx.send(utils.get_online_msg(bot))
        global awake
        awake = True
    except:
        await ctx.send('Error during activation')


bot.run(configs.WAR_BOT_TOKEN)
