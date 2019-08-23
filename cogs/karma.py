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
post = TinyDB('comments.json') #Comment leaderboard.
priv = TinyDB('blacklist.json') #Privacy Mode blacklist. Users with PM on will not have their messages logged in the comment leaderboard.

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
		
	# ---------------------------------
	#	    ?GPLB (GLOBAL POST LB)
	# ---------------------------------
	
	@commands.command(aliases=['gplb', 'globalpostleaderboards'], description="Check the top 10 posts of all time on every server! May take a while to load.")
	async def globalpostleaderboard(self, ctx, *args):
		"""Check the toppest posts on every guild!"""
		result = post.all() # "Result" is just the entire database.
		leaderboard = {} # Prepares an empty dictionary.
		j = 0
		for x in result: # For each entry in the database:
			leaderboard[j] = [int(x.get("points")), str(x.get("content")), str(x.get("username")), str(x.get("embed")), str(x.get("servers"))] # ...save the user's ID and its amount of points in a new Python database.
			j = j+1
		
		leaderboard = sorted(leaderboard.items(), key = lambda x : x[1][0], reverse=True)
		print(leaderboard)
		
		numero = 1
		emoji = discord.utils.get(ctx.message.guild.emojis, name="plus")
		
		for key,values in leaderboard:
			if numero != 11:
				username = await self.client.fetch_user(values[2])
				guild = await self.client.fetch_guild(values[4])
				contenido=values[1]
				autor=username
				foto=username.avatar_url
				if(len(values[3]) > 0):
					imagen=values[3]
				if numero == 1:
					emberino=discord.Embed(description=contenido, colour=discord.Colour(0xffd700))
				elif numero == 2:
					emberino=discord.Embed(description=contenido, colour=discord.Colour(0xc0c0c0))
				elif numero == 3:
					emberino=discord.Embed(description=contenido, colour=discord.Colour(0xcd7f32))
				else:
					emberino=discord.Embed(description=contenido, colour=discord.Colour(0xa353a9))
				emberino.set_author(name=autor
				, icon_url=foto)
				emberino.set_footer(text=guild, icon_url=guild.icon_url)
				emberino.add_field(name="Karma", value=f"{emoji} " + str(values[0]), inline=True)
				if numero == 1:
					emberino.add_field(name="Position", value="🥇 "+str(numero), inline=True)
				elif numero == 2:
					emberino.add_field(name="Position", value="🥈 "+str(numero), inline=True)
				elif numero == 3:
					emberino.add_field(name="Position", value="🥉 "+str(numero), inline=True)
				else:
					emberino.add_field(name="Position", value="✨ "+str(numero), inline=True)
				if(len(values[3]) > 0):
					emberino.set_image(url=values[3])
				await ctx.send(embed=emberino)
				numero = numero + 1

	# ---------------------------------
	#	    ?PLB (SERVER POST LB)
	# ---------------------------------
	
	@commands.command(aliases=['splb', 'plb', 'serverpostleaderboard', 'postleaderboards', 'serverpostleaderboards'], description="Check the top 10 posts of all time on this server! May take a while to load.")
	async def postleaderboard(self, ctx, *args):
		"""Shows posts with most karma on this server!"""
		currentguild = str(ctx.message.guild.id)
		result = post.search(Query()['servers'] == currentguild) # "Result" is just the entire database.
		leaderboard = {} # Prepares an empty dictionary.
		j = 0
		for x in result: # For each entry in the database:
			leaderboard[j] = [int(x.get("points")), str(x.get("content")), str(x.get("username")), str(x.get("embed")), str(x.get("servers"))] # ...save the user's ID and its amount of points in a new Python database.
			j = j+1
		
		leaderboard = sorted(leaderboard.items(), key = lambda x : x[1][0], reverse=True)
		print(leaderboard)
		
		numero = 1
		emoji = discord.utils.get(ctx.message.guild.emojis, name="plus")
		guild = ctx.message.guild #Optimization!
		
		for key,values in leaderboard:
			if numero != 11:
				username = await self.client.fetch_user(values[2])
				contenido=values[1]
				autor=username
				foto=username.avatar_url
				if(len(values[3]) > 0):
					imagen=values[3]
				if numero == 1:
					emberino=discord.Embed(description=contenido, colour=discord.Colour(0xffd700))
				elif numero == 2:
					emberino=discord.Embed(description=contenido, colour=discord.Colour(0xc0c0c0))
				elif numero == 3:
					emberino=discord.Embed(description=contenido, colour=discord.Colour(0xcd7f32))
				else:
					emberino=discord.Embed(description=contenido, colour=discord.Colour(0xa353a9))
				emberino.set_author(name=autor
				, icon_url=foto)
				emberino.set_footer(text=guild, icon_url=guild.icon_url)
				emberino.add_field(name="Karma", value=f"{emoji} " + str(values[0]), inline=True)
				if numero == 1:
					emberino.add_field(name="Position", value="🥇 "+str(numero), inline=True)
				elif numero == 2:
					emberino.add_field(name="Position", value="🥈 "+str(numero), inline=True)
				elif numero == 3:
					emberino.add_field(name="Position", value="🥉 "+str(numero), inline=True)
				else:
					emberino.add_field(name="Position", value="✨ "+str(numero), inline=True)
				if(len(values[3]) > 0):
					emberino.set_image(url=values[3])
				await ctx.send(embed=emberino)
				numero = numero + 1

def setup(client):
	client.add_cog(Karma(client))
