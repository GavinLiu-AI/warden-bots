from discord_components import Select, SelectOption

X_ID = 120341906818334721

ANNOUNCEMENTS_CHANNEL_ID = 870222133115117568
BOT_COMMANDS_CHANNEL_ID = 909256529788682302
GENERAL_CHANNEL_ID = 870297428899803246

ROLE_SELECT_MESSAGE_ID_PATH = 'temp/role-select-message-id'

IMAGE_WAR = 'images/war.jpg'
IMAGE_INVASION = 'images/invasion.jpg'

YES_EMOJI = '✅'
MAYBE_EMOJI = '❔'
NO_EMOJI = '❌'

ADMIN_ROLES = ['Moderator', 'War-Lead', 'Master Warden', 'Grand Master Warden', 'Squad Lead', 'Wardens of the Hunt']


WAR_SIGNUP_LABEL_MESSAGE = '**War/Invasion Sign up: '
DM_INTRODUCTION_LABEL_MESSAGE = '\n\n**Are you already in our database?**'


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


async def wait_for_input(bot, custom_id):
    return await bot.wait_for("select_option", check=lambda inter: inter.custom_id == custom_id, timeout=60)


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
