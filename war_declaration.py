import datetime
import uuid
import discord
import utils


async def select_zone(ctx, bot):
    custom_id = uuid.uuid4().hex
    options = utils.OPTIONS_ZONES
    title = '**Please fill out information for war announcements**\n\n⚔ __**Select Zone**__'

    return await utils.get_interaction(bot=bot, user=ctx, custom_id=custom_id, options=options, title=title)


async def select_offense(ctx, bot):
    custom_id = uuid.uuid4().hex
    options = utils.OPTIONS_WAR
    title = '⚔ __**Select Offense/Defence/Invasion**__'

    return await utils.get_interaction(bot=bot, user=ctx, custom_id=custom_id, options=options, title=title)


async def select_date(ctx, bot):
    custom_id = uuid.uuid4().hex
    today = utils.get_today_date()
    options = [str(today),
               str(today + datetime.timedelta(days=1)),
               str(today + datetime.timedelta(days=2))]
    title = '⚔ __**Select Date**__'

    return await utils.get_interaction(bot=bot, user=ctx, custom_id=custom_id, options=options, title=title)


async def select_time(ctx, bot):
    custom_id = uuid.uuid4().hex
    options = utils.OPTIONS_TIME
    title = '⚔ __**Select Start Time (PST)**__'

    return await utils.get_interaction(bot=bot, user=ctx, custom_id=custom_id, options=options, title=title)


async def announce(ctx, channel, message, offense, emojis):
    try:
        if offense == 'Invasion':
            image_path = utils.IMAGE_INVASION
        else:
            image_path = utils.IMAGE_WAR

        msg = await channel.send(message, file=discord.File(image_path))
        await utils.add_emojis(msg, emojis)
    except Exception as e:
        await ctx.send(e)


async def confirm_war(ctx, bot, zone, offense, time, date):
    custom_id = uuid.uuid4().hex
    options = utils.OPTIONS_YES_NO
    title = '⚔ __**Confirm war announcement: {0} {1} at {2} PST on {3}**__'.format(zone, offense, time, date)

    return await utils.get_interaction(bot=bot, user=ctx, custom_id=custom_id, options=options, title=title)


async def start(ctx, bot):
    try:
        zone = await select_zone(ctx, bot)
        offense = await select_offense(ctx, bot)
        date = await select_date(ctx, bot)
        time = await select_time(ctx, bot)
        confirm = await confirm_war(ctx, bot, zone=zone, offense=offense, time=time, date=date)

        return zone, offense, date, time, confirm
    except Exception as e:
        await ctx.send(e)


def get_announcement_message(cmd_prefix, zone, offense, time, date, custom_msg):
    message = '\n@everyone ' if cmd_prefix == '.' else ''
    message = message + \
              utils.WAR_SIGNUP_LABEL + \
              "\n\nLocation: {0} {1} \nTime: {2} PST\nDate: {3} **".format(zone, offense, time, date) + custom_msg + \
              "\n\nClick on one of the reactions to let us know your availability. " \
              "\n_(Please complete the survey if you receive one from Wardens War Bot. " \
              "If the survey expires type .update in channel to add/edit your loadout)_" \
              "\n{0}: Attending {1}: Tentative {2}: Not Attending".format(utils.YES_EMOJI, utils.MAYBE_EMOJI,
                                                                          utils.NO_EMOJI)
    return message


def get_war_content(message, reaction):
    message = message.split(' ')
    war_format = ''
    zone = ''
    date = ''
    for i, j in enumerate(message):
        if 'Location:' in j:
            zone = message[i + 1]
            war_format = message[i + 2]
        elif 'Date:' in j:
            date = message[i + 1]

    if reaction == utils.YES_EMOJI:
        attend = 'Yes'
    elif reaction == utils.MAYBE_EMOJI:
        attend = 'Maybe'
    else:
        attend = 'No'

    return [war_format, zone, date, attend]
