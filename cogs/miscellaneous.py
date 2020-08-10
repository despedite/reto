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

config = cfg.search(Query()['search'] == 'value')
for c in config:
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
		embed=discord.Embed(title="Changelog", description="Reto 1.5 - 2020/8/10\n[Check out the full, more readable changelog on Github!](https://github.com/despedite/reto/releases)", color=0x74f8dd)
		embed.set_thumbnail(url="https://i.ibb.co/ySfQhDG/reto.png")
		embed.add_field(name="Souped-up Leaderboards", value="The Post Leaderboards got a huge make-over! Formerly, you could only see the top 10 posts from the current server and the best server at a snail's pace, due to Discord restrictions. Now, you can see 5 posts at a time, and use the reactions on the last post to see even more posts (or remove them, to prevent spam). Aditionally, you can now @ someone on the ?plb or ?gplb commands to find out their bestest posts, whether that is globally or on said server.", inline=False)
		embed.add_field(name="More helpful Help Command", value="Remember the previous loaded (and loathed) Help command? Well, it's FINALLY, completely re-done. Based off of [StudioMFTechnologies's work](https://gist.github.com/StudioMFTechnologies/ad41bfd32b2379ccffe90b0e34128b8b), " + botname + " now lets you choose from a list of command categories by sending a message on DMs, thus cutting down on unnecesary message clutter. You can write ?help {category} to see every command in said category.", inline=False)
		embed.add_field(name="Personalizable Prefixes", value="Do you have too many bots in your server? Are you getting three bots replying to you whenever you write ?help? Fret not - now you can personalize which prefix " + botname + " goes by now by typing in ?prefix!  Do note that the bot's messages won't change if the server prefix does, so if " + botname + " tells you to use ?lb, for example, remember your preferred prefix and use that instead.", inline=False)
		embed.add_field(name="One-click Activity Manager", value="This one is going to be useful to those who are self-hosting " + botname + ". You know that \"Playing\" status on the bot that constantly changes messages every 30 seconds or so? You can already personalize this rotation on config.json, but it's kind of a hassle. You have to reboot " + botname + ", change the JSON file, it's not pretty. Well, if you set the \"botowner\" variable with your User ID, you can now make use of the ?activity command! You can write your own activities with the syntax ?activity create \"{Insert activity text here}\", or delete previous ones with ?activity delete {id}. No rebooting or messing around with files required!", inline=False)
		embed.add_field(name="In-depth User Profiles", value="The ?karma command has been upgraded and expanded into the ?profile command! (Don't worry, you can still use ?karma just like the ol' times.) Using it will now give you a variety of stats, apart from the karma total. The stats included have in them the absolute karma total, the Global and Local Leaderboard rankings, how many posts you've reacted to, and how many stars your posts have received. It's likely this list will be expanded over time, so stay on the lookout for this tab!", inline=False)
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
