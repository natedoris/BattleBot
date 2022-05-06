

import asyncio
import discord
import constants
from discord.ext import commands
from urllib import request, error
from game.config import config
import os
import zipfile
import pyautogui
import keyboard
import subprocess
from win32gui import FindWindow, SetWindowPos
import win32con as win32con
from winreg import *
import time
import signal
import game.config as cfg
import game.status as bot_status
import embeddable.embeds


class HostGame(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    PATH = config['game-file-path']
    GAMENAME = config['game-name']
    NICKNAME = config['nickname']

    game_network_conn = ''

    # Assigned in the "async def host" method
    network_conn = ''
    
    # Message embeds for fanciness
    e = embeddable.embeds

    EXITING = "**Application exiting...**"

    """
    Map Section Handling
    """
    
    def url_check(self, url):
        if url[0:4].lower() != "http":
            return False
        else:
            return True

    # Download the zip file map
    def download_map(self, map):
        with request.urlopen(map) as f:
            a = map.split("/")
            file = open(f"{self.PATH}{a[len(a) - 1]}", "wb")
            file.write(f.read())

    # 1 - Extract the zipped map to the Outlaws folder.
    # 2 - Write the contents of the zipped file to text file "extract_list"
    # so it can keep track of what to delete
    def extract_map(self, mapname):
        map = mapname.split("/")
        file = map[len(map) - 1]
        with zipfile.ZipFile(f"{self.PATH}{file}") as unzip:
            with open("maps\\extract_list.txt", "w") as elist:
                for i in unzip.namelist():
                    elist.write(f"{i}\n")
                elist.write(file)
            unzip.extractall(self.PATH)

    # Reads "extract_list" and removes the files prior to a new game starting
    def map_cleanup(self):
        with open(f"maps\\extract_list.txt", "r") as readfile:
            for i in readfile.readlines():
                try:
                    os.remove(self.PATH + i.strip("\n"))
                except FileNotFoundError as fe:
                    print(fe)

    # Outlaws reads the RCM file for map instructions. This method modifies the RCM file
    _modes = []
    def rcm_get_game_modes(self, file_data):
        for fdata in file_data:
            if fdata.startswith("MODE"):
                mode_data = fdata.split(":")
                s_mode = mode_data[1].strip()
                self._modes = list(s_mode)

    def rcm_read_file(self):
        with open("maps\\extract_list.txt", "r") as readfile:
            for i in readfile.readlines():
                if i.strip("\n").casefold().endswith(".rcm"):
                    rcm_file = open(self.PATH + i.strip("\n"), "r+")
                    self.rcm_get_game_modes(rcm_file)

    def rcm_check_mode(self, game_mode):
        for mode in self._modes:
            if game_mode == mode:
                return True

    def mod_rcm_file(self, game_mode):
        with open("maps\\extract_list.txt", "r") as readfile:
            for i in readfile.readlines():
                if i.strip("\n").casefold().endswith(".rcm"):

                    # Open the RCM data file
                    rcm_file = open(self.PATH + i.strip("\n"), "r+")
                    # Creating data string variable to pass contents of RCM into
                    data = ""
                    for text in rcm_file:
                        if text.startswith("MODE"):
                            text = text.replace(text, f"MODES:\t{game_mode}\n")
                        data += text
                    # Close the RCM File
                    rcm_file.close()

                    # Opening the RCM File in write mode
                    rcm_file = open(self.PATH + i.strip("\n"), "w")
                    # Overwrite the data in the RCM File
                    rcm_file.write(data)
                    rcm_file.close()
                    return True
            return False

    """
    Game Start Handling
    """

    _PID = ''

    # Starts a new Outlaws olwin.exe process with command line args.
    async def start_game(self):
        popen = subprocess.Popen
        outlaws = popen(f"C:\\GOG Games\\Outlaws\\olwin.exe /nosound /host {self.NICKNAME} " +
                        f"{self.GAMENAME}" +
                        f" /netdriver {self.game_network_conn}")
        self._PID = outlaws.pid
        await asyncio.sleep(1)
        # Create handle for window operations
        handle = FindWindow("LucasArtsOutlawsWClass", "Outlaws")
        while handle is None:
            await asyncio.sleep(0.1)
            handle = FindWindow("LucasArtsOutlawsWClass", "Outlaws")
        
        # Make sure the window is the top most
        SetWindowPos(handle, win32con.HWND_TOPMOST, 0, 0, 0, 0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
        
        # Left screen click on Outlaws to make sure window has focus
        pyautogui.click(50, 50, 1)
        # Start Game Window
        pyautogui.click(510, 470)
        # Multiplayer Options Window
        pyautogui.click(540, 475)
        time.sleep(1.5)
        pyautogui.screenshot('pictures\\screenshots\\lobby.png', region=(0, 0, 640, 500))
     
        # Enter Game
        pyautogui.click(420, 480)
        time.sleep(0.5)
        keyboard.send('t')
        keyboard.send('t')

    # Useful to see if the game is currently running
    def game_status(self):
        if not FindWindow("LucasArtsOutlawsWClass", "Outlaws"):
            return False
        else:
            return True

    # If the game is hung up or the players want to change this has been included to terminate the game early
    def quit_game(self):
        os.kill(self._PID, signal.SIGTERM)
        time.sleep(.5)
        if FindWindow("LucasArtsOutlawsWClass", "Outlaws"):
            return False
        else:
            return True

    # When a user sets the number of kills we don't want it permanent. This is a default setting
    async def set_defaults_end_of_match(self):
        with OpenKey(HKEY_CURRENT_USER, constants.REGISTRY_PATH, 0, KEY_ALL_ACCESS) as key:
            SetValueEx(key, "Kills To End Game", 0, REG_SZ, "40")
        cfg.multiplayer_game_mode = "D"

    _mapname = ''
    _kills_limit = ''

    #Hosts the game.
    #-Downloads the selected map file
    #-Modifies the RCM file as per game mode
    #-Launch olwin.exe using popen
    #-Navigate through the game menu's using pyautogui
    #-At lobby menu : Take screenshot, upload to discord, then enter the game
    #-Set bot status to hosting
    #-Set registry values back to defaults
    @commands.guild_only()
    @commands.command(name="host", brief="Host an Outlaws match")
    async def host(self, ctx, *args):
        # Confirm that game isn't already running
        if self.game_status():
            await ctx.send(embed=self.e.warning("Game is already hosted"))
            return

        if len(args) < 2:
            await ctx.send(embed=self.e.error(
                f"Usage: {constants.CMD_PREFIX}host wsock http://website.com/map.zip" +
                f"\nUsage: {constants.CMD_PREFIX}host dplay http://website.com/map.zip")
            )
            return
        
        self.network_conn = args[0]
        url = args[1]

        if (self.network_conn.lower() != "wsock") and (self.network_conn.lower() != "dplay"):
            await ctx.send(embed=self.e.error("Please specify Winsock (wsock) or DirectPlay (dplay)"))

        elif not url:
            await ctx.send(embed=self.e.error("Please specify a map - i.e. host players.com/map/map.zip"))
            return
        elif self.url_check(url) is not True:
            await ctx.send(embed=self.e.error(f"*{url}* is not a valid URL {ctx.author.mention}"))
            return
        else:
            await ctx.send(embed=self.e.warning("Checking map and game configuration..."))
            # Sets the _mapname variable for use in the "status" command
            self._mapname = url
            self.game_network_conn = cfg.GAME_CONN[self.network_conn]


            # Sets the _kills_limit variable for use in the "status" command
            # Takes a snapshot of the registry value so in the event a user sets the kill limit during the game
            # the "status" command won't give false kill limit value
            with OpenKey(HKEY_CURRENT_USER, constants.REGISTRY_PATH) as key:
                self._kills_limit = QueryValueEx(key, "Kills To End Game")

            # Remove the previous map files
            #await ctx.send("Cleaning up previous session...")
            self.map_cleanup()

            # Download the new zip file map
            try:
                #await ctx.send("Downloading map...")
                self.download_map(url)
            except error as e:
                await ctx.send(embed=self.e.error(f"*Please check the URL. \nError code: {e}*\n" +
                                                  f"{self.EXITING}"))

                # Extract the zip files
            try:
                self.extract_map(url)
                #await ctx.send(" Extracting map...")
            except zipfile.BadZipFile as bad_zip:
                await ctx.send(bad_zip)

            # Modify the RCM file for Deathmatch
            #await ctx.send("Checking map configuration...")
            self.rcm_read_file()

            if not self.rcm_check_mode(cfg.multiplayer_game_mode):
                modes = ''
                for mode in self._modes:
                    modes += f"{cfg.rcm_game_mode_from_file[mode]}, "
                await ctx.send(embed=self.e.error("**Map configuration is not accepted**\n" +
                                                  f"*Supported map modes for {self._mapname} are*\n**{modes}**\n" +
                                                  f"Application Exiting"))
                return


            if self.mod_rcm_file(cfg.multiplayer_game_mode):
                await ctx.send(embed=self.e.base("Configuration has passed! Game starting up..."))
            else:
                await ctx.send(embed=self.e.error("No multiplayer maps found"))
                return

            # Start the game
            await self.start_game()

            # Notify the users that the game has indeed started
            await ctx.send(file=discord.File(r'pictures\screenshots\lobby.png'))
            await ctx.send(embed=self.e.base(
                f"Network : **{cfg.GAME_CONN_CONV[self.network_conn]}**\n" +
                f"Address: **{cfg.GAME_URL[self.network_conn]}**\n" +
                f"{self._mapname}\n" +
                f"Mode: **{cfg.mplayer_current_game_mode}**\n" +
                f"Number of kills to end current session: **{self._kills_limit[0]}**"))

            await bot_status.update(self.bot, f"Outlaws (HOSTING {cfg.GAME_CONN_CONV[self.network_conn]})", discord.Status.do_not_disturb)

            # Relax until the game has ended.

            # Set the default amount of kills at the end of the game
            await self.set_defaults_end_of_match()

    @host.error
    async def host_error(self, ctx, error):
        if isinstance(error, commands.errors.NoPrivateMessage):
            await ctx.author.send(embed=self.e.error("Can not host game from private message"))

    @commands.guild_only()
    @commands.command(name="term", brief="Terminate the current game")
    async def term(self, ctx):
        # if self.memberauth.auth_check(ctx.message.author.id):
        if self.quit_game():
            await ctx.send(embed=self.e.base("Game terminated"))
            await bot_status.update(self.bot, "Outlaws", discord.Status.online)
            await self.set_defaults_end_of_match()
        else:
            await ctx.send(embed=self.e.error("Game did not terminate"))

    @term.error
    async def term_error(self, ctx, error):
        if isinstance(error, commands.errors.NoPrivateMessage):
            await ctx.author.send(embed=self.e.error("Can not terminate game from private message"))


    @commands.command(name="status", brief="Check if the game is hosted")
    async def status(self, ctx):
        if self.game_status():
            pyautogui.screenshot('pictures\\screenshots\\status.png', region=(440, 0, 200, 215))
            await ctx.send(file=discord.File(r'pictures\screenshots\status.png'))
            await ctx.send(embed=self.e.base(
                f"Network : **{cfg.GAME_CONN_CONV[self.network_conn]}**\n" +
                f"Address: **{cfg.GAME_URL[self.network_conn]}**\n" +
                f"{self._mapname}\n" +
                f"Mode: **{cfg.mplayer_current_game_mode}**\n" +
                f"Number of kills to end current session: **{self._kills_limit[0]}**"))
        else:
            return await ctx.send(embed=self.e.warning("Game is not hosted"))
