import datetime
import discord
import utils
import spreadsheet


async def select_zone(ctx, bot):
    options = utils.OPTIONS_ZONES
    title = 'Select Zone'

    embed = discord.Embed(title=title,
                          colour=discord.Colour.gold())
    await ctx.send(embed=embed)

    return await utils.get_interaction(bot=bot, ctx=ctx, options=options)


async def select_offense(ctx, bot):
    options = utils.OPTIONS_WAR
    title = 'Select Offense/Defence/Invasion'

    embed = discord.Embed(title=title,
                          colour=discord.Colour.gold())
    await ctx.send(embed=embed)

    return await utils.get_interaction(bot=bot, ctx=ctx, options=options)


async def select_date(ctx, bot):
    today = utils.get_today_date()
    options = [str(today),
               str(today + datetime.timedelta(days=1)),
               str(today + datetime.timedelta(days=2))]
    title = 'Select Date'

    embed = discord.Embed(title=title,
                          colour=discord.Colour.gold())
    await ctx.send(embed=embed)

    return await utils.get_interaction(bot=bot, ctx=ctx, options=options)


async def select_time(ctx, bot):
    options = utils.OPTIONS_TIME
    title = 'Select Start Time (PST)'

    embed = discord.Embed(title=title,
                          colour=discord.Colour.gold())
    await ctx.send(embed=embed)

    return await utils.get_interaction(bot=bot, ctx=ctx, options=options)


async def announce(ctx, bot, cmd_prefix, zone, offense, date, time):
    try:
        emojis = [utils.YES_EMOJI]
        everyone = '@everyone' if cmd_prefix == '.' else ''
        channel = bot.get_channel(utils.WAR_SIGNUP_CHANNEL_ID) if cmd_prefix == '.' \
            else bot.get_channel(utils.BOT_COMMANDS_CHANNEL_ID)
        title = f'{zone} {offense} ({utils.get_weekday(date)} {time}, {date})'
        description = utils.WAR_SIGNUP_DESCRIPTION
        embed = discord.Embed(title=title,
                              description=description,
                              colour=discord.Colour.gold())
        embed.set_image(url=ctx.message.attachments[0].url)
        message = await channel.send(content=everyone, embed=embed)
        await utils.add_emojis(msg=message, emojis=emojis)
    except Exception as e:
        await ctx.send(e)


async def confirm_war(ctx, bot, zone, offense, time, date):
    options = utils.OPTIONS_YES_NO
    title = f'Please Confirm: \n{zone} {offense} ({utils.get_weekday(date)} {time}, {date})'

    embed = discord.Embed(title=title,
                          colour=discord.Colour.gold())
    await ctx.send(embed=embed)

    return await utils.get_interaction(bot=bot, ctx=ctx, options=options)


async def start_selection(ctx, bot, cmd_prefix):
    try:
        zone = await select_zone(ctx, bot)
        offense = await select_offense(ctx, bot)
        date = await select_date(ctx, bot)
        time = await select_time(ctx, bot)
        confirm = await confirm_war(ctx, bot, zone=zone, offense=offense, time=time, date=date)

        if confirm == utils.YES:
            await announce(ctx=ctx, bot=bot, cmd_prefix=cmd_prefix, zone=zone, offense=offense, date=date, time=time)
            spreadsheet.append_to_sheet(sheet_id=spreadsheet.SPREADSHEET_WAR_ATTENDANCE_ID,
                                        _range=spreadsheet.TAB_ALL_WARS,
                                        data=[[date, time, zone, offense]])
    except Exception as e:
        await ctx.send(e)


def get_war_content(message):
    # 'zone offense (weekday, time, date)'
    message = message.replace('(', '')
    char = [',', '(', ')']
    for c in char:
        message = message.replace(c, '')
    message = message.split(' ')

    index_offense = 0
    offenses = utils.OPTIONS_WAR
    for offense in offenses:
        if offense in message:
            index_offense = message.index(offense)
            break

    zone = ' '.join(message[:index_offense])
    offense = message[index_offense]
    # time = message[index_offense + 2]
    date = message[-1]

    return [offense, zone, date]
