import uuid
import spreadsheet
import utils


async def get_ign_confirm(bot, user):
    try:
        q = await user.send('❕ __**What is your In Game Name?**__')

        reply = await bot.wait_for(
            "message",
            timeout=600,
            check=lambda m: m.author == user and m.channel.id == q.channel.id)
        ign = reply.content.strip()

        if not ign:
            await user.send('_Invalid Name._')
            return ign, utils.NO

        custom_id = uuid.uuid4().hex
        options = utils.OPTIONS_YES_NO
        title = '❔ __**Confirm your IGN as {0}?**__'.format(ign)

        return ign, await utils.get_interaction(bot=bot, user=user, custom_id=custom_id, options=options, title=title)
    except Exception as e:
        await utils.log_in_channel(bot, utils.format_error_msg(user, e))


async def get_role(bot, user):
    try:
        custom_id = uuid.uuid4().hex
        options = utils.OPTIONS_ROLES
        title = '⚔ __**What is your in game role?**__'

        role = await utils.get_interaction(bot=bot, user=user, custom_id=custom_id, options=options, title=title)
        return role.split(' ', 1)[1]
    except Exception as e:
        await utils.log_in_channel(bot, utils.format_error_msg(user, e))


async def get_weapon(bot, user, string):
    try:
        custom_id = uuid.uuid4().hex
        options = utils.OPTIONS_WEAPONS
        title = '🗡️ __**What is your ' + string + ' weapon?**__'

        return await utils.get_interaction(bot=bot, user=user, custom_id=custom_id, options=options, title=title)
    except Exception as e:
        await utils.log_in_channel(bot, utils.format_error_msg(user, e))


async def ask_gear_score(bot, user):
    try:
        q = await user.send('⚠ __**What is your Gear Score (integer, 0-600)?**__')

        reply = await bot.wait_for(
            "message",
            timeout=600,
            check=lambda m: m.author == user and m.channel.id == q.channel.id)
        gs = reply.content

        if not gs.isdigit():
            await user.send('Invalid Number.')
            return 0

        gs = int(gs)
        if gs <= 0 or gs > 600:
            await user.send('Invalid Range, 0-600 only.')
            return 0

        return gs
    except Exception as e:
        await utils.log_in_channel(bot, utils.format_error_msg(user, e))


async def get_weapons(bot, user):
    weapon_1 = await get_weapon(bot, user, 'primary')
    weapon_2 = await get_weapon(bot, user, 'secondary')

    if weapon_1 == weapon_2:
        await user.send('Both weapons cannot be the same, try again')
        weapon_1 = await get_weapon(bot, user, 'primary')
        weapon_2 = await get_weapon(bot, user, 'secondary')

    return weapon_1, weapon_2


async def get_ign(bot, user):
    ign, confirmed = await get_ign_confirm(bot, user)
    while not ign:
        ign, confirmed = await get_ign_confirm(bot, user)
    while confirmed != utils.YES:
        ign, confirmed = await get_ign_confirm(bot, user)

    return ign


async def get_gear_score(bot, user):
    gear_score = await ask_gear_score(bot, user)
    while not gear_score:
        gear_score = await ask_gear_score(bot, user)

    return gear_score


async def get_company(bot, user):
    try:
        q = await user.send('🛡️ __**What is your company name?**__')

        reply = await bot.wait_for(
            "message",
            timeout=600,
            check=lambda m: m.author == user and m.channel.id == q.channel.id)
        return reply.content.strip()
    except Exception as e:
        await utils.log_in_channel(bot, utils.format_error_msg(user, e))


async def get_in_company(bot, user):
    try:
        custom_id = uuid.uuid4().hex
        options = utils.OPTIONS_YES_NO
        title = '🛡️ __**Are you in a company?**__'

        return await utils.get_interaction(bot=bot, user=user, custom_id=custom_id, options=options, title=title)
    except Exception as e:
        await utils.log_in_channel(bot, utils.format_error_msg(user, e))


def user_id_exists(data, user_id):
    ids = [int(row[0]) for row in data]
    for id in ids:
        if user_id == id:
            return True
    return False


