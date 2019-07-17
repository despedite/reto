import discord
from discord.ext import commands
import asyncio
import pyfiglet
from tinydb import TinyDB, Query, where
from tinydb.operations import add, subtract
import aiohttp        
import aiofiles
import os.path
db = TinyDB('db.json')

# ↓↓↓ MODIFY THIS FIRST! ↓↓↓

bottoken = "BOT_TOKEN_HERE" # This is needed to host the bot. Never share this token!
botname = "Rēto" # How the code will refer to your bot.
devname = "@Erik#0944" # OPTIONAL: Contact information for the bot's creator, mentioned at the end of ?setup. If left blank, no dev contact info will be shown.

# ↑↑↑ MODIFY THIS FIRST! ↑↑↑

prefix = "?"
bot = commands.Bot(command_prefix=prefix)
client = discord.Client()
ascii_banner = pyfiglet.figlet_format(botname + ".py")

# -------------------------
#	  ON READY COMMAND
# -------------------------

@bot.event
async def on_ready():
	print (ascii_banner)
	print (botname + " is ONLINE!")
	if len(bot.guilds) == 1:
		print ("Running with the name " + str(bot.user) + " on " + str(len(bot.guilds)) + " server")
	else:
		print ("Running with the name " + str(bot.user) + " on " + str(len(bot.guilds)) + " servers")
	print ("Invite link: https://discordapp.com/api/oauth2/authorize?client_id=" + str(bot.user.id) + "&permissions=1342449744&scope=bot")
	print ("?setup to get started!")
	print ("--------------------------------------------")
	game = discord.Game("?setup to start! | 1.1.1")
	await bot.change_presence(activity=game)

# -------------------------
#			SETUP
# -------------------------

@bot.command(pass_context=True, description="Sets up the bot, creating the necessary roles, channels and emojis for it to function. REQUIRED ROLES: Manage messages")
@commands.has_permissions(manage_guild=True)
async def setup(ctx):
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
	except:
		await ctx.send(":x: An error has occurred while creating the role **Curator**. Check the bot's permissions and try again!")
	
	# If the channel "#best-of" doesn't exist, the bot creates it.
	try:
		channelsearch = discord.utils.get(ctx.guild.channels, name="best-of")
		if channelsearch == None:
			await ctx.guild.create_text_channel('best-of')
			await ctx.send(":two: The channel **best-of** has been created. Here's where messages that have had the reaction '10' will go.")
		else:
			await ctx.send(":two: The channel **best-of** already exists, no further action has been taken.")
	except:
		await ctx.send(":x: An error has occurred while creating the channel **#best-of**. Check the bot's permissions and try again!")

	# If the user who executed the command doesn't have assigned the role "Curator", the bot assigns it.
	try:
		if discord.utils.get(ctx.message.author.roles, name="Curator") is None:
			role = discord.utils.get(ctx.guild.roles, name="Curator")
			await ctx.message.author.add_roles(role)
			await ctx.send(":three: The role **Curator** has been assigned to you! This means that you can access the emoji :10: later on. For other people, assign it to them manually and after a restart (CTRL+R) they should be able to access said emoji.")
		else:
			await ctx.send(":three: The role **Curator** has already been assigned, no further action has been taken.")
	except:
		await ctx.send(":x: An error has occurred while assigning you the role **Curator**. Check the bot's permissions and try again!")

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
	except:
		await ctx.send(":x: An error has occurred while creating the role-exclusive emoji **:10:**. Check the bot's permissions and that there's space for three more emojis and try again!")

	# If the emoji "plus" doesn't exist, the bot creates it.
	try:
		plussearch = discord.utils.get(ctx.guild.emojis, name="plus")
		if plussearch == None:
			with open("images/plus.png", "rb") as image:
				await ctx.guild.create_custom_emoji(name="plus", image=image.read())
				await ctx.send(":five: The emoji **:plus:** has been created. This emoji can be used by anyone to increase the commenter's karma by one!")
		else:
			await ctx.send(":five: The emoji **:plus:** already exists, no further action has been taken.")
	except:
		await ctx.send(":x: An error has occurred while creating the emoji **:plus:**. Check the bot's permissions and that there's space for three more emojis and try again!")
	
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
	except:
		await ctx.send(":x: An error has occurred while creating the emoji **:minus:**. Check the bot's permissions and that there's space for three more emojis and try again!")

# -------------------------------
#		   USER REACTS
# -------------------------------
	
