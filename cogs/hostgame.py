# TODO: Clean up the print code - Set perhaps some logging instead
# TODO: Create settings such as amount of kills or time limit, etc...
#

import asyncio
import discord
from discord.ext import commands, tasks
from urllib import request, error
from game.config import config
from db.auth import DataBase
import os
import zipfile
import pyautogui
import keyboard
import pydirectinput
import subprocess
from win32gui import FindWindow, SetWindowPos, SetFocus, SetForegroundWindow
import win32con as win32con
from winreg import *
import time
import signal
import game.config as cfg
import game.status as bot_status
import embeddable.embeds
import game.config as cfg


class HostGame(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    memberauth = DataBase()

    PATH = config['game-file-path']
    GAMENAME = config['game-name']
    NICKNAME = config['nickname']

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
        with open("maps\\extract_list.txt", "r") as readfile:
            for i in readfile.readlines():
                try:
                    os.remove(self.PATH + i.strip("\n"))
                except FileNotFoundError as fe:
                    print(fe)

    # Outlaws reads the RCM file for map instructions. This modifies the RCM file so that only
    # the deathmatch option is available. In the future this will become a variable that will change
    # upon request for "CTF" or the like.
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

    # Starts the Outlaws olwin.exe with command line options. Currently only directplay is available
    # Will figure out Hamachi / Winsock in the future
    async def start_game(self):
        popen = subprocess.Popen
        outlaws = popen(f"C:\\GOG Games\\Outlaws\\olwin.exe /safe /nosound /host {self.NICKNAME} "
                        f"{self.GAMENAME}"
                        f" /netdriver LECDP3.DLL")
        self._PID = outlaws.pid
        await asyncio.sleep(1)
        # Create handle for window operations
        handle = FindWindow(None, "Outlaws")
        while handle is None:
            await asyncio.sleep(0.1)
            handle = FindWindow(None, "Outlaws")

        # Make sure the window is the top most
        # SetWindowPos(handle, win32con.HWND_TOPMOST, 0, 0, 0, 0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
        # SetForegroundWindow(handle)
        # Mouse click left hand corner as "SetWindowPos" not exactly working 100%
        time.sleep(1.0)
        pyautogui.click(50, 50, 1)
        time.sleep(0.5)
        keyboard.send('tab')
        time.sleep(0.1)
        keyboard.send('tab')
        time.sleep(0.1)
        keyboard.send('tab')
        time.sleep(0.1)
        keyboard.send('tab')
        time.sleep(0.1)
        keyboard.send('enter')
        time.sleep(2)
        keyboard.send('tab')
        time.sleep(0.1)
        keyboard.send('tab')
        time.sleep(0.1)
        keyboard.send('tab')
        time.sleep(0.1)
        keyboard.send('tab')
        time.sleep(0.1)
        keyboard.send('tab')
        time.sleep(0.1)
        keyboard.send('tab')
        time.sleep(0.1)
        keyboard.send('tab')
        time.sleep(0.1)
        keyboard.send('enter')
        time.sleep(3)
        pyautogui.screenshot('pictures\\screenshots\\lobby.png', region=(0, 0, 640, 500))
        keyboard.send('tab')
        time.sleep(0.1)
        keyboard.send('tab')
        time.sleep(0.1)
        keyboard.send('tab')
        time.sleep(0.1)
        keyboard.send('enter')
        time.sleep(0.5)
        keyboard.send('t')
        keyboard.send('t')

    # Useful to see if the game is currently running
    def game_status(self):
        if not FindWindow(None, "Outlaws"):
            return False
        else:
            return True

    # Here we "poll" the game every 5 seconds to see if the game has ended.
    @tasks.loop(seconds=5)
    async def check_game_status(self):
        try:
            game_over_btn = pyautogui.locateOnScreen('pictures\\gameover.png')
            if game_over_btn is not None:
                await bot_status.update(self.bot, "Outlaws", discord.Status.online)
                self.quit_game()
                self.check_game_status.cancel()
        except pyautogui.ImageNotFoundException as e:
            print(e)

    # If the game is hung up or the players want to change this has been included to terminate the game early
    def quit_game(self):
        os.kill(self._PID, signal.SIGTERM)
        self.check_game_status.cancel()  # Cancel the task in case someone exits early
        time.sleep(.5)
        if FindWindow(None, "Outlaws"):
            return False
        else:
            return True

    # When a user sets the number of kills we don't want it permanent. This is a default setting
    async def set_defaults_end_of_match(self):
        _path = r"SOFTWARE\Classes\VirtualStore\MACHINE\SOFTWARE\WOW6432Node\LucasArts Entertainment Company\Outlaws" \
                r"\Users\Default User\Multiplayer"
        with OpenKey(HKEY_CURRENT_USER, _path, 0, KEY_ALL_ACCESS) as key:
            SetValueEx(key, "Kills To End Game", 0, REG_SZ, "40")
        cfg.multiplayer_game_mode = "D"

    _mapname = ''
    _kills_limit = ''

    # Hosts the game. This is where a lot of the logic is tied into
    @commands.command(name="host", brief="Host an Outlaws match")
    async def host(self, ctx, *args):
        if self.game_status():
            await ctx.send(embed=self.e.warning("Game is already hosted"))
            return
        elif not args:
            await ctx.send(embed=self.e.error("Please specify a map - i.e. host players.com/map/map.zip"))
            return
        elif self.url_check(args[0]) is not True:
            await ctx.send(embed=self.e.error(f"*{args[0]}* is not a valid URL {ctx.author.mention}"))
            return
        else:
            await ctx.send(embed=self.e.warning("Checking map and game configuration..."))
            # Sets the _mapname variable for use in the "status" command
            self._mapname = args[0]

            # Sets the _kills_limit variable for use in the "status" command
            # Takes a snapshot of the registry value so in the event a user sets the kill limit during the game
            # the "status" command won't give false kill limit value
            _path = r"SOFTWARE\Classes\VirtualStore\MACHINE\SOFTWARE\WOW6432Node\LucasArts Entertainment " \
                    r"Company\Outlaws" \
                    r"\Users\Default User\Multiplayer"
            with OpenKey(HKEY_CURRENT_USER, _path) as key:
                self._kills_limit = QueryValueEx(key, "Kills To End Game")

            # Remove the previous map files
            #await ctx.send("Cleaning up previous session...")
            self.map_cleanup()

            # Download the new zip file map
            try:
                #await ctx.send("Downloading map...")
                self.download_map(args[0])
            except error as e:
                await ctx.send(embed=self.e.error(f"*Please check the URL. \nError code: {e}*\n"
                                                  f"{self.EXITING}"))

                # Extract the zip files
            try:
                self.extract_map(args[0])
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
                await ctx.send(embed=self.e.error("**Map configuration is not accepted**\n"
                                                  f"*Supported map modes for {self._mapname} are*\n**{modes}**\n"
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
            await ctx.send(embed=self.e.base(f"IP: 104.168.214.165\n{self._mapname}\n"
                                             f"Mode: {cfg.mplayer_current_game_mode}\n"
                                             f"Number of kills to end current session: {self._kills_limit[0]}"))

            await bot_status.update(self.bot, "Outlaws (HOSTING)", discord.Status.do_not_disturb)

            # Relax until the game has ended.
            # Operations "pause" here until game is complete.
            # Async in operation so this function will not hang other operations
            #await self.check_game_status.start()

            # Set the default amount of kills at the end of the game
            await self.set_defaults_end_of_match()

    @commands.command(name="term", brief="Terminate the current game")
    async def term(self, ctx):
        if self.memberauth.auth_check(ctx.message.author.id):
            if self.quit_game():
                await ctx.send(embed=self.e.base("Game terminated"))
                await bot_status.update(self.bot, "Outlaws", discord.Status.online)
                await self.set_defaults_end_of_match()
            else:
                await ctx.send(embed=self.e.error("Game did not terminate"))
        else:
            return await ctx.send(embed=self.e.error("Access denied - Please see an admin for access"))

    @commands.command(name="status", brief="Check if the game is hosted")
    async def status(self, ctx):
        if self.game_status():
            pyautogui.screenshot('pictures\\screenshots\\status.png', region=(440, 0, 200, 215))
            await ctx.send(file=discord.File(r'pictures\screenshots\status.png'))
            await ctx.send(embed=self.e.base(f"IP: 104.168.214.165\n{self._mapname}\n"
                                             f"Mode: {cfg.mplayer_current_game_mode}\n"
                                             f"Number of kills to end current session: {self._kills_limit[0]}"))
        else:
            return await ctx.send(embed=self.e.warning("Game is not hosted"))
