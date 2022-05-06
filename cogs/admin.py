# Deprecating the administration functionality. Not necessary at this time

import discord
from discord.ext import commands
import embeddable.embeds

class Admin(commands.Cog):
    _access_denied = "Access Denied - Please talk to an admin for access \n" \
                     "Type !admins for a list of users."

    e = embeddable.embeds

    def __init__(self, bot):
        self.bot = bot
        self.db = DataBase()

    """
    Add user to database
    """

    @commands.command(name="admins", brief="List of Admins")
    async def admins(self, ctx):
        names = "**Admins**"
        for i in self.db.admin_list():
            name = str(i).strip("(),")
            names += f"\n<@{name}>"
        await ctx.send(embed=self.e.base(f"Sent you the list via dm {ctx.author.mention}"))
        await ctx.author.send(embed=self.e.base(names))

    @commands.command(name="adduser", brief="Add a user to the admin group")
    async def adduser(self, ctx, member: discord.Member):
        # if not member:
        #     return await ctx.send("No user specified")
        if self.db.auth_check(ctx.message.author.id):
            if not self.db.member_insert(member.id):
                return await ctx.send(embed=self.e.warning(f"User {member.name} has already been added"))
            else:
                self.db.member_insert(member.id)
                return await ctx.send(embed=self.e.base(f"{member.name} has been added to the Admins"))
        else:
            return await ctx.send(embed=self.e.error(self._access_denied))

    @adduser.error
    async def adduser_error(self, ctx, error):
        if isinstance(error, commands.errors.MissingRequiredArgument):
            return await ctx.send(embed=self.e.warning("Missing required user name"))
        if isinstance(error, commands.errors.BadArgument):
            return await ctx.send(embed=self.e.warning("Please enter @user"))

    """
    Remove user from database
    """

    @commands.command(name="rmuser", brief="Remove user from Admins")
    async def rmuser(self, ctx, member: discord.Member):
        if member.id == 650496725554954261:
            return await ctx.send(embed=self.e.warning("Access denied - Can not remove owner"))
        if self.db.auth_check(ctx.message.author.id):
            if not self.db.member_delete(member.id):
                return await ctx.send(embed=self.e.error(f"User {member.name} not found in Admins"))
            else:
                self.db.member_delete(member.id)
                return await ctx.send(embed=self.e.base("{member.name} has been removed"))
        else:
            return await ctx.send(embed=self.e.error(self._access_denied))

    @rmuser.error
    async def rmuser_error(self, ctx, error):
        if isinstance(error, commands.errors.MissingRequiredArgument):
            return await ctx.send(embed=self.e.warning("Missing required user name"))
        if isinstance(error, commands.errors.BadArgument):
            return await ctx.send(embed=self.e.warning("Please enter @user"))
