import discord
import utils
import spreadsheet


async def init_game_poll(ctx, bot):
    data = spreadsheet.read_sheet(sheet_id=utils.SPREADSHEET_GAME_POLL_ID, _range=utils.TAB_PARTICIPANTS)

    if data:
        title = 'On-going game poll'
        description = 'Please end ongoing game poll first, type **.poll game done**'
        embed = discord.Embed(title=title,
                              description=description,
                              colour=discord.Colour.gold())
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(title=f'Game Poll ({str(utils.get_today_date())})',
                              description=utils.GAME_POLL_MESSAGE + f'\n\n*Click on {utils.GAME_EMOJI} to participate*',
                              colour=discord.Colour.gold())
        channel = bot.get_channel(utils.EVENT_CHANNEL_ID)
        message = await channel.send(content='@everyone', embed=embed)
        await utils.add_emojis(msg=message, emojis=utils.GAME_EMOJI)


async def add_game_prompt(bot, user):
    try:
        data = spreadsheet.read_sheet(sheet_id=utils.SPREADSHEET_GAME_POLL_ID, _range=utils.TAB_GAMES)

        options = utils.OPTIONS_YES_NO
        title = 'Would you like to add a game?'
        description = '**Games currently in the poll:**\n' + ''.join(['\n• ' + d[0] for d in data]) + \
                      '\n\n*Select **NO** to skip*'
        embed = discord.Embed(title=title,
                              description=description,
                              colour=discord.Colour.gold())
        await user.send(embed=embed)

        return await utils.get_interaction(bot=bot, ctx=user, options=options)
    except Exception as e:
        await utils.log_in_channel(bot, utils.error_msg(user, e))


async def update_games(bot, user):
    try:
        title = 'Enter games (up to 3)'
        description = 'Separated by commas (,).\n\nE.g. CSGO, Overwatch, BF2042'
        embed = discord.Embed(title=title,
                              description=description,
                              colour=discord.Colour.gold())
        q = await user.send(embed=embed)

        reply = await bot.wait_for(
            "message",
            timeout=600,
            check=lambda m: m.author == user and m.channel.id == q.channel.id)
        new_games = [game.strip() for game in reply.content.split(',')]

        if len(set(new_games)) > 3:
            title = 'Too many games'
            description = 'Please enter up to 3 games separated by commas.'
            embed = discord.Embed(title=title,
                                  description=description,
                                  colour=discord.Colour.gold())
            await user.send(embed=embed)
            return

        data = spreadsheet.read_sheet(sheet_id=utils.SPREADSHEET_GAME_POLL_ID, _range=utils.TAB_GAMES)
        games = [d[0] for d in data]
        for new_game in new_games:
            if new_game not in games:
                spreadsheet.append_to_sheet(
                    sheet_id=utils.SPREADSHEET_GAME_POLL_ID,
                    _range=utils.TAB_GAMES,
                    data=[[new_game, 1]])

    except Exception as e:
        await utils.log_in_channel(bot, utils.error_msg(user, e))


async def vote_games(bot, user):
    try:
        voted = []
        for i in range(3):
            data = spreadsheet.read_sheet(sheet_id=utils.SPREADSHEET_GAME_POLL_ID, _range=utils.TAB_GAMES)
            games = set([d[0] for d in data]) - set(voted)

            options = [utils.OPTION_DONE] + sorted(games)
            title = 'Vote for up to 3 games'
            description = 'Games currently in the poll:\n' + ''.join(['\n• ' + d[0] for d in data]) + \
                          '\n\n*Select **Done** if finished*'
            embed = discord.Embed(title=title,
                                  description=description,
                                  colour=discord.Colour.gold())
            await user.send(embed=embed)

            game = await utils.get_interaction(bot=bot, ctx=user, options=options)
            if game == utils.OPTION_DONE:
                break

            voted.append(game)

            index, votes = spreadsheet.get_game_index(game)
            spreadsheet.update_sheet_data(sheet_id=utils.SPREADSHEET_GAME_POLL_ID, data=[[game, votes + 1]],
                                          _range=utils.TAB_GAMES + f'!A{index + 2}')

        spreadsheet.append_to_sheet(sheet_id=utils.SPREADSHEET_GAME_POLL_ID, _range=utils.TAB_PARTICIPANTS,
                                    data=[[str(user.id)]])

    except Exception as e:
        await user.send(e)


async def dm_game(bot, user):
    try:
        data = spreadsheet.read_sheet(sheet_id=utils.SPREADSHEET_GAME_POLL_ID, _range=utils.TAB_PARTICIPANTS)
        if not data:
            title = 'Poll has ended'
            description = 'The next poll will be announced in the **Event Channel**, stay tuned!'
            embed = discord.Embed(title=title,
                                  description=description,
                                  colour=discord.Colour.gold())
            await user.send(embed=embed)
            return


        participants = spreadsheet.read_sheet(utils.SPREADSHEET_GAME_POLL_ID, utils.TAB_PARTICIPANTS)
        participants = [p[0] for p in participants]
        if str(user.id) in participants:
            title = 'Seems like you have already voted'
            description = 'If it is a mistake, please contact X.'
            embed = discord.Embed(title=title,
                                  description=description,
                                  colour=discord.Colour.gold())
            await user.send(embed=embed)
            return

        add_game = await add_game_prompt(bot, user)

        while add_game == utils.YES:
            await update_games(bot, user)
            add_game = await add_game_prompt(bot, user)

        await vote_games(bot, user)
        title = 'Thanks for voting!'
        description = 'We will announce results soon. 😊'
        embed = discord.Embed(title=title,
                              description=description,
                              colour=discord.Colour.gold())
        await user.send(embed=embed)
    except Exception as e:
        await user.send(e)


async def announce_winners(bot, winners, almost_won):
    description = 'This week\'s winner game\n\n' + utils.FIRE_EMOJI + \
                  ' **{winners} ({votes} votes)**'.format(winners=', '.join([w[0] for w in winners]),
                                                          votes=winners[0][1])
    if almost_won:
        followed_by = ''
        for game in almost_won:
            followed_by += '{game} ({votes} votes) '.format(game=game[0], votes=game[1])
        description += f'\n\nFollowed by {followed_by}'

    embed = discord.Embed(title='Game Poll Result',
                          description=description,
                          colour=discord.Colour.gold())
    channel = bot.get_channel(utils.EVENT_CHANNEL_ID)
    await channel.send(content='@everyone', embed=embed)

    spreadsheet.clear_game_poll()


async def end_game_poll(ctx, bot):
    data = spreadsheet.read_sheet(sheet_id=utils.SPREADSHEET_GAME_POLL_ID, _range=utils.TAB_GAMES)
    if not data:
        await ctx.send('Cannot fetch data, please message X.')
    else:
        votes_list = set([int(d[1]) for d in data])
        most_vote = max(votes_list)
        winners = []
        for d in data:
            if int(d[1]) == most_vote:
                winners.append(d)

        almost_won = []
        if len(votes_list) >= 3:
            for i in range(2):
                votes_list.remove(most_vote)
                most_vote = max(votes_list)
                for d in data:
                    if int(d[1]) == most_vote:
                        almost_won.append(d)

        await announce_winners(bot, winners, almost_won)
