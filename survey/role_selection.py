import uuid

import utils


async def init(bot, user):
    try:
        custom_id = uuid.uuid4().hex
        options = [utils.YES, utils.NO]
        title = "Hello! 👋 You have indicated that you might be attending war/invasion." \
                "\n\n**Please complete the following questions to be considered in our roster.** " + \
                "\n\n⚠ __**Have you uploaded info via Wardens War Bot before?**__" + \
                '\n(Select *No* if it is your first time interacting with this bot or if you are unsure.)'

        return await utils.get_interaction(bot=bot, user=user, custom_id=custom_id, options=options, title=title)
    except:
        await utils.log_in_channel(bot, "Error during DM init with {0}".format(user.name))


async def get_ign_confirm(bot, user):
    try:
        q = await user.send('❕ __**What is your In Game Name?**__')

        reply = await bot.wait_for(
            "message",
            timeout=300,
            check=lambda m: m.author == user and m.channel.id == q.channel.id)
        ign = reply.content.strip()

        if not ign:
            await user.send('_Invalid Name._')
            return ign, utils.NO

        custom_id = uuid.uuid4().hex
        options = [utils.YES, utils.NO]
        title = '❔ __**Confirm your IGN as {0}?**__'.format(ign)

        return ign, await utils.get_interaction(bot=bot, user=user, custom_id=custom_id, options=options, title=title)
    except:
        await utils.log_in_channel(bot, "Error during IGN prompt with {0}".format(user.name))


async def get_role(bot, user):
    try:
        custom_id = uuid.uuid4().hex
        options = ['🛡️ Tank', '🗡️ Melee DPS', '🏹 Range DPS', '🧙 Mage', '💚 Healer']
        title = '⚔ __**What is your in game role?**__'

        return await utils.get_interaction(bot=bot, user=user, custom_id=custom_id, options=options, title=title)
    except:
        await utils.log_in_channel(bot, "Error during IGN prompt with {0}".format(user.name))


async def get_weapon(bot, user, string):
    try:
        custom_id = uuid.uuid4().hex
        options = ['Bow', 'Fire Staff', 'Great Axe', 'Hatchet', 'Ice Gauntlet', 'Life Staff', 'Musket', 'Rapier',
                   'Spear', 'Sword and Shield', 'Void Gauntlet', 'War Hammer']
        title = '🗡️ __**What is your ' + string + ' weapon?**__'

        return await utils.get_interaction(bot=bot, user=user, custom_id=custom_id, options=options, title=title)
    except:
        await utils.log_in_channel(bot, "Error during IGN prompt with {0}".format(user.name))


async def ask_gear_score(bot, user):
    try:
        q = await user.send('⚠ __**What is your Gear Score (integer, 0-600)?**__'
                            '\n_If you are not sure, make your best guess._')

        reply = await bot.wait_for(
            "message",
            timeout=300,
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
    except:
        await utils.log_in_channel(bot, "Error during IGN prompt with {0}".format(user.name))


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
            timeout=300,
            check=lambda m: m.author == user and m.channel.id == q.channel.id)
        return reply.content.strip()
    except:
        await utils.log_in_channel(bot, "Error during IGN prompt with {0}".format(user.name))


async def get_in_company(bot, user):
    try:
        custom_id = uuid.uuid4().hex
        options = [utils.YES, utils.NO]
        title = '🛡️ __**Are you in a company?**__'

        return await utils.get_interaction(bot=bot, user=user, custom_id=custom_id, options=options, title=title)
    except:
        await utils.log_in_channel(bot, "Error during IGN prompt with {0}".format(user.name))


async def send_dm(bot, user):
    try:
        is_returning_player = await init(bot, user)

        # TODO: New/Old Player
        ign = await get_ign(bot, user)
        in_company = await get_in_company(bot, user)
        if in_company == utils.YES:
            company = await get_company(bot, user)
        else:
            company = 'None'
        role = await get_role(bot, user)
        weapon_1, weapon_2 = await get_weapons(bot, user)
        gear_score = await get_gear_score(bot, user)

        await user.send("Thank you for completing the survey, make sure to sign up at the war board in game. 😊")

    except:
        await utils.log_in_channel(bot, "Error during DM with {0}".format(user.name))
