'''
Unable to use just 1 static address to read the lobby chat. Will revisit this another time
'''

import game.player
import win32gui
import win32process
from ctypes import *
# To open the process
import win32api


class PlayerStats:
    players = []  # Players list
    gamers = game.player
    decoded_memory = None

    async def get_handle(self, window_name):
        hwnd = win32gui.FindWindow(None, window_name)
        if hwnd is None:
            print(f"Did not find {hwnd}")
        else:
            return hwnd

    async def get_process_id(self, handle):
        pid = win32process.GetWindowThreadProcessId(handle)
        if pid is None:
            print(f"Did not find pid for {handle}")
        else:
            return pid[1]

    async def add_player(self, player_name):
        for player in self.players:
            if player_name == player:
                return
            else:
                self.players.append(self.gamers.Player(player_name))
                print(f"Added Player : {player}")

    #   Here we add the score for the player
    async def add_score(self, player_name, amount):
        for player in self.players:
            if player_name == player:
                player.add_score(1)

    #   Here we add the deaths for the player
    async def add_deaths(self, player_name, amount):
        for player in self.players:
            if player_name == player:
                player.deaths(1)

    #   Here we sift through the data to determine where to place the objects
    async def player_sort(self, data):
        parsed_data = data.split(' ')
        for i in parsed_data:
            print(f"{i} == x")
        if parsed_data[1] == "joined":
            await self.add_player(self.gamers.Player(parsed_data[0]))
        if parsed_data[1] == "killed" and parsed_data[2].contains("you"):
            await self.add_deaths(parsed_data[0])
        if parsed_data[1] == "killed" and parsed_data[2].contains("you") is not True:
            await self.add_score(parsed_data[0])

    async def main(self):
        print("1")
        open_process = win32api.OpenProcess(0x0010, 1, self.get_process_id(self.get_handle("Outlaws")))
        read_mem = win32process.ReadProcessMemory(open_process, 0x535236, 90)
        self.decoded_memory = read_mem.decode('utf-8')
        print("@")
        print(f"Decoded Mem {self.decoded_memory}")

        while 1 == 1:
            print("FUCK!!")
            await self.player_sort(self.decoded_memory)

    # def add_score(player_name):
    #     for player in players:
    #         if player_name == player:

    # def split_string(string_to_split):
    #     data = string_to_split.split(' ')
    #     if data[1] == 'killed':

    # open_process = win32api.OpenProcess(0x0010, 1, get_process_id(get_handle("Outlaws")))
    # read_mem = win32process.ReadProcessMemory(open_process, 0x535236, 90)
    # print(read_mem.decode('utf-8'))
    #
    # print(get_handle("Outlaws"))
    # print(get_process_id(get_handle("Outlaws")))

