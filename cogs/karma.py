import discord
from discord.ext import commands
import asyncio
from tinydb import TinyDB, Query, where
from tinydb.operations import add, subtract
import aiohttp        
import aiofiles
import os.path
import os

db = TinyDB('db.json') #Database file: stores points of every user.
cfg = TinyDB("config.json") #Config file: stores configurations for the bot. Modify at your heart's content!
srv = TinyDB('server.json') #Server-specific configuration - allows you to modify stuff like the name of the reactions, for example.

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

def setup(client):
	client.add_cog(Karma(client))