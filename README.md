# BattleBot
 A Discord Bot written in Python that automates multiplayer hosting for the game known as Outlaws created by LucasArts.
 
 # Uses
 Used for automating the following tasks,
 -Launching the game into multiplayer mode
 -Downloading an archived user made "map" (pass the bot a URL with the archive), extracting its contents to the game folder, modifying the map mode inside the file
 -Starts the game and sends a screenshot of completion to the specific Discord channel
 -After players complete session they initiate a command to terminate
 -Included a small SQLite database for "admin" users. This functions as a way to prevent unwanted terminations of the game. Everyone can host a match but only trusted people can terminate the match. (This feature to be removed in the future as most people that play this game are not malicious)
 
 # Disclaimer
 This is a work in progress and a way for me to learn Python and Git. Not all .py files are in use. There are certain functions I have included that do not work (such as the function to search the screen for the game ending text. I left it in to test but it fails as the pixel colors change depending on the map)
