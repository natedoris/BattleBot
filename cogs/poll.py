# TODO set up poll
# m = re.split('(?<=[?|.] )', s
from discord.ext import commands
import re

class Poll(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    poll_counter = [[]]

    # Splitting tuple and using a regex to seperate out the '?' and '.'
    def split_args(self, args):
        conv_to_str = str(' '.join(args))
        print(conv_to_str)
        poll_questions = re.split('(?<=[?|.] )', conv_to_str)
        print(f"poll questions {poll_questions}")
        return poll_questions

    def print_tuple(self, args):
        data = ''
        for arg in args:
            data += f"{arg}\n"
        return data



    @commands.command(name="poll")
    async def poll(self, ctx, *poll_resp):
        # Create poll data here
        # poll_data = ' '.join(poll_resp)
        pdata = self.split_args(poll_resp)
        #self.print_tuple(pdata)
        await ctx.send(self.print_tuple(pdata))
        #await ctx.send(self.split_args(args))