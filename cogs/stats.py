import asyncio
from discord.ext import commands
from game.player_stats import PlayerStats


class Stats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    playerstats = PlayerStats

    @commands.command(name="stats")
    async def stats(self, ctx):
        print("Initiated")
        await self.playerstats.main(self=self.self)
