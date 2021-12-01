from discord_components import Select, SelectOption
import datetime
from pytz import timezone

# Files

GOOGLE_KEY = 'google-key.json'
# GOOGLE_KEY = '/home/chrisliuengr/wardens-bots/google-key.json'

IMAGE_WAR = 'images/war.jpg'
# IMAGE_WAR = '/home/chrisliuengr/wardens-bots/images/war.jpg'
IMAGE_INVASION = 'images/invasion.jpg'
# IMAGE_INVASION = '/home/chrisliuengr/wardens-bots/images/invasion.jpg'


# Google Spreadsheet
SPREADSHEET_WAR_ID = '1Pq5NkCikB5f1dXmWlLQ8nXYiZZTFcrEJggy7OJ3DkoQ'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
TAB_DATA = 'data'
TAB_WARSIGNUP = 'warsignup'

SPREADSHEET_GAME_POLL_ID = '1gUou0_yJqARkcsXPsXAfEk7ahghlDOZyjQyFfHF931M'
TAB_GAMES = 'games'

# Discord
X_ID = 120341906818334721

ANNOUNCEMENTS_CHANNEL_ID = 870222133115117568
BOT_COMMANDS_CHANNEL_ID = 909256529788682302
GENERAL_CHANNEL_ID = 870297428899803246
WAR_SIGNUP_CHANNEL_ID = 911441115197083719
EVENT_CHANNEL_ID = 891540447166595102

ADMIN_ROLES = ['Moderator', 'War-Lead', 'Master Warden', 'Grand Master Warden', 'Squad Lead', 'Wardens of the Hunt']

# Selections
YES = 'Yes'
NO = 'No'

YES_EMOJI = '✅'
MAYBE_EMOJI = '❔'
NO_EMOJI = '❌'
GAME_EMOJI = '🕹'
FIRE_EMOJI = '🔥'

OPTIONS_YES_NO = [YES, NO]

OPTION_UPDATE_IGN = 'In Game Name'
OPTION_UPDATE_COMP = 'Company'
OPTION_UPDATE_ROLE = 'Role'
OPTION_UPDATE_WEAPON = 'Weapons'
OPTION_UPDATE_GS = 'Gear Score'
OPTION_DONE = 'Done'
OPTIONS_UPDATES = [OPTION_UPDATE_IGN, OPTION_UPDATE_COMP, OPTION_UPDATE_ROLE, OPTION_UPDATE_WEAPON, OPTION_UPDATE_GS,
                   OPTION_DONE]

OPTIONS_WARDEN_COMPANIES = ['Wardens of the Hunt', 'Wardens Rising']

OPTIONS_ZONES = ['Brightwood', 'Cutlass Keys', 'Ebonscale_Reach', 'Everfall', 'First_Light', 'Monarch\'s_Bluffs',
                 'Mourningdale', 'Reekwater', 'Restless_Shore', 'Weaver\'s_Fen', 'Windsward']
OPTIONS_WAR = ['Offense', 'Defense', 'Invasion']
OPTIONS_ROLES = ['🛡️ Tank', '🗡️ Melee DPS', '🏹 Range DPS', '🧙 Mage', '💚 Healer']
OPTIONS_WEAPONS = ['Bow', 'Fire Staff', 'Great Axe', 'Hatchet', 'Ice Gauntlet', 'Life Staff', 'Musket', 'Rapier',
                   'Spear', 'Sword and Shield', 'Void Gauntlet', 'War Hammer']
OPTIONS_TIME = ['4PM', '4:30PM', '5PM', '5:30PM', '6PM', '6:30PM', '7PM', '7:30PM', '8PM', '8:30PM', '9PM', '9:30PM',
                '10PM', '10:30PM', '11PM']

# Labels
WAR_SIGNUP_LABEL = '**War/Invasion Sign up: '
GAME_POLL_LABEL = 'Game Poll'

# Messages
DM_SURVEY_INTRO_MESSAGE = 'Hello! 👋 You have indicated that you might be attending war/invasion.' \
                          '\n\n**Please complete the following questions to be considered in our roster.**' \
                          '\n_(It will expire after 10 minutes)_'
DM_SURVEY_RETURNING_PLAYER_MESSAGE = 'We have your information in the database!'
DM_SURVEY_UPDATE_PROMPT = '\n\n__**Would you like to update anything today?**__'
GAME_POLL_MESSAGE = 'What other games besides New World would you be interested in playing with us this week?' \
                    '\nLet us know and we will play the most voted game together at a scheduled time.'


async def send_interation_message(interaction):
    await interaction.send(content=f"{interaction.values[0]} selected")


async def set_selections(ctx, title, options, custom_id, placeholder=''):
    await ctx.send(
        title,
        components=[
            Select(
                placeholder=placeholder,
                options=[SelectOption(label=option, value=option) for option in options],
                custom_id=custom_id,
            )
        ],
    )


async def wait_for_input(bot, custom_id, timeout=600):
    return await bot.wait_for("select_option", check=lambda inter: inter.custom_id == custom_id, timeout=timeout)


async def log_in_channel(bot, message, channel_id=BOT_COMMANDS_CHANNEL_ID):
    channel = bot.get_channel(channel_id)
    await channel.send(message)


async def unauthorized(ctx):
    await ctx.send('Unauthorized for this command.')


async def is_admin(ctx):
    if not (set([role.name for role in ctx.author.roles]).intersection(set(ADMIN_ROLES)) or ctx.author.id == X_ID):
        await unauthorized(ctx)
        return False

    return True


async def is_dev(ctx):
    if not ctx.author.id == X_ID:
        await unauthorized(ctx)
        return False

    return True


async def add_emojis(msg, emojis):
    for emoji in emojis:
        await msg.add_reaction(emoji)


async def remove_other_reactions(bot, payload, message, emoji_name):
    # Remove all other reactions in the message by this user
    for reaction in message.reactions:
        if reaction.emoji != emoji_name:
            users = await reaction.users().flatten()
            for user in users:
                if user.id == payload.user_id:
                    await message.remove_reaction(reaction.emoji, user)


def get_online_msg(bot):
    return '{0} is online'.format(bot.user.name)


def get_deactivation_msg(bot):
    return '{0} is online but deactivated. Type ".activate" command for activation.'.format(bot.user.name)


async def get_interaction(bot, user, custom_id, options, title):
    await set_selections(user, title=title, options=options, custom_id=custom_id)
    interaction = await wait_for_input(bot, custom_id)
    await send_interation_message(interaction)

    return interaction.values[0]


def get_today_date():
    return datetime.datetime.now(timezone('US/Pacific')).date()


def format_error_msg(user, e):
    return '{0}: {1}'.format(user, e)


def message_in_embeds(message, embeds):
    if not embeds:
        return False

    embeds_list = [embed.title for embed in embeds]
    for embed in embeds_list:
        if message in embed:
            return True

    return False
