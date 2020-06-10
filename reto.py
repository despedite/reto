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

db = TinyDB('db.json') #Database file: stores points of every user.
cfg = TinyDB("config.json") #Config file: stores configurations for the bot. Modify at your heart's content!
srv = TinyDB('server.json') #Server-specific configuration - allows you to modify stuff like the name of the reactions, for example.

for c in cfg:
	bottoken = c['bottoken']
	botname = c['botname']
	devname = c['devname']
	botver = c['botver']
	prefix = c['prefix']
	botactivity = c['activity']

bot = commands.Bot(command_prefix=prefix, connector=aiohttp.TCPConnector(ssl=False))
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
	#NICE
	srv.insert({'serverid': guild.id, 'heart': 'plus', 'crush': 'minus', 'star': '10'})

async def statusupdates():
	while True:
		await asyncio.sleep(30)
		if botver != "":
			game = discord.Game(botactivity[random.randrange(len(botactivity))] + " | v" + botver)
		else:
			game = discord.Game(botactivity)
		await bot.change_presence(activity=game)

bot.run(bottoken)
