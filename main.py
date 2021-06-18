'''
TODO: Get the game to terminate when game is over automatically
TODO: Change the help section to read a little nicer
TODO: Update all ctx.sends to one message instead of multiple awaits
TODO: Add additional functionality, like findmap / etc.
'''

from discord import Status
from discord.ext import commands
from cogs.hostgame import HostGame
from cogs.admin import Admin
from cogs.gameconfig import ConfigGame
from cogs.poll import Poll
import game.status as bot_status

bot = commands.Bot(command_prefix="!")

TOKEN = ""  # Enter Discord Bot token here

bot.add_cog(HostGame(bot))
bot.add_cog(Admin(bot))
bot.add_cog(ConfigGame(bot))
bot.add_cog(Poll(bot))

@bot.event
async def on_ready():
    print("READY")
    await bot_status.update(self=bot,
                            name="Outlaws",
                            status=Status.online)

bot.run(TOKEN)
