'''
TODO: Get the game to terminate when game is over automatically
TODO: Change the help section to read a little nicer
TODO: Update all ctx.sends to one message instead of multiple awaits
TODO: Add additional functionality, like findmap / etc.
'''

from discord import Status
from discord.ext import commands
from cogs.hostgame import HostGame
from cogs.gameconfig import ConfigGame
import game.status as bot_status
import constants
import embeddable.embeds

bot = commands.Bot(command_prefix=f"{constants.CMD_PREFIX}")

TOKEN = ''

bot.add_cog(HostGame(bot))
bot.add_cog(ConfigGame(bot))

@bot.event
async def on_ready():
    print("READY")
    await bot_status.update(self=bot,
                            name="Outlaws",
                            status=Status.online)

@bot.event
async def on_command_error(error, ctx):
    if isinstance(error, commands.CommandNotFound):
        await bot.send_message(ctx.message(embed=embeddable.embeds.error("Unknown command")))


bot.run(TOKEN)
