import uuid
import spreadsheet
import utils
import discord


async def get_role(bot, user):
    try:
        options = utils.OPTIONS_ROLES
        title = 'What is your role?'
        embed = discord.Embed(title=title,
                              colour=discord.Colour.gold())
        await user.send(embed=embed)

        role = await utils.get_interaction(bot=bot, ctx=user, options=options)
        return role.split(' ', 1)[1]
    except Exception as e:
        await utils.log_in_channel(bot, utils.error_msg(user, e))


async def get_weapon(bot, user, string, weapon_1=None):
    try:
        if weapon_1:
            options = sorted(set(utils.OPTIONS_WEAPONS) - {[weapon_1]})
        else:
            options = sorted(utils.OPTIONS_WEAPONS)
        title = 'What is your ' + string + ' weapon?'
        embed = discord.Embed(title=title,
                              colour=discord.Colour.gold())
        await user.send(embed=embed)

        return await utils.get_interaction(bot=bot, ctx=user, options=options)
    except Exception as e:
        await utils.log_in_channel(bot, utils.error_msg(user, e))


async def ask_gear_score(bot, user):
    try:
        title = 'What is your Gear Score? (integer, 0-600)'
        embed = discord.Embed(title=title,
                              colour=discord.Colour.gold())
        q = await user.send(embed=embed)

        reply = await bot.wait_for(
            "message",
            timeout=600,
            check=lambda m: m.author == user and m.channel.id == q.channel.id)
        gs = reply.content

        if not gs.isdigit():
            await user.send('Not a integer, try again')
            return 0

        gs = int(gs)
        if gs <= 0 or gs > 600:
            await user.send('Invalid Range, 0-600 only. Try again')
            return 0

        return gs
    except Exception as e:
        await utils.log_in_channel(bot, utils.error_msg(user, e))


async def get_weapons(bot, user):
    weapon_1 = await get_weapon(bot=bot, user=user, string='primary')
    weapon_2 = await get_weapon(bot=bot, user=user, string='secondary', weapon_1=weapon_1)

    return weapon_1, weapon_2


async def get_ign(bot, user):
    try:
        title = 'What is your in game name?'
        embed = discord.Embed(title=title,
                              colour=discord.Colour.gold())
        q = await user.send(embed=embed)

        reply = await bot.wait_for(
            "message",
            timeout=600,
            check=lambda m: m.author == user and m.channel.id == q.channel.id)
        return reply.content.strip()
    except Exception as e:
        await utils.log_in_channel(bot, utils.error_msg(user, e))


async def get_gear_score(bot, user):
    gear_score = await ask_gear_score(bot, user)
    while not gear_score:
        gear_score = await ask_gear_score(bot, user)

    return gear_score


async def get_company(bot, user):
    try:
        title = 'What is your company name?'
        description = '*Type **None** if you are not in a company*'
        embed = discord.Embed(title=title,
                              description=description,
                              colour=discord.Colour.gold())
        q = await user.send(embed=embed)

        reply = await bot.wait_for(
            "message",
            timeout=600,
            check=lambda m: m.author == user and m.channel.id == q.channel.id)
        return reply.content.strip()
    except Exception as e:
        await utils.log_in_channel(bot, utils.error_msg(user, e))


def user_id_exists(data, user_id):
    ids = [int(row[0]) for row in data]
    for id in ids:
        if user_id == id:
            return True
    return False


def get_player_info(data):
    return f'**Name**: {data[2]}\n\n**Company**: {data[4]}\n\n**Role**: {data[5]}\n\n**Primary Weapon**: {data[6]}' \
           f'\n\n**Secondary Weapon**: {data[7]}\n\n**Gear Score**: {data[8]}'


async def is_warden_prompt(bot, user):
    try:
        options = utils.OPTIONS_YES_NO
        title = 'Are you a Warden?'
        embed = discord.Embed(title=title,
                              colour=discord.Colour.gold())
        await user.send(embed=embed)

        return await utils.get_interaction(bot=bot, ctx=user, options=options)
    except Exception as e:
        await utils.log_in_channel(bot, utils.error_msg(user, e))


