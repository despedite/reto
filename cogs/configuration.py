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
best = TinyDB('bestname.json') #Best Of name: Used to look up the Best-Of name of the channel.

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
		loadingEmoji = self.client.get_emoji(660250625107296256)
		loadingText = await ctx.send(str(loadingEmoji) + " Getting " + botname + " ready to go...")
		error = False
		creationLog = ""
		
		# If the role "Curator" doesn't exist, the bot creates it.
		try:
			rolesearch = discord.utils.get(ctx.guild.roles, name="Curator")
			if rolesearch == None:
				await ctx.guild.create_role(name="Curator")
				creationLog += "\n- The Curator role (users with this role can use the Star emoji) was created."
		except Exception as e:
			error = True
			errorLog = "Something happened while creating the role *Curator*. Maybe the bot doesn't have sufficient permissions?"
		
		# If the channel "#best-of" doesn't exist, the bot creates it.
		try:
			channelsearch = discord.utils.get(ctx.guild.channels, name="best-of")
			if channelsearch == None:
				server = str(ctx.message.guild.id)
				await ctx.guild.create_text_channel('best-of')
				channelid = discord.utils.get(self.client.get_all_channels(), name='best-of')
				print(channelid.id)
				best.upsert({'serverid': server, 'channelid': channelid.id, 'notification': "message"}, Query().serverid == server)
				creationLog += "\n- The Best Of channel, where Starred comments lie, was created."
		except Exception as e:
			error = True
			errorLog = "There was an error while trying to create the Best Of channel. May have to do with permissions?"

		# If the user who executed the command doesn't have assigned the role "Curator", the bot assigns it.
		try:
			if discord.utils.get(ctx.message.author.roles, name="Curator") is None:
				role = discord.utils.get(ctx.guild.roles, name="Curator")
				await ctx.message.author.add_roles(role)
				creationLog += "\n- You were given the role Curator."
		except Exception as e:
			error = True
			errorLog = "While creating the role Curator, an error occurred. May have to do something with permissions."

		# If the emoji "10" doesn't exist, the bot creates it.
		try:
			rolesearch = discord.utils.get(ctx.guild.roles, name="Curator")
			emojisearch = discord.utils.get(ctx.guild.emojis, name="10")
			if emojisearch == None:
				with open("images/star.png", "rb") as image:
					await ctx.guild.create_custom_emoji(name="10", image=image.read(), roles=[rolesearch])
					creationLog += "\n- The emoji Star (+10) was created. Only Curators can use it to add content to the Best Of channel!"
		except Exception as e:
			error = True
			errorLog = "Trying to create the role-exclusive emoji Star (10) sent out an error. Maybe there's not enough space for new emoji, or the bot doesn't have permissions."

		# If the emoji "plus" doesn't exist, the bot creates it.
		try:
			plussearch = discord.utils.get(ctx.guild.emojis, name="plus")
			if plussearch == None:
				with open("images/plus.png", "rb") as image:
					await ctx.guild.create_custom_emoji(name="plus", image=image.read())
					creationLog += "\n The emoji Heart (+1) was created."
		except Exception as e:
			error = True
			errorLog = "Trying to create the emoji Heart (plus) sent out an error. Maybe there's not enough space for new emoji, or the bot doesn't have permissions."
		
		# If the emoji "minus" doesn't exist, the bot creates it.
		try:
			minussearch = discord.utils.get(ctx.guild.emojis, name="minus")
			if minussearch == None:
				with open("images/minus.png", "rb") as image:
					await ctx.guild.create_custom_emoji(name="minus", image=image.read())
					creationLog += "\n- The emoji Crush (-1) was created."
		except Exception as e:
			error = True
			errorLog = "Trying to create the emoji Crush (minus) sent out an error. Maybe there's not enough space for new emoji, or the bot doesn't have permissions."
		
		await loadingText.delete()
		emoji = discord.utils.get(ctx.message.guild.emojis, name="10")
		
		if error == False and creationLog != "":
			await ctx.send("**" + botname + "** is now set up and ready to go!\n\n*What changed?*")
			creationLog += "\n"
			if creationLog != "":
				await ctx.send(creationLog)
			await ctx.send("*What now?*\n- Giving someone the role *Curator* on Server Settings will let them use the " + str(emoji) + " emoji to star posts. A Discord restart (CTRL+R) may be needed to see the emoji.\n- Edit the look of the default emojis using the command ?emoji to make " + botname + " your own!\n- Rename the #best-of channel to a name you like the most on Server Settings.\n- Use the command ?notification if your server is big, and you'd rather change the confirm message (e.g. Congrats! +10 points to the user) to a reaction.")
			if devname != "":
				await ctx.send("- If any issues arise, make sure to check in on Reto's official support server, over at **" + devname + "**. :heart:")
			else:
				await ctx.send("- Thank you very much for installing **" + botname + "**! :heart:")
		elif error == True:
			await ctx.send("**Oops!** Something happened and the setup couldn't be completed. (" + errorLog + ")\n- Check that there is space to create three new emojis and that the bot has sufficient permissions.\n- If you're certain everything was taken care off, try writting ?setup again.")
			if devname != "":
				await ctx.send("- In case these issues persist, get in touch: " + devname)
		else:
			await ctx.send("**" + botname + "** was already set up - nothing has changed!\n\n*Want some pointers?*\n- Giving someone the role *Curator* on Server Settings will let them use the " + str(emoji) + " emoji to star posts. A Discord restart (CTRL+R) may be needed to see the emoji.\n- Edit the look of the default emojis using the command ?emoji to make " + botname + " your own!\n- Rename the #best-of channel to a name you like the most on Server Settings.\n- Use the command ?notification if your server is big, and you'd rather change the confirm message (e.g. Congrats! +10 points to the user) to a reaction.")
			if devname != "":
				await ctx.send("- If any issues arise, make sure to check in on Reto's official support server, over at **" + devname + "**. :heart:")
			else:
				await ctx.send("- Thank you very much for installing **" + botname + "**! :heart:")
			
			
	# -------------------------
	#		MANAGE EMOJIS
	# -------------------------
				
	@commands.command(aliases=['reto', 'config', 'cfg', 'emojis'], description='Used by server admins to manage their emojis. ?emoji edit to change the look of a heart/crush/10 points, ?emoji default to restore all emojis, ?emoji best-of to change the name of #best-of. REQUIRED ROLES: Manage messages')
	@commands.has_permissions(manage_guild=True)
	async def emoji(self, ctx, *args):
		"""Used to manage bot emojis. REQUIRED ROLES: Manage messages"""
		script_dir = os.path.dirname(__file__) #<-- absolute dir the script is in
		rel_path = "../images/testimage.png"
		path = os.path.join(script_dir, rel_path)
		if not args:
			await ctx.send("Please provide an argument!\n**?emoji edit** *name_of_emoji* - Lets you edit any of the three default emojis (10/plus/minus). Image required.\n**?emoji default** - Restores the custom emoji (10/plus/minus) to their original state.\n**?emoji best-of** - Allows you to rename the Best Of channel for personalization! Make sure to use this command instead of renaming it through Discord.")
		elif args[0] == "best-of":
			if not args[1]:
				await ctx.send("No name for the #best-of channel was provided. Usage: ?emoji best-of Channel-For-Cool-Posts")
			else:
				server = str(ctx.message.guild.id)
				best.upsert({'serverid': server, 'name': args[1]}, Query().serverid == server)
				await ctx.send("The best-of channel hath now been renamed to " + args[1] + "!")
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
		elif args[0] == "name":
			await ctx.send("working on this feature")
		else:
			await ctx.send("Invalid argument!\n**?emoji edit** *name_of_emoji* - Lets you edit any of the three default emojis (10/plus/minus). Image required.\n**?emoji default** - Restores the custom emoji (10/plus/minus) to their original state.\n**?emoji best-of** - Allows you to rename the Best Of channel for personalization! Make sure to use this command instead of renaming it through Discord.")

	# -------------------------
	#	SET UP NAME MODIFYING
	# -------------------------
				
	@commands.command(description="Let's get you set up and ready to change #best-of's name with this command!")
	@commands.has_permissions(manage_guild=True)
	async def name(self,ctx,*args):
		"""Get the ability to change #best-of's name!"""
		y2k = await ctx.send(":arrows_counterclockwise: Looking up if you're set up already...")
		best.clear_cache()
		server = str(ctx.message.guild.id)
		channel = best.search(Query().serverid == server)
		if (channel):
			await ctx.send(":white_check_mark: **You're already set up!**")
			await ctx.send("If you want to change the name of the #best-of channel, you can edit it on the Discord settings as usual!")
			await y2k.delete()
		else:
			channelid = discord.utils.get(self.client.get_all_channels(), name='best-of')
			print(channelid.id)
			best.upsert({'serverid': server, 'channelid': channelid.id, 'notification': "message"}, Query().serverid == server)
			await ctx.send(":raised_hands: **You weren't set up**, so I did it for you.")
			await ctx.send("If you want to change the name of the #best-of channel, you can edit it on the Discord settings as usual!")
			await y2k.delete()

	# -------------------------
	#	CHANGE NOTIFICATIONS
	# -------------------------
				
	@commands.command(aliases=['notif', 'notifications'], description="Change the confirm notification settings (e.g. Congrats! X person gave you a star and now you're in the Best Of channel.) from Reactions to Messages. (?notification message/?notification reaction)")
	@commands.has_permissions(manage_guild=True)
	async def notification(self,ctx,*args):
		"""Change confirm notif. to messages or reactions."""
		loadingEmoji = self.client.get_emoji(660250625107296256)
		okayEmoji = self.client.get_emoji(660217963911184384)
		server = str(ctx.message.guild.id)
		best.clear_cache()
		server = str(ctx.message.guild.id)
		channel = best.search(Query().serverid == server)
		if not channel:
			channelid = discord.utils.get(self.client.get_all_channels(), name='best-of')
			best.upsert({'serverid': server, 'channelid': channelid.id, 'notification': "message"}, Query().serverid == server)
		notifmode = best.search(Query().serverid == server)
		notifmode = notifmode[0]['notification']
		notifstr = str(notifmode)
		if not args:
			await ctx.send("You're currently using **" + notifstr.capitalize() + "** Mode.\n*?notification message* tells " + botname + " to send a message when someone Stars/Hearts/Crushes a comment. Great for small servers, and shows the Karma that the user currently has.\n*?notification reaction* sends a reaction when someone Stars/Hearts/Crushes a comment. Great if you don't want to have excess notifications on Mobile, but it doesn't show the Karma the user has.")
		elif args[0] == "reaction" or args[0] == "reactions":
			best.update({"notification": "reaction"}, where('serverid') == server)
			await ctx.send("*Got it!* Reto is now on Reaction Mode.\nNext time someone reacts to a comment, said message will be reacted with " + str(okayEmoji) + " for a couple of seconds.")
		elif args[0] == "message" or args[0] == "messages":
			best.update({"notification": "message"}, where('serverid') == server)
			await ctx.send("*Got it!* Reto is now on Message Mode.\nNext time someone reacts to a comment, they'll be sent a message as confirmation (which will delete itself after a couple of seconds).")
		else:
			await ctx.send("**Oops!** That's not a valid option.\n*?notification message* tells " + botname + " to send a message when someone Stars/Hearts/Crushes a comment. Great for small servers, and shows the Karma that the user currently has.\n*?notification reaction* sends a reaction when someone Stars/Hearts/Crushes a comment. Great if you don't want to have excess notifications on Mobile, but it doesn't show the Karma the user has.")
		

def setup(client):
	client.add_cog(Configuration(client))