@bot.event
async def on_reaction_add(reaction, user):

	# -------------------------
	#	  REACTION = :10:
	# -------------------------

	if reaction.emoji.name == '10' and reaction.count == 1:
		channel = reaction.message.channel
		
		# Post the message in #best-of

		contenido=reaction.message.content
		autor=reaction.message.author.name
		foto=reaction.message.author.avatar_url
		if(len(reaction.message.attachments) > 0):
			imagen=reaction.message.attachments[0].url
		subido=reaction.users(limit=1)
		emberino=discord.Embed(description=contenido)
		emberino.set_author(name=autor, icon_url=foto)
		if(len(reaction.message.attachments) > 0):
			emberino.set_image(url=imagen)
		channel = discord.utils.get(reaction.message.guild.channels, name="best-of")

		# Add user to the points table
		value = str(reaction.message.author.id)
		exists = db.count(Query().username == value)
		if exists == 0:
			db.insert({'username': value, 'points': 10})
		else:
			db.update(add('points',10), where('username') == value)
		
		# If the channel #best-of doesn't exist, the bot creates it before posting it.
		
		if channel == None:
			await reaction.message.guild.create_text_channel('best-of')
			channel = reaction.message.channel
			await channel.send("The channel **best-of** doesn't exist, if the bot has permissions it has been created.")
			channel = discord.utils.get(reaction.message.guild.channels, name="best-of")
			await channel.send(embed=emberino)
		else:
			await channel.send(embed=emberino)
		
		# Send a confirmation message

		channel = reaction.message.channel
		result = db.get(Query()['username'] == value)
		
		send = await channel.send("Congrats, **{}**! Your post will be forever immortalized in the server's #best-of. You now have {} points. (+10)".format(reaction.message.author.name,result.get('points')))
		
		# Delete said message
		await asyncio.sleep(3) 
		await send.delete()

	# -------------------------
	#	  REACTION = :PLUS:
	# -------------------------	
	
	if reaction.emoji.name == 'plus':
		channel = reaction.message.channel

		# Add user to the points table
		value = str(reaction.message.author.id)
		exists = db.count(Query().username == value)
		if exists == 0:
			db.insert({'username': value, 'points': 1})

			# Send a confirmation message
			result = db.get(Query()['username'] == value)
			heart = await channel.send("**Hearted!** {} now has {} points. (+1)".format(reaction.message.author.name,result.get('points')))
			await asyncio.sleep(3) 
			await heart.delete()

		else:
			db.update(add('points',1), where('username') == value)

			# Send a confirmation message
			result = db.get(Query()['username'] == value)
			heart = await channel.send("**Hearted!** {} now has {} points. (+1)".format(reaction.message.author.name,result.get('points')))
			await asyncio.sleep(3) 
			await heart.delete()

	# -------------------------
	#	  REACTION = :MINUS:
	# -------------------------	
	
	if reaction.emoji.name == 'minus':
		channel = reaction.message.channel

		# Add user to the points table
		value = str(reaction.message.author.id)
		exists = db.count(Query().username == value)
		if exists == 0:
			db.insert({'username': value, 'points': -1})

			# Send a confirmation message
			result = db.get(Query()['username'] == value)
			crush = await channel.send("**Crushed.** {} now has {} points. (-1)".format(reaction.message.author.name,result.get('points')))
			await asyncio.sleep(3) 
			await crush.delete()

		else:
			db.update(subtract('points',1), where('username') == value)

			# Send a confirmation message
			result = db.get(Query()['username'] == value)
			crush = await channel.send("**Crushed.** {} now has {} points. (-1)".format(reaction.message.author.name,result.get('points')))
			await asyncio.sleep(3) 
			await crush.delete()

# -------------------------
#	      ?KARMA
# -------------------------

@bot.command(aliases=['points', 'point'], description="Check the accumulated amount of points (Karma) a given user has. Ping to check another user's karma account.")
async def karma(ctx, *args):
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

# -------------------------
#		MANAGE EMOJIS
# -------------------------
			
@bot.command(aliases=['reto', 'config', 'cfg', 'emojis'], description='Used by server admins to manage their emojis. ?emoji edit to change the look of a heart/crush/10 points, ?emoji default to restore all emojis. REQUIRED ROLES: Manage messages')
@commands.has_permissions(manage_guild=True)
async def emoji(ctx, *args):
	"""Used to manage bot emojis. REQUIRED ROLES: Manage messages"""
	script_dir = os.path.dirname(__file__) #<-- absolute dir the script is in
	rel_path = "images/testimage.png"
	path = os.path.join(script_dir, rel_path)
	if not args:
		await ctx.send("Please provide an argument!\n**?emoji edit** *name_of_emoji* - Lets you edit any of the three default emojis (10/plus/minus). Image required.\n**?emoji default** - Restores the custom emoji (10/plus/minus) to their original state.")
	elif args[0] == "edit":
		if len(args) != 2:
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
								with open("images/testimage.png", "rb") as image:
									emojisearch = discord.utils.get(ctx.guild.emojis, name="10")
									await emojisearch.delete()
									await ctx.guild.create_custom_emoji(name="10", image=image.read(), roles=[rolesearch])
									await ctx.send("The emoji **:10:** has been modified.")
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
								with open("images/testimage.png", "rb") as image:
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
								with open("images/testimage.png", "rb") as image:
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
	else:
		await ctx.send("Invalid argument!\n**?emoji edit** *name_of_emoji* - Lets you edit any of the three default emojis (10/plus/minus). Image required.\n**?emoji default** - Restores the custom emoji (10/plus/minus) to their original state.")
@bot.command(description="Simple testing command to check the bot's latency.")
async def ping(ctx):
	"""Simple latency tester."""
	latency = bot.latency
	await ctx.send(latency)

@bot.command(description='Sends an invite link for the bot to invite it to other servers.')
async def invite(ctx):
	"""Invite the bot to your server!"""
	await ctx.send("Here's an invitation link for the bot: https://discordapp.com/api/oauth2/authorize?client_id=" + str(bot.user.id) + "&permissions=1342449744&scope=bot")

bot.run(bottoken)