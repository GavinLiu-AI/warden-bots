from discord.ext import commands

import configs

bot = commands.Bot(command_prefix='.')


@bot.event
async def on_ready():
    print('Logged on as', bot.user)


@bot.command()
async def ping(ctx):
    await ctx.send('pong')


bot.run(configs.WAR_BOT_TOKEN)
