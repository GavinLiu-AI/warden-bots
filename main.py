from discord_components import Button, ComponentsBot
from selections import war_selection

import configs

bot = ComponentsBot('.')


@bot.event
async def on_ready():
    print('Logged on as', bot.user)


@bot.command()
async def button(ctx):
    await ctx.send("Buttons!", components=[Button(label="Button", custom_id="button1")])
    interaction = await bot.wait_for(
        "button_click", check=lambda inter: inter.custom_id == "button1"
    )
    await interaction.send(content="Button Clicked")


@bot.command()
async def war(ctx):
    zone, offense, date, time = await war_selection.start(ctx, bot)
    await war_selection.confirmation(ctx, bot, zone, offense, date, time)


bot.run(configs.WAR_BOT_TOKEN)
