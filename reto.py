import discord
from discord.ext import commands
import asyncio
import pyfiglet
from tinydb import TinyDB, Query, where
from tinydb.operations import add, subtract
import aiohttp        
import aiofiles
import os.path
import os
import json
import random
import dbl

db = TinyDB('json/db.json') #Database file: stores points of every user.
cfg = TinyDB("json/config.json") #Config file: stores configurations for the bot. Modify at your heart's content!
srv = TinyDB('json/server.json') #Server-specific configuration - allows you to modify stuff like the name of the reactions, for example.
activity = TinyDB('json/activity.json') #Activity file: the "Playing" commands the bot has.
customprefix = TinyDB('json/prefix.json') #Prefix file: custom prefixes per server.

for c in cfg:
	bottoken = c['bottoken']
	botname = c['botname']
	support = c['support']
	botver = c['botver']
	prefix = c['prefix']

getactivities = activity.all()
botactivity = []
i = 0
for value in getactivities:
	botactivity.append(getactivities[i]["activity"])
	i += 1	

def get_prefix(bot, msg):
	customprefix.clear_cache()
	if not msg.guild: # is on DMs
		return commands.when_mentioned_or(prefix)(bot,msg)
	else:
		pre = customprefix.search(Query().server == msg.guild.id)
		if pre:
			return pre[0]["prefix"] # custom prefix on json db
		else:
			return prefix # default prefix

bot = commands.Bot(command_prefix=get_prefix)
client = discord.Client()
ascii_banner = pyfiglet.figlet_format(botname + ".py")

@bot.command
async def load(ctx, extension):
	bot.load_extension(f'cogs.{extension}')

@bot.command
async def unload(ctx, extension):
	bot.unload_extension(f'cogs.{extension}')

for file in os.listdir("./cogs"):
	if file.endswith(".py"):
		bot.load_extension(f'cogs.{file[:-3]}') #[:-3] removes the last 3 chars

@bot.event
async def on_ready():
	print (ascii_banner)
	print (botname + " is ONLINE!")
	if len(bot.guilds) == 1:
		print ("Running with the name " + str(bot.user) + " on " + str(len(bot.guilds)) + " server")
	else:
		print ("Running with the name " + str(bot.user) + " on " + str(len(bot.guilds)) + " servers")
	print ("Invite link: https://discordapp.com/api/oauth2/authorize?client_id=" + str(bot.user.id) + "&permissions=1342449744&scope=bot")
	print ("Ver " + botver + " - check the updates with ?changelog")
	print ("?setup to get started!")
	print ("--------------------------------------------")

	if botver != "":
		game = discord.Game(botactivity[random.randrange(len(botactivity))] + " | v" + botver)
	else:
		game = discord.Game(botactivity)
	await bot.change_presence(activity=game)
	bot.loop.create_task(statusupdates())

@bot.event
async def on_guild_join(guild):
	srv.insert({'serverid': guild.id, 'heart': 'plus', 'crush': 'minus', 'star': '10'})
	for channel in guild.text_channels:
		if channel.permissions_for(guild.me).send_messages:
			embed=discord.Embed(title="Thank you for inviting Reto!", description="Try using the ?setup command to get started!\nIf any problems arise, [join our Discord server](https://google.com) so we can give you a hand.")
			embed.set_thumbnail(url="https://i.ibb.co/ySfQhDG/reto.png")
			await channel.send(embed=embed)
		break

async def statusupdates():
	while True:
		await asyncio.sleep(30)

		# update the activity list
		activity.clear_cache()
		getactivities = activity.all()
		i = 0
		botactivity = []
		for value in getactivities:
			botactivity.append(getactivities[i]["activity"])
			i += 1

		if botver != "":
			game = discord.Game(botactivity[random.randrange(len(botactivity))] + " | v" + botver)
		else:
			game = discord.Game(botactivity)
		await bot.change_presence(activity=game)	

bot.run(bottoken)
