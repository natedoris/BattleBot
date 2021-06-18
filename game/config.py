config = {
    "game-name": "Earl's Cabin",
    "nickname": "Earl",
    "game-file-path": "C:\\GOG Games\\Outlaws\\",
    "number-of-kills": 40,
    "maximum-players": 16
}

# Game mode default config D for Deathmatch
multiplayer_game_mode = "D"

# Game mode reference variable set to Deathmatch as default
mplayer_current_game_mode = "Deathmatch"
mplayer_game_mode = "Deathmatch"

# Dictionary lists for game modes - Data Read only
rcm_game_modifier = {
    "ctf": "C",
    "dm": "D",
    "tm": "M",
    "secret": "S",
    "tag": "T",
    "kfc": "K",
}
rcm_game_modifier_ref_table = {
    "ctf": "Capture the Flag",
    "dm": "Deathmatch",
    "tm": "Team match",
    "secret": "Secret Document",
    "tag": "Tag",
    "kfc": "Kill the Fool with the Chicken"
}

rcm_game_mode_from_file = {
    "C": "Capture the Flag",
    "D": "Deathmatch",
    "M": "Team match",
    "S": "Secret Document",
    "T": "Tag",
    "K": "Kill the Fool with the Chicken"
}
