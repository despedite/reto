import discord
from discord.ext import commands
import asyncio
from tinydb import TinyDB, Query, where
from tinydb.operations import add, subtract
import aiohttp        
import aiofiles
import os.path
import os
from collections import Counter


cfg = TinyDB("json/config.json") #Config file: stores configurations for the bot. Modify at your heart's content!
activity = TinyDB('json/activity.json') #Activity file: the "Playing" commands the bot has.

config = cfg.search(Query()['search'] == 'value')
for c in config:
	bottoken = c['bottoken']
	botname = c['botname']
	support = c['support']
	botver = c['botver']
	prefix = c['prefix']
	botowner = c['botowner']


class Management(commands.Cog):
	"""
	Commands that have to do with Reto's upkeep. Not relevant to normal users.
	"""
	def __init__(self, client):
		self.client = client
	
	#-------------------------
	#   MANAGEMENT COMMANDS
	#-------------------------
	@commands.command()
	async def activity(self,ctx,*args):
		"""[BOT ADMIN ONLY] Change the bot's activity."""
		isOwner = False
		for x in botowner:
			if (int(ctx.message.author.id) == int(x)):
				isOwner = True

		if isOwner:
			if not args:
				embed = await showActivityList()
				glb = await ctx.send(embed=embed)
			if args[0] == "create":
				if len(args) == 1:
					await ctx.send("Please introduce the text of the activity to be created.")
				else:
					activity.insert({'activity': args[1]})
					await ctx.send('The activity "' + args[1] + '" has been added to the list!')
			elif args[0] == "delete":
				if len(args) == 1:
					await ctx.send("Please introduce the ID of the activity to be deleted. _You can check it doing ?activity_.")
				else:
					# if len of activity equals 1 then dont let it remove
					try:
						toDelete = [int(args[1])]
						activity.remove(doc_ids=toDelete)
					except:
						await ctx.send("The activity with the ID " + args[1] + " couldn't be deleted. (Double check if it exists?)")
					else:
						await ctx.send('The activity with the ID ' + args[1] + ' has been deleted.')
			else:
				embed = await showActivityList()
			glb = await ctx.send(embed=embed)
		else:
			await ctx.send("Looks like you don't have permission to do this?\n_Are you hosting " + botname + "? If so make sure your User ID is on the **botowner** array on the config.json file!_")

async def showActivityList():
	activity.clear_cache()
	result = activity.all()
	s = ""

	for value in result: 
		s += ("ID: " + str(value.doc_id) + " - " + value["activity"] + "\n")
	embed = discord.Embed(title="List of Activities", colour=discord.Colour(0xa353a9), description=s)
	embed.set_footer(text="Add more with ?activity create, or remove one with ?activity delete.")
	return embed
			
def setup(client):
	client.add_cog(Management(client))