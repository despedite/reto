![alt text](RetoCoverart.png)

# Rēto
Rēto is an upvote and downvote system akin to Reddit, for Discord! Any user can heart a message they particularly like (or crush a message they don't quite enjoy) by reacting to said message with a :plus: or :minus: to add or subtract to an user's Karma score. Not only that, but users with the "Curator" role have access to the :10: emoji, which will grant the message-poster 10 points towards their Karma, and send the message to a "#best-of" channel for all the world to see. This bot is perfect for personal and community channels that want to have an alternative scoring system to that of levelling up, and want to showcase how fun and interesting their community is!

![alt text](2019-06-2821-12-43_Trim.gif)

## Getting Started
You can add Rēto to your server [by clicking on this link!](https://discordapp.com/api/oauth2/authorize?client_id=591466921812164608&permissions=1342449744&scope=bot)
Afterwards, send the command **?setup** to get the bot ready for action. This will:

- create the role "Curators"
- add you to said role
- create the channel #best-of (you can move this to another category later)
- create a emoji exclusive to the role "Curators": the Star (:10:)
- create emojis available for everyone (Heart :plus: and Crush :minus:)

Make sure the bot has the appropiate permissions and that there's enough space for three new custom emoji in your server! After you're done, you can react to any message with any of the three supported emojis and Rēto will respond accordingly and update the karma of the commenter. You can check your karma with **?karma**, or check other people's karma with **?karma @{USER}**.


## Self-hosting Rēto
So, you've decided to self-host Rēto. Whether that's because you want to put Karma to good use by implementing other features to the bot or adapting it to your server's necessities, good on you! Here's what you'll need to set up Rēto on a machine of your very own.

### Dependencies
- [discord.py](https://github.com/Rapptz/discord.py): py -3 -m pip install -U discord.py
- [pyfiglet](https://github.com/pwaller/pyfiglet): pip install pyfiglet
- [TinyDB](https://github.com/msiemens/tinydb): pip install tinydb
- [aiofiles](https://github.com/Tinche/aiofiles): pip install aiofiles **(NEW)**


~~The next thing you'll need is a *MySQL database*.~~ Rēto doesn't use MySQL anymore, and the JSON database is created on first install. Hooray!

Go to https://discordapp.com/developers/applications/me and create an application for your bot. Create a bot account, copy the token and modify the bot token on the last line. Run reto.py and invite the bot using OAuth2! Rēto will need the following permissions: &permissions=1342449744.

Rēto was originally made for the [Discord Hack Week 2019](https://discord.gg/hackweek).
