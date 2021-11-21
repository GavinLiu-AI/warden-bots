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


def get_month_day(date):
    _, month, day = date.split('-')
    return month + '/' + day


async def select_date(ctx, bot):
    custom_id = uuid.uuid4().hex
    today = datetime.datetime.today().date()
    dates = [str(today),
             str(today + datetime.timedelta(days=1)),
             str(today + datetime.timedelta(days=2))]
    options = [get_month_day(date) for date in dates]
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
    except:
        await ctx.send('Error during war announcement')


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
    except:
        await ctx.send('Error during war declaration')


def get_announcement_message(zone, offense, time, date, custom_msg):
    message = '\n@everyone\n' + utils.WAR_SIGNUP_LABEL_MESSAGE + \
              "{0} {1} at {2} PST on {3}!**".format(zone, offense, time, date) + \
              custom_msg + \
              "\n\nClick on one of the reactions to let us know your availability. " \
              "\n_(Please complete the survey if you receive one from Wardens War Bot. " \
              "If the survey expires type .update in channel to add/edit your loadout)_" \
              "\n{0}: Attending {1}: Tentative {2}: Not Attending"\
                  .format(utils.YES_EMOJI, utils.MAYBE_EMOJI, utils.NO_EMOJI)
    return message
