from discord_components import Select, SelectOption
import datetime
import utils
import discord


async def set_selections(ctx, title, options, custom_id):
    await ctx.send(
        title,
        components=[
            Select(
                placeholder=title,
                options=[SelectOption(label=option, value=option) for option in options],
                custom_id=custom_id,
            )
        ],
    )


async def wait_for_input(bot, custom_id):
    return await bot.wait_for("select_option", check=lambda inter: inter.custom_id == custom_id, timeout=None)


async def send_message(interaction):
    await interaction.send(content=f"{interaction.values[0]} selected")


async def select_zone(ctx, bot):
    custom_id = 'select1'
    options = ['Brightwood', 'Cutlass Keys', 'Ebonscale Reach', 'Everfall', 'First Light', 'Monarch\'s Bluffs',
               'Mourningdale', 'Reekwater', 'Restless Shore', 'Weaver\'s Fen', 'Windsward']
    await set_selections(ctx, 'Select Zone', options, custom_id)
    interaction = await wait_for_input(bot, custom_id)
    await send_message(interaction)

    return interaction.values[0]


async def select_offense(ctx, bot):
    custom_id = 'select2'
    options = ['Offense', 'Defense', 'Invasion']
    await set_selections(ctx, 'Select Offense/Defence/Invasion', options, custom_id)
    interaction = await wait_for_input(bot, custom_id)
    await send_message(interaction)

    return interaction.values[0]


def get_month_day(date):
    _, month, day = date.split('-')
    return month + '/' + day


async def select_date(ctx, bot):
    custom_id = 'select3'
    today = datetime.datetime.today().date()
    dates = [str(today),
             str(today + datetime.timedelta(days=1)),
             str(today + datetime.timedelta(days=2))]
    options = [get_month_day(date) for date in dates]
    await set_selections(ctx, 'Select Date', options, custom_id)
    interaction = await wait_for_input(bot, custom_id)
    await send_message(interaction)

    return interaction.values[0]


async def select_time(ctx, bot):
    custom_id = 'select4'
    options = ['4PM', '4:30PM', '5PM', '5:30PM', '6PM', '6:30PM', '7PM', '7:30PM', '8PM', '8:30PM', '9PM', '9:30PM',
               '10PM', '10:30PM', '11PM']
    await set_selections(ctx, 'Select Start Time (PST)', options, custom_id)
    interaction = await wait_for_input(bot, custom_id)
    await send_message(interaction)

    return interaction.values[0]


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


async def start(ctx, bot):
    try:
        await ctx.send('Please fill out information for war announcements')
        zone = await select_zone(ctx, bot)
        offense = await select_offense(ctx, bot)
        date = await select_date(ctx, bot)
        time = await select_time(ctx, bot)

        return zone, offense, date, time
    except:
        await ctx.send('Oops, please try again!')
