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

db = TinyDB('json/db.json') #Database file: stores points of every user.
cfg = TinyDB("json/config.json") #Config file: stores configurations for the bot. Modify at your heart's content!
srv = TinyDB('json/server.json') #Server-specific configuration - allows you to modify stuff like the name of the reactions, for example.
priv = TinyDB('json/blacklist.json') #Privacy Mode blacklist. Users with PM on will not have their messages logged in the comment leaderboard.
best = TinyDB('json/bestname.json') #Best Of name: Used to look up the Best-Of name of the channel.

for c in cfg:
	bottoken = c['bottoken']
	botname = c['botname']
	support = c['support']
	botver = c['botver']
	prefix = c['prefix']


class Miscellaneous(commands.Cog):
	"""
	Bonus stuff that has to do with the bot's updates, invites, privacy settings, and other extras.
	"""
	def __init__(self, client):
		self.client = client
	
	#------------------------
	# MISCELLANEOUS COMMANDS
	#------------------------
	@commands.command(description="Simple testing command to check the bot's latency.")
	async def ping(self, ctx):
		"""Nothing but a simple latency tester."""
		latency = str(round(self.client.latency,3))
		await ctx.send("🏓 **Pong!** Looks like the latency is about " + latency + "s.")

	@commands.command(aliases=['update', 'changelog', 'log', 'news'], description="Check the new features on the bot since last update!")
	async def updates(self, ctx):
		"""Check Reto's new features!"""
		embed=discord.Embed(title="Changelog", description="Reto 1.5.1 - 2020/9/8\n[Check out the full, more readable changelog on Github!](https://github.com/despedite/reto/releases)", color=0x74f8dd)
		embed.set_thumbnail(url="https://i.ibb.co/ySfQhDG/reto.png")
		embed.add_field(name="Various Hotfixes", value="Various bugs have been quickly patched in the past release. Namely, the ?profile command works as intended on all scenarios, bots now can't react to messages in an attempt to stop ''gaming the system'', and more dialogues have been changed to allow for custom naming (Bot Owner only).", inline=False)
		embed.add_field(name="Read more about it!", value="Reto v1.5, released on August, includes a treasure trove of features. [Read the full changelog](https://github.com/despedite/reto/releases) to take a look at all the changes and overhauls included on the update!", inline=False)
		await ctx.send(embed=embed)

	@commands.command(description='Sends an invite link for the bot to invite it to other servers.')
	async def invite(self, ctx):
		"""Invite the bot to your server!"""
		await ctx.send("Here's an invitation link for the bot: https://discordapp.com/api/oauth2/authorize?client_id=" + str(self.client.user.id) + "&permissions=1342449744&scope=bot")
	
	@commands.command()
	async def privacy(self,ctx,*args):
		"""Info on what Reto knows about you."""
		if not args:
			await ctx.send("The Reto developers value your privacy and strive for full transparency in what data they use.\n**As of v1.2.1**, Reto now logs information of what servers you're in, the amount of points you have, and your user ID. These values are necessary for using ?lb and ?glb functions, and they are in the standard User ID format that Discord.py uses, with no real way to make use of it outside of code.\n**As of v1.3**, Reto now knows the posts you've made and in which server you've made them ONLY if they are hearted/crushed/added to the Best-Of, in order to make ?plb and ?gplb work properly.\n\nIf you wish to not have your personal posts logged, you can opt out of ?plb by enabling Privacy Mode (?privacy on). Note that this will not delete your previous data or disable people from voting on posts made while Privacy Mode was off, and will hide your posts from post leaderboards, local or global.")
		elif args[0] == "on":
			exists = priv.count(Query().username == ctx.message.author.id)
			if exists == 0:
				priv.insert({'username': ctx.message.author.id})
				await ctx.send("**Done!** From now on, Reto will not log your posts. This will opt you out from post leaderboards - if you so wish to re-enable this feature, you can use *?privacy off* to whitelist yourself.")
			else:
				await ctx.send("**Privacy Mode was already turned on**, so nothing has changed. *Did you mean ?privacy off?*")
		elif args[0] == "off":
			priv.remove(where('username') == ctx.message.author.id)
			await ctx.send("**Done!** From now on, Reto will start logging your posts, enabling you to use post leaderboards. You can always turn this off with *?privacy on.*")
		else:
			await ctx.send("The Reto developers value your privacy and strive for full transparency in what data they use.\n**As of v1.2.1**, Reto now logs information of what servers you're in, the amount of points you have, and your user ID. These values are necessary for using ?lb and ?glb functions, and they are in the standard User ID format that Discord.py uses, with no real way to make use of it outside of code.\n**As of v1.3**, Reto now knows the posts you've made and in which server you've made them ONLY if they are hearted/crushed/added to the Best-Of, in order to make ?plb and ?gplb work properly.\n\nIf you wish to not have your personal posts logged, you can opt out of ?plb by enabling Privacy Mode (?privacy on). Note that this will not delete your previous data or disable people from voting on posts made while Privacy Mode was off, and will hide your posts from post leaderboards, local or global.")
			
def setup(client):
	client.add_cog(Miscellaneous(client))