async def greet_new_player(bot, user):
    try:
        custom_id = uuid.uuid4().hex
        options = utils.OPTIONS_YES_NO
        title = "Hello! 👋 You have indicated that you might be attending war/invasion." \
                "\n\n**Please complete the following questions to be considered in our roster.** " + \
                "\n\n⚠ __**Have you uploaded info via Wardens War Bot before?**__" + \
                '\n(Select *No* if it is your first time interacting with this bot or if you are unsure.)'

        return await utils.get_interaction(bot=bot, user=user, custom_id=custom_id, options=options, title=title)
    except Exception as e:
        await utils.log_in_channel(bot, utils.format_error_msg(user, e))


def get_player_info(data):
    return '\n\nYou are {0} of {1}, a {2} using {3} and {4}, your gear score is {5}.' \
            .format(data[2], data[4], data[5], data[6], data[7], data[8])


async def ask_for_update(bot, user, data):
    try:
        custom_id = uuid.uuid4().hex
        options = utils.OPTIONS_YES_NO

        player_info_msg = get_player_info(data)
        title = utils.DM_SURVEY_RETURNING_PLAYER_MESSAGE + player_info_msg + utils.DM_SURVEY_UPDATE_PROMPT

        return await utils.get_interaction(bot=bot, user=user, custom_id=custom_id, options=options, title=title)
    except Exception as e:
        await utils.log_in_channel(bot, utils.format_error_msg(user, e))


async def is_warden_prompt(bot, user):
    try:
        custom_id = uuid.uuid4().hex
        options = utils.OPTIONS_YES_NO
        title = '⚔ __**Are you a Warden?**__'

        return await utils.get_interaction(bot=bot, user=user, custom_id=custom_id, options=options, title=title)
    except Exception as e:
        await utils.log_in_channel(bot, utils.format_error_msg(user, e))


async def get_warden_company(bot, user):
    try:
        custom_id = uuid.uuid4().hex
        options = utils.OPTIONS_WARDEN_COMPANIES
        title = '⚔ __**Which Warden company are you in?**__'

        return await utils.get_interaction(bot=bot, user=user, custom_id=custom_id, options=options, title=title)
    except Exception as e:
        await utils.log_in_channel(bot, utils.format_error_msg(user, e))


async def get_company_prompts(bot, user):
    company = 'None'
    is_warden = await is_warden_prompt(bot, user)
    if is_warden == utils.YES:
        company = await get_warden_company(bot, user)
    else:
        in_company = await get_in_company(bot, user)
        if in_company == utils.YES:
            company = await get_company(bot, user)

    return company, is_warden


async def start_survey(bot, user, player_exist):
    ign = await get_ign(bot, user)
    company, is_warden = await get_company_prompts(bot, user)
    role = await get_role(bot, user)
    weapon_1, weapon_2 = await get_weapons(bot, user)
    gear_score = await get_gear_score(bot, user)

    data = [str(user.id), str(user), ign, is_warden, company, role, weapon_1, weapon_2, gear_score]
    if not player_exist:
        spreadsheet.upload_war_data(data=data)
    else:
        spreadsheet.upload_war_data(data=data, update=True)

    return data


async def update_player_data(bot, user, player_data):
    try:
        custom_id = uuid.uuid4().hex
        options = utils.OPTIONS_UPDATES
        title = get_player_info(player_data) + '\n\n__**Would you like to update your info?**__ ' \
                                               '*(Select Done if everything is up-to-date)*'

        choice = await utils.get_interaction(bot=bot, user=user, custom_id=custom_id, options=options, title=title)

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
            await user.send(utils.DM_SURVEY_INTRO_MESSAGE)
            player_data = await start_survey(bot, user, player_exist=False)

            if war_content:
                spreadsheet.upload_war_signup(data=player_data + war_content)
        else:
            player_data = all_data[spreadsheet.get_user_index(_range=utils.TAB_DATA, user_id=user.id)]
            if war_content:
                spreadsheet.upload_war_signup(data=player_data+war_content)

            finished = False
            while not finished:
                new_data, finished = await update_player_data(bot, user, player_data)
                if war_content:
                    spreadsheet.upload_war_signup(data=new_data + war_content)

        if war_content:
            await user.send("Thank you for completing the survey, make sure to sign up at the war board in game. 😊")
        else:
            await user.send("Thank you for completing the survey! 😊")

    except Exception as e:
        await utils.log_in_channel(bot, utils.format_error_msg(user, e))
