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


db = TinyDB('db.json') #Database file: stores points of every user.
cfg = TinyDB("config.json") #Config file: stores configurations for the bot. Modify at your heart's content!
srv = TinyDB('server.json') #Server-specific configuration - allows you to modify stuff like the name of the reactions, for example.
priv = TinyDB('blacklist.json') #Privacy Mode blacklist. Users with PM on will not have their messages logged in the comment leaderboard.

config = cfg.search(Query()['search'] == 'value')
for c in config:
	bottoken = c['bottoken']
	botname = c['botname']
	devname = c['devname']
	botver = c['botver']
	prefix = c['prefix']


class Miscellaneous(commands.Cog):
	def __init__(self, client):
		self.client = client
	
	#------------------------
	# MISCELLANEOUS COMMANDS
	#------------------------
	@commands.command(description="Simple testing command to check the bot's latency.")
	async def ping(self, ctx):
		"""Simple latency tester."""
		latency = self.client.latency
		await ctx.send(latency)

	@commands.command(description="Check the new features on the bot since last update!")
	async def updates(self, ctx):
		"""Check Reto's new features!"""
		await ctx.send("**v1.3.0** Changelog\n❤️ Post leaderboards! Using ?plb, you'll be able to check the bots with the most amount of votes out there.\n❤️ GLOBAL post leaderboards! By using ?gplb, similarly to regular global leaderboards, you'll be able to check the most upvoted posts of all Discord.\n❤️ Privacy features! Reto saves quite more data about your usage than before: by using ?privacy you'll be able to limit Reto's usage.\n❤️ ?update now allows you to check the Reto update changelog. Like you're doing right now, of course.\n❤️ For Reto forkers on GitHub, now you can change the bot's activity in the config.json file.\n❤️ Various bugfixes! Namely, you can't heart, crush or star your own comments now to prevent comment exploiting.")

	@commands.command(description='Sends an invite link for the bot to invite it to other servers.')
	async def invite(self, ctx):
		"""Invite the bot to your server!"""
		await ctx.send("Here's an invitation link for the bot: https://discordapp.com/api/oauth2/authorize?client_id=" + str(self.client.user.id) + "&permissions=1342449744&scope=bot")
	
	@commands.command()
	async def privacy(self,ctx,*args):
		"""Info on what Reto knows about you."""
		if not args:
			await ctx.send("The Reto developers value your privacy and strive for full transparency in what data they use.\n**As of v1.2.1**, Reto now logs information of what servers you're in, the amount of points you have, and your user ID. These values are necessary for using ?lb and ?glb functions, and they are in the standard User ID format that Discord.py uses, with no real way to make use of it outside of code.\n**As of v1.3**, Reto now knows the posts you've made and in which server you've made them ONLY if they are hearted/crushed/added to the Best-Of, in order to make ?plb and ?gplb work properly.\nIf you wish to not have your personal posts logged, you can opt out of ?plb by enabling Privacy Mode (?privacy on). Note that this will not delete your previous data or disable people from voting on posts made while Privacy Mode was off, and will hide your posts from post leaderboards, local or global.")
		elif args[0] == "on":
			exists = priv.count(Query().username == ctx.message.author.id)
			if exists == 0:
				priv.insert({'username': ctx.message.author.id})
				await ctx.send("**Done!** From now on, Reto will not log your posts. This will opt you out from post leaderboards - if you so wish to re-enable this feature, you can use *?privacy on* to whitelist yourself.")
			else:
				await ctx.send("**Privacy Mode was already turned on**, so nothing has changed. *Did you mean ?privacy off?*")
		elif args[0] == "off":
			priv.remove(where('username') == ctx.message.author.id)
			await ctx.send("**Done!** From now on, Reto will start logging your posts, enabling you to use post leaderboards. You can always turn this off with *?privacy off.*")
		else:
			await ctx.send("The Reto developers value your privacy and strive for full transparency in what data they use.\n**As of v1.2.1**, Reto now logs information of what servers you're in, the amount of points you have, and your user ID. These values are necessary for using ?lb and ?glb functions, and they are in the standard User ID format that Discord.py uses, with no real way to make use of it outside of code.\n**As of v1.3**, Reto now knows the posts you've made and in which server you've made them ONLY if they are hearted/crushed/added to the Best-Of, in order to make ?plb and ?gplb work properly.\nIf you wish to not have your personal posts logged, you can opt out of ?plb by enabling Privacy Mode (?privacy on). Note that this will not delete your previous data or disable people from voting on posts made while Privacy Mode was off, and will hide your posts from post leaderboards, local or global.")
	

def setup(client):
	client.add_cog(Miscellaneous(client))
