from discord_components import Select, SelectOption, Button
import datetime


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
    options = ['Offensive', 'Defensive']
    await set_selections(ctx, 'Select Offensive or Defensive War', options, custom_id)
    interaction = await wait_for_input(bot, custom_id)
    await send_message(interaction)

    return interaction.values[0]


async def select_date(ctx, bot):
    custom_id = 'select3'
    today = datetime.datetime.today().date()
    options = [str(today + datetime.timedelta(days=1)),
               str(today + datetime.timedelta(days=2))]
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


async def confirmation(ctx, bot, zone, offense, date, time):
    await ctx.send("Please confirm: {0} {1} war at {2} PST on {3}".format(zone, offense, time, date),
                   components=[Button(label="Confirm", custom_id="button1")])
    interaction = await bot.wait_for(
        "button_click", check=lambda inter: inter.custom_id == "button1", timeout=60
    )

    await interaction.send(content="Confirmed, announcing war!")


async def start(ctx, bot):
    try:
        zone = await select_zone(ctx, bot)
        offense = await select_offense(ctx, bot)
        date = await select_date(ctx, bot)
        time = await select_time(ctx, bot)

        return zone, offense, date, time
    except:
        await ctx.send('Oops, please try again!')
