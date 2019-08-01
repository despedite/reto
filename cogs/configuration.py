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

class Configuration(commands.Cog):
	def __init__(self, client):
		self.client = client
	
	# ---------------------
	#	  SET UP BOT
	# ---------------------

	
	
	@commands.command(name="setup", pass_context=True, description="Sets up the bot, creating the necessary roles, channels and emojis for it to function. REQUIRED ROLES: Manage messages")
	@commands.has_permissions(manage_guild=True)
	async def setup(self, ctx):
		"""Sets up the bot automagically. REQUIRED ROLES: Manage messages"""
		await ctx.send("Oh, hi there! Let's get the bot set up.")
		await ctx.send("Before starting, check that there is space to create three new emojis and that the bot has sufficient permissions. If the setup process doesn't finish properly, correct these issues and input ?setup again.")
		
		# If the role "Curator" doesn't exist, the bot creates it.
		try:
			rolesearch = discord.utils.get(ctx.guild.roles, name="Curator")
			if rolesearch == None:
				await ctx.guild.create_role(name="Curator")
				await ctx.send(":one: I've created the role **Curator**. Give this role to the people you want to allow posting on the Best Of channel.")
			else:
				await ctx.send(":one: The role **Curator** already exists, no further action has been taken.")
		except Exception as e:
			await ctx.send(":x: An error has occurred while creating the role **Curator**: " + e)
		
		# If the channel "#best-of" doesn't exist, the bot creates it.
		try:
			channelsearch = discord.utils.get(ctx.guild.channels, name="best-of")
			if channelsearch == None:
				await ctx.guild.create_text_channel('best-of')
				await ctx.send(":two: The channel **best-of** has been created. Here's where messages that have had the reaction '10' will go.")
			else:
				await ctx.send(":two: The channel **best-of** already exists, no further action has been taken.")
		except Exception as e:
			await ctx.send(":x: An error has occurred while creating the channel **#best-of**: " + e)

		# If the user who executed the command doesn't have assigned the role "Curator", the bot assigns it.
		try:
			if discord.utils.get(ctx.message.author.roles, name="Curator") is None:
				role = discord.utils.get(ctx.guild.roles, name="Curator")
				await ctx.message.author.add_roles(role)
				await ctx.send(":three: The role **Curator** has been assigned to you! This means that you can access the emoji :10: later on. For other people, assign it to them manually and after a restart (CTRL+R) they should be able to access said emoji.")
			else:
				await ctx.send(":three: The role **Curator** has already been assigned, no further action has been taken.")
		except Exception as e:
			await ctx.send(":x: An error has occurred while assigning you the role **Curator**: " + e)

		# If the emoji "10" doesn't exist, the bot creates it.
		try:
			rolesearch = discord.utils.get(ctx.guild.roles, name="Curator")
			emojisearch = discord.utils.get(ctx.guild.emojis, name="10")
			if emojisearch == None:
				with open("images/star.png", "rb") as image:
					await ctx.guild.create_custom_emoji(name="10", image=image.read(), roles=[rolesearch])
					await ctx.send(":four: The emoji **:10:** has been created. This emoji can only be used by **Curator**s, and will send the message to the **#best-of** channel.")
			else:
				await ctx.send(":four: The emoji **:10:** already exists, no further action has been taken.")
		except Exception as e:
			await ctx.send(":x: An error has occurred while creating the role-exclusive emoji **:10:**: " + e)

		# If the emoji "plus" doesn't exist, the bot creates it.
		try:
			plussearch = discord.utils.get(ctx.guild.emojis, name="plus")
			if plussearch == None:
				with open("images/plus.png", "rb") as image:
					await ctx.guild.create_custom_emoji(name="plus", image=image.read())
					await ctx.send(":five: The emoji **:plus:** has been created. This emoji can be used by anyone to increase the commenter's karma by one!")
			else:
				await ctx.send(":five: The emoji **:plus:** already exists, no further action has been taken.")
		except Exception as e:
			await ctx.send(":x: An error has occurred while creating the emoji **:plus:**: " + e)
		
		# If the emoji "minus" doesn't exist, the bot creates it.
		try:
			minussearch = discord.utils.get(ctx.guild.emojis, name="minus")
			if minussearch == None:
				with open("images/minus.png", "rb") as image:
					await ctx.guild.create_custom_emoji(name="minus", image=image.read())
					await ctx.send(":six: The emoji **:minus:** has been created. This emoji can be used by anyone to decrease the commenter's karma by one.")
			else:
				await ctx.send(":six: The emoji **:minus:** already exists, no further action has been taken.")
			
			await ctx.send("-----------------------")
			await ctx.send("You're all set! Now all you have to do is assign the **Curator** role on Server Settings to people you want to let contribute to #best_of. A Discord restart (CTRL+R) may be needed to see the emoji.\nAfter you're done, check out the ?emoji command if you want to edit what emojis are displayed as :10:, :plus: and :minus:.")
			if devname != "":
				await ctx.send("Thank you very much for installing **" + botname + "**! If you have any issues, please contact **" + devname + "**. :heart:")
			else:
				await ctx.send("Thank you very much for installing **" + botname + "**! :heart:")
		except Exception as e:
			await ctx.send(":x: An error has occurred while creating the emoji **:minus:**: " + e)
			
			
	# -------------------------
	#		MANAGE EMOJIS
	# -------------------------
				
	@commands.command(aliases=['reto', 'config', 'cfg', 'emojis'], description='Used by server admins to manage their emojis. ?emoji edit to change the look of a heart/crush/10 points, ?emoji default to restore all emojis. REQUIRED ROLES: Manage messages')
	@commands.has_permissions(manage_guild=True)
	async def emoji(self, ctx, *args):
		"""Used to manage bot emojis. REQUIRED ROLES: Manage messages"""
		script_dir = os.path.dirname(__file__) #<-- absolute dir the script is in
		rel_path = "../images/testimage.png"
		path = os.path.join(script_dir, rel_path)
		if not args:
			await ctx.send("Please provide an argument!\n**?emoji edit** *name_of_emoji* - Lets you edit any of the three default emojis (10/plus/minus). Image required.\n**?emoji default** - Restores the custom emoji (10/plus/minus) to their original state.")
		elif args[0] == "edit":
			if len(args) != 3:
				await ctx.send ("No emoji name was provided. Valid emoji names: 10/plus/minus")
			elif args[1] == "10":
					if not ctx.message.attachments:
						await ctx.send("I couldn't find an image! Upload an image along with your command (not an URL).")
					else:
						async with aiohttp.ClientSession() as session:
							url = ctx.message.attachments[0].url
							print (url)
							async with session.get(url) as resp:
								if resp.status == 200:
									f = await aiofiles.open(path, mode='wb')
									await f.write(await resp.read())
									await f.close()
									rolesearch = discord.utils.get(ctx.guild.roles, name="Curator")
									with open("../images/testimage.png", "rb") as image:
										emojisearch = discord.utils.get(ctx.guild.emojis, name="10")
										await emojisearch.delete()
										await ctx.guild.create_custom_emoji(name="10", image=image.read())
										await ctx.send("The emoji **:plus:** has been modified.")
										
			elif args[1] == "plus":
					if not ctx.message.attachments:
						await ctx.send("I couldn't find an image! Upload an image along with your command (not an URL).")
					else:
						async with aiohttp.ClientSession() as session:
							url = ctx.message.attachments[0].url
							print (url)
							async with session.get(url) as resp:
								if resp.status == 200:
									f = await aiofiles.open(path, mode='wb')
									await f.write(await resp.read())
									await f.close()
									rolesearch = discord.utils.get(ctx.guild.roles, name="Curator")
									with open("../images/testimage.png", "rb") as image:
										emojisearch = discord.utils.get(ctx.guild.emojis, name="plus")
										await emojisearch.delete()
										await ctx.guild.create_custom_emoji(name="plus", image=image.read())
										await ctx.send("The emoji **:plus:** has been modified.")
			elif args[1] == "minus":
					if not ctx.message.attachments:
						await ctx.send("I couldn't find an image! Upload an image along with your command (not an URL).")
					else:
						async with aiohttp.ClientSession() as session:
							url = ctx.message.attachments[0].url
							print (url)
							async with session.get(url) as resp:
								if resp.status == 200:
									f = await aiofiles.open(path, mode='wb')
									await f.write(await resp.read())
									await f.close()
									rolesearch = discord.utils.get(ctx.guild.roles, name="Curator")
									with open("../images/testimage.png", "rb") as image:
										emojisearch = discord.utils.get(ctx.guild.emojis, name="minus")
										await emojisearch.delete()
										await ctx.guild.create_custom_emoji(name="minus", image=image.read())
										await ctx.send("The emoji **:minus:** has been modified.")
			else:
				await ctx.send("Invalid emoji name. Valid names: 10/plus/minus")
		elif args[0] == "default":
			try:
				# Restore :10:
				rolesearch = discord.utils.get(ctx.guild.roles, name="Curator")
				emojisearch = discord.utils.get(ctx.guild.emojis, name="10")
				if emojisearch == None:
					with open("images/star.png", "rb") as image:
						await ctx.guild.create_custom_emoji(name="10", image=image.read(), roles=[rolesearch])
				else:
					await emojisearch.delete()
					with open("images/star.png", "rb") as image:
						await ctx.guild.create_custom_emoji(name="10", image=image.read(), roles=[rolesearch])
				# Restore :plus:
				emojisearch = discord.utils.get(ctx.guild.emojis, name="plus")
				if emojisearch == None:
					with open("images/plus.png", "rb") as image:
						await ctx.guild.create_custom_emoji(name="plus", image=image.read())
				else:
					await emojisearch.delete()
					with open("images/plus.png", "rb") as image:
						await ctx.guild.create_custom_emoji(name="plus", image=image.read())
				# Restore :minus:
				emojisearch = discord.utils.get(ctx.guild.emojis, name="minus")
				if emojisearch == None:
					with open("images/minus.png", "rb") as image:
						await ctx.guild.create_custom_emoji(name="minus", image=image.read())
				else:
					await emojisearch.delete()
					with open("images/minus.png", "rb") as image:
						await ctx.guild.create_custom_emoji(name="minus", image=image.read())
				await ctx.send("All emojis have been restored!")
			except:
				await ctx.send("An error has occurred while restoring the emojis. Check the bot's permissions and that there's space for three more emojis and try again!")
		elif args[0] == "name":
			await ctx.send("working on this feature")
		else:
			await ctx.send("Invalid argument!\n**?emoji edit** *name_of_emoji* - Lets you edit any of the three default emojis (10/plus/minus). Image required.\n**?emoji default** - Restores the custom emoji (10/plus/minus) to their original state.")
	
def setup(client):
	client.add_cog(Configuration(client))