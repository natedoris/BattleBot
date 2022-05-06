from discord.ext import commands
from winreg import *
import game.config as cfg
import embeddable.embeds
import constants


class ConfigGame(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    e = embeddable.embeds
    '''
        Configuration 
    '''

    hostgame_match_modes = ''

    def set_registry(self, key_to_change, value):
        with OpenKey(HKEY_CURRENT_USER, constants.REGISTRY_PATH, 0, KEY_ALL_ACCESS) as key:
            SetValueEx(key, key_to_change, 0, REG_SZ, str(value))

    def get_registry(self, key_to_retrieve):
        with OpenKey(HKEY_CURRENT_USER, constants.REGISTRY_PATH) as key:
            query = QueryValueEx(key, key_to_retrieve)
            return query

    # Retrieve registry value info for multiplayer config
    @commands.command(name="config", brief="See default configuration")
    async def config(self, ctx):
        with OpenKey(HKEY_CURRENT_USER, constants.REGISTRY_PATH) as key:
            end_after_number_of_kills = QueryValueEx(key, "Kills To End Game")
            max_players = QueryValueEx(key, "Maximum Players")

            await ctx.send(embed=self.e.base(f"Number of kills to end game: {end_after_number_of_kills[0]}\n" +
                           f"Maximum players: {max_players[0]}"))

    # Set registry value "number of kills"
    @commands.command(name="kills", brief="Set number of kills")
    async def kills(self, ctx, args):
        args = int(args)
        if not args or args > 200:
            await ctx.send(embed=self.e.warning("`Please enter a number of kills between 1 and 200`"))
        else:
            self.set_registry("Kills To End Game", args)
            await ctx.send(embed=self.e.base(f"Kills changed to {self.get_registry('Kills To End Game')[0]}"))

    # Set registry value "maximum players"
    @commands.command(name="players", brief="Set number of max players")
    async def players(self, ctx, args):
        args = int(args)
        if not args or args > 20:
            await ctx.send(embed=self.e.warning("`Please enter a number of players between 6 and 20`"))
        else:
            with OpenKey(HKEY_CURRENT_USER, constants.REGISTRY_PATH, 0, KEY_ALL_ACCESS) as key:
                SetValueEx(key, "Maximum Players", 0, REG_SZ, str(args))
                end = QueryValueEx(key, "Maximum Players")
                await ctx.send(embed=self.e.base(f"`Maximum Players set to {end[0]}`"))

    # Set mode, CTF DM etc
    @commands.command(name="mode", brief="Set game mode. Resets to DM after match is over. eg. !mode ctf")
    async def mode(self, ctx, modes, *limit):
        mode = modes.strip().lower()
        if mode in cfg.rcm_game_modifier:
            cfg.multiplayer_game_mode = cfg.rcm_game_modifier[mode]
            cfg.mplayer_current_game_mode = cfg.rcm_game_modifier_ref_table[mode]

            await ctx.send(embed=self.e.base(
                f"`Setting mode to {cfg.mplayer_current_game_mode}. (Map must have {cfg.mplayer_current_game_mode} " +
                f"enabled)`"))
        else:
            dict_to_string = ''
            for key in cfg.rcm_game_modifier_ref_table.items():
                dict_to_string += f"\n{key}"
                dict_to_string = dict_to_string.replace("'", "")
                dict_to_string = dict_to_string.replace(",", " :")
            await ctx.send(embed=self.e.error(f"Unable to find game mode.\nGame modes are {dict_to_string}"))

    @mode.error
    async def mode_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(embed=self.e.error(f"Game modes are *ctf, dm, tm, secret, tag, kfc*\n" +
                                              f"Usage: !mode ctf"))
                                              