async def get_company_prompts(bot, user):
    is_warden = await is_warden_prompt(bot, user)
    if is_warden == utils.YES:
        return 'Wardens', is_warden
    else:
        company = await get_company(bot, user)

    return company, is_warden


async def start_survey(bot, user):
    # Send intro message
    embed = discord.Embed(title=utils.DM_SURVEY_INTRO_TITLE,
                          description=utils.DM_SURVEY_INTRO_DESCRIPTION,
                          colour=discord.Colour.gold())
    await user.send(embed=embed)

    ign = await get_ign(bot, user)
    company, is_warden = await get_company_prompts(bot, user)
    role = await get_role(bot, user)
    weapon_1, weapon_2 = await get_weapons(bot, user)
    gear_score = await get_gear_score(bot, user)

    data = [str(user.id), str(user), ign, is_warden, company, role, weapon_1, weapon_2, gear_score]
    spreadsheet.upload_war_data(data=data)

    return data


async def update_player_data(bot, user, player_data):
    try:
        options = utils.OPTIONS_UPDATES

        title = 'Would you like to update your data?'
        description = get_player_info(player_data) + '\n\n*Select **Done** if everything is up-to-date*'
        embed = discord.Embed(title=title,
                              description=description,
                              colour=discord.Colour.gold())
        await user.send(embed=embed)

        choice = await utils.get_interaction(bot=bot, ctx=user, options=options)

        ign = player_data[2]
        is_warden = player_data[3]
        company = player_data[4]
        role = player_data[5]
        weapon_1 = player_data[6]
        weapon_2 = player_data[7]
        gear_score = player_data[8]

        if choice == utils.OPTION_UPDATE_IGN:
            ign = await get_ign(bot, user)
        elif choice == utils.OPTION_UPDATE_COMP:
            company, is_warden = await get_company_prompts(bot, user)
        elif choice == utils.OPTION_UPDATE_ROLE:
            role = await get_role(bot, user)
        elif choice == utils.OPTION_UPDATE_WEAPON:
            weapon_1, weapon_2 = await get_weapons(bot, user)
        elif choice == utils.OPTION_UPDATE_GS:
            gear_score = await get_gear_score(bot, user)
        elif choice == utils.OPTION_DONE:
            return player_data, True

        new_data = [str(user.id), str(user), ign, is_warden, company, role, weapon_1, weapon_2, gear_score]
        spreadsheet.upload_war_data(data=new_data, update=True)

        return new_data, False
    except Exception as e:
        await user.send(e)


async def send_dm(bot, user, war_content=None):
    try:
        all_data = spreadsheet.read_sheet(sheet_id=utils.SPREADSHEET_WAR_ID, _range=utils.TAB_DATA)
        player_exist = user_id_exists(all_data, user.id)

        if not player_exist:
            player_data = await start_survey(bot, user)

            if war_content:
                spreadsheet.upload_war_signup(data=player_data + war_content)
        else:
            player_data = all_data[spreadsheet.get_user_index(_range=utils.TAB_DATA, user_id=user.id)]
            if war_content:
                spreadsheet.upload_war_signup(data=player_data + war_content)

            finished = False
            while not finished:
                player_data, finished = await update_player_data(bot, user, player_data)
                if war_content:
                    spreadsheet.upload_war_signup(data=player_data + war_content)

        description = 'Your data has been uploaded.'
        if war_content:
            description += '\n*Make sure to sign up at the war board in game.*'

        title = 'Thank you for completing the survey! 😎'
        embed = discord.Embed(title=title,
                              description=description,
                              colour=discord.Colour.gold())
        await user.send(embed=embed)

    except Exception as e:
        await utils.log_in_channel(bot, utils.error_msg(user, e))
