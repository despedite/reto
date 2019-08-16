import discord
from discord.ext import commands
import asyncio
from tinydb import TinyDB, Query, where
from tinydb.operations import add, subtract
import aiohttp        
import aiofiles
import os.path
import os
import json
import datetime

db = TinyDB('db.json') #Database file: stores points of every user.
cfg = TinyDB("config.json") #Config file: stores configurations for the bot. Modify at your heart's content!
srv = TinyDB('server.json') #Server-specific configuration - allows you to modify stuff like the name of the reactions, for example.
table = db.table('_default', cache_size=None, smart_cache=True)

config = cfg.search(Query()['search'] == 'value')
for c in config:
	bottoken = c['bottoken']
	botname = c['botname']
	devname = c['devname']
	botver = c['botver']
	prefix = c['prefix']

class Karma(commands.Cog):
	def __init__(self, client):
		self.client = client
	
	# -------------------------
	#	      ?KARMA
	# -------------------------

	@commands.command(aliases=['points', 'point'], description="Check the accumulated amount of points (Karma) a given user has. Ping to check another user's karma account.")
	async def karma(self, ctx, *args):
		"""Check your karma! (or karma of other people by @mention-ing them)."""
		if not args:
			valor = str(ctx.message.author)
			searchvalor = str(ctx.message.author.id)

			result = db.get(Query()['username'] == searchvalor)
			
			send = await ctx.send("The user **{}** has a total of **{}** points.".format(ctx.message.author.name,result.get('points')))
		elif not ctx.message.mentions:
			await ctx.send("Invalid command! Do **?karma** to find out about your score, or @mention another user to get their score.")
		else:
			try:
				valor = str(ctx.message.mentions[0].name)
				searchvalor = str(ctx.message.mentions[0].id)
				
				resultmention = db.get(Query()['username'] == searchvalor)
				resultprint = resultmention.get('points')
					
				send = await ctx.send("The user **{}** has a total of **{}** points.".format(valor,resultprint))
			except:
				valor = str(ctx.message.mentions[0].name)
				send = await ctx.send("The user **{}** doesn't appear to have any points. Odd.".format(valor))
	
	# -------------------------------
	#	    ?GLOBALLEADERBOARD
	# -------------------------------
	
	@commands.command(aliases=['glb'], description="Check the top 10 users of Discord! May take a while to load.\nYour username/score isn't showing up on the leaderboards? Update 1.2.1 made it so servers you're in and your score are joined together. This will refresh the next time someone hearts/crushs/stars one of your comments.")
	async def globalleaderboard(self, ctx, *args):
		"""Check the top karma holders on all Discord!"""
		result = db.all() # "Result" is just the entire database.
		leaderboard = {} # Prepares an empty dictionary.
		for x in result: # For each entry in the database:
			leaderboard[x.get("username")] = int(x.get("points")) # ...save the user's ID and its amount of points in a new Python database.
		leaderboard = sorted(leaderboard.items(), key = lambda x : x[1], reverse=True) # Sort this database by amount of points.
		s = ""
		i = 0
		for key, value in leaderboard: # For each value in the new, sorted DB:
			if i != 10:
				user = await self.client.fetch_user(key)
				if i==0:
					s += ("🥇 " + str(user) + " - " + str(value) +" Karma\n")
				elif i==1:
					s += ("🥈 " + str(user) + " - " + str(value) +" Karma\n")
				elif i==2:
					s += ("🥉 " + str(user) + " - " + str(value) +" Karma\n")
				else:
					s += ("✨ " + str(user) + " - " + str(value) +" Karma\n")
				i = i+1
		embed = discord.Embed(title="Global Leaderboard", colour=discord.Colour(0xa353a9), description=s, timestamp=datetime.datetime.utcfromtimestamp(1565153513))
		embed.set_footer(text="Your score not appearing? ?help glb", icon_url=self.client.user.avatar_url)
		glb = await ctx.send(embed=embed)

	# --------------------------
	#	    ?LEADERBOARD
	# --------------------------
	
	@commands.command(aliases=['lb'], description="Check the top 10 users of your server! May take a while to load.\nYour username/score isn't showing up on the leaderboards? Update 1.2.1 made it so servers you're in and your score are joined together. This will refresh the next time someone hearts/crushs/stars one of your comments.")
	async def leaderboard(self, ctx, *args):
		"""Check this server's users with the most karma."""
		db.clear_cache()
		User = Query()
		server = str(ctx.message.guild.id)
		result = db.search(User.servers.all([server])) # doesnt work
		print("server: " + str(server) + " result: " + str(result))
		leaderboard = {} # Prepares an empty dictionary.
		for x in result: # For each entry in the database:
			leaderboard[x.get("username")] = int(x.get("points")) # ...save the user's ID and its amount of points in a new Python database.
		leaderboard = sorted(leaderboard.items(), key = lambda x : x[1], reverse=True) # Sort this database by amount of points.
		s = ""
		i = 0
		for key, value in leaderboard: # For each value in the new, sorted DB:
			if i != 10:
				user = await self.client.fetch_user(key)
				if i==0:
					s += ("🥇 " + str(user) + " - " + str(value) +" Karma\n")
				elif i==1:
					s += ("🥈 " + str(user) + " - " + str(value) +" Karma\n")
				elif i==2:
					s += ("🥉 " + str(user) + " - " + str(value) +" Karma\n")
				else:
					s += ("✨ " + str(user) + " - " + str(value) +" Karma\n")
				i = i+1
		embed = discord.Embed(title="Server Leaderboard", colour=discord.Colour(0xa353a9), description=s, timestamp=datetime.datetime.utcfromtimestamp(1565153513))
		embed.set_footer(text="Your score not appearing? ?help lb", icon_url=self.client.user.avatar_url)
		glb = await ctx.send(embed=embed)
def setup(client):
	client.add_cog(Karma(client))
