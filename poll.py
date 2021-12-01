import discord
import utils
import spreadsheet
import uuid


def poll_exist(data):
    return max([int(d[1]) for d in data]) > 1


async def init_game_poll(ctx, bot):
    data = spreadsheet.read_sheet(sheet_id=utils.SPREADSHEET_GAME_POLL_ID, _range=utils.TAB_GAMES)

    if poll_exist(data):
        await ctx.send('Please end ongoing game poll first, type **.poll game done**')
    else:
        embed = discord.Embed(title='Game Poll ({0})'.format(str(utils.get_today_date())),
                              description=utils.GAME_POLL_MESSAGE + '\n\n*Click on {0} to participate*'.format(
                                  utils.GAME_EMOJI),
                              colour=discord.Colour.gold())
        channel = bot.get_channel(utils.EVENT_CHANNEL_ID)
        message = await channel.send(content='@everyone', embed=embed)
        await utils.add_emojis(msg=message, emojis=utils.GAME_EMOJI)


async def add_game_prompt(bot, user):
    try:
        data = spreadsheet.read_sheet(sheet_id=utils.SPREADSHEET_GAME_POLL_ID, _range=utils.TAB_GAMES)

        custom_id = uuid.uuid4().hex
        options = utils.OPTIONS_YES_NO
        title = 'Games currently in the poll:\n' + \
                ''.join(['\n• ' + d[0] for d in data]) + \
                '\n\n❕ __**Would you like to add a game?**__ *(Select NO to skip and proceed to vote.)*'

        return await utils.get_interaction(bot=bot, user=user, custom_id=custom_id, options=options, title=title)
    except Exception as e:
        await utils.log_in_channel(bot, utils.format_error_msg(user, e))


async def update_games(bot, user):
    try:
        q = await user.send('❕ __**Enter the names of the games (up to 3), separated by commas (,)**__ '
                            '\n*(E.g. CSGO, Overwatch, BF2042)*')

        reply = await bot.wait_for(
            "message",
            timeout=600,
            check=lambda m: m.author == user and m.channel.id == q.channel.id)
        new_games = [game.strip() for game in reply.content.split(',')]

        if len(set(new_games)) > 3:
            await user.send('Please enter up to 3 games separated by commas.')
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
        await utils.log_in_channel(bot, utils.format_error_msg(user, e))


async def vote_games(bot, user):
    try:
        voted = []
        for i in range(3):
            data = spreadsheet.read_sheet(sheet_id=utils.SPREADSHEET_GAME_POLL_ID, _range=utils.TAB_GAMES)
            games = set([d[0] for d in data]) - set(voted)

            custom_id = uuid.uuid4().hex
            options = games
            title = 'Games currently in the poll:\n' + \
                    ''.join(['\n• ' + d[0] for d in data]) + \
                    '\n\n🗳️ __**Vote for 3 games (unordered)**__'

            game = await utils.get_interaction(bot=bot, user=user, custom_id=custom_id, options=options, title=title)
            voted.append(game)

            index, votes = spreadsheet.get_game_index(game)
            spreadsheet.update_sheet_data(sheet_id=utils.SPREADSHEET_GAME_POLL_ID, data=[[game, votes + 1]],
                                          _range=utils.TAB_GAMES + '!A{0}'.format(index + 2))

    except Exception as e:
        await user.send(e)


async def dm_game(bot, user):
    try:
        add_game = await add_game_prompt(bot, user)

        while add_game == utils.YES:
            await update_games(bot, user)
            add_game = await add_game_prompt(bot, user)

        await vote_games(bot, user)
        await user.send('Thanks for voting! We will announce results soon. 😊')
    except Exception as e:
        await user.send(e)


async def announce_winners(bot, winners, almost_won):
    description = 'This week\'s winner game\n\n' + utils.FIRE_EMOJI + \
                  ' **{0} ({1} votes)**'.format(', '.join([w[0] for w in winners]), winners[0][1])
    if almost_won:
        followed_by = ''
        for game in almost_won:
            followed_by += '{0} ({1} votes) '.format(game[0], game[1])
        description += '\n\nFollowed by {0}'.format(followed_by)

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
