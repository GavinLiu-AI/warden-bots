import datetime
import uuid

import discord

import utils


async def select_zone(ctx, bot):
    custom_id = uuid.uuid4().hex
    options = ['Brightwood', 'Cutlass Keys', 'Ebonscale Reach', 'Everfall', 'First Light', 'Monarch\'s Bluffs',
               'Mourningdale', 'Reekwater', 'Restless Shore', 'Weaver\'s Fen', 'Windsward']
    title = '**Please fill out information for war announcements**\n\n⚔ __**Select Zone**__'
    await utils.set_selections(ctx, title=title, options=options, custom_id=custom_id)
    interaction = await utils.wait_for_input(bot, custom_id)
    await utils.send_interation_message(interaction)

    return interaction.values[0]


async def select_offense(ctx, bot):
    custom_id = uuid.uuid4().hex
    options = ['Offense', 'Defense', 'Invasion']
    title = '⚔ __**Select Offense/Defence/Invasion**__'
    await utils.set_selections(ctx, title=title, options=options, custom_id=custom_id)
    interaction = await utils.wait_for_input(bot, custom_id)
    await utils.send_interation_message(interaction)

    return interaction.values[0]


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
    await utils.set_selections(ctx, title=title, options=options, custom_id=custom_id)
    interaction = await utils.wait_for_input(bot, custom_id)
    await utils.send_interation_message(interaction)

    return interaction.values[0]


async def select_time(ctx, bot):
    custom_id = uuid.uuid4().hex
    options = ['4PM', '4:30PM', '5PM', '5:30PM', '6PM', '6:30PM', '7PM', '7:30PM', '8PM', '8:30PM', '9PM', '9:30PM',
               '10PM', '10:30PM', '11PM']
    title = '⚔ __**Select Start Time (PST)**__'
    await utils.set_selections(ctx, title=title, options=options, custom_id=custom_id)
    interaction = await utils.wait_for_input(bot, custom_id)
    await utils.send_interation_message(interaction)

    return interaction.values[0]


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


async def start(ctx, bot):
    try:
        zone = await select_zone(ctx, bot)
        offense = await select_offense(ctx, bot)
        date = await select_date(ctx, bot)
        time = await select_time(ctx, bot)

        return zone, offense, date, time
    except:
        await ctx.send('Error during war declaration')