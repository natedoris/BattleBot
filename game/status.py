import discord


# Command to update the bot's status when game is initiated and destroyed
async def update(self, name, status):
    activity = discord.Activity()
    activity.type = discord.ActivityType.playing
    activity.name = name
    await self.change_presence(activity=activity,
                               status=status)
