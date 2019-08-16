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

class Reaction(commands.Cog):
	def __init__(self, client):
		self.client = client
	
	# -------------------------------
	#		   USER REACTS
	# -------------------------------
		
	@commands.Cog.listener()
	async def on_reaction_add(self, reaction, user):
		
		# to-do: check if user who reacted is same as user who posted the messages
		
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
			server = str(reaction.message.guild.id)
			if exists == 0:
				print("user didnt exist.")
				db.insert({'username': value, 'points': 10, 'servers': [server]})
			else:
				User=Query()
				serverid=str(reaction.message.guild.id)
				existsserver = db.count((User.servers.any([serverid])) & (User.username == value))				# no funciona
				print(str(existsserver))
				print("user does exist.")
				print("server id: " + serverid)
				print("is the server in the list?? = " + str(existsserver))
				if existsserver == 0:
					print("server wasnt on the list.")
					db.update(add('points',10), where('username') == value)
					l = str(db.search((User.username == value)))
					print(l)
					if "servers" not in l:
						print("legacy user, didn't have any servers. added its first one")
						docs = db.search(User.username == value)
						for doc in docs:
							doc['servers'] = [str(server)]
						db.write_back(docs)
					else:
						print("added a new server!")
						db.update(add('servers',[server]), where('username') == value)
				else:
					print("server was on the list.")
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
			server = str(reaction.message.guild.id)
			if exists == 0:
				print("user didnt exist.")
				db.insert({'username': value, 'points': 1, 'servers': [server]})
				# Send a confirmation message
				result = db.get(Query()['username'] == value)
				heart = await channel.send("**Hearted!** {} now has {} points. (+1)".format(reaction.message.author.name,result.get('points')))
				await asyncio.sleep(3) 
				await heart.delete()
			else:
				User=Query()
				serverid=str(reaction.message.guild.id)
				existsserver = db.count((User.servers.any([serverid])) & (User.username == value))				# no funciona
				print(str(existsserver))
				print("user does exist.")
				print("server id: " + serverid)
				print("is the server in the list?? = " + str(existsserver))
				if existsserver == 0:
					print("server wasnt on the list.")
					db.update(add('points',1), where('username') == value)
					l = str(db.search((User.username == value)))
					print(l)
					if "servers" not in l:
						print("legacy user, didn't have any servers. added its first one")
						docs = db.search(User.username == value)
						for doc in docs:
							doc['servers'] = [str(server)]
						db.write_back(docs)
					else:
						print("added a new server!")
						db.update(add('servers',[server]), where('username') == value)
				else:
					print("server was on the list.")
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
			server = str(reaction.message.guild.id)
			if exists == 0:
				print("user didnt exist.")
				db.insert({'username': value, 'points': 1, 'servers': [server]})
				# Send a confirmation message
				result = db.get(Query()['username'] == value)
				crush = await channel.send("**Crushed.** {} now has {} points. (-1)".format(reaction.message.author.name,result.get('points')))
				await asyncio.sleep(3) 
				await crush.delete()

			else:
				User=Query()
				serverid=str(reaction.message.guild.id)
				existsserver = db.count((User.servers.any([serverid])) & (User.username == value))				# no funciona
				print(str(existsserver))
				print("user does exist.")
				print("server id: " + serverid)
				print("is the server in the list?? = " + str(existsserver))
				if existsserver == 0:
					print("server wasnt on the list.")
					db.update(subtract('points',1), where('username') == value)
					l = str(db.search((User.username == value)))
					print(l)
					if "servers" not in l:
						print("legacy user, didn't have any servers. added its first one")
						docs = db.search(User.username == value)
						for doc in docs:
							doc['servers'] = [str(server)]
						db.write_back(docs)
					else:
						print("added a new server!")
						db.update(add('servers',[server]), where('username') == value)
				else:
					print("server was on the list.")
					db.update(subtract('points',1), where('username') == value)

				# Send a confirmation message
				result = db.get(Query()['username'] == value)
				crush = await channel.send("**Crushed.** {} now has {} points. (-1)".format(reaction.message.author.name,result.get('points')))
				await asyncio.sleep(3) 
				await crush.delete()

def setup(client):
	client.add_cog(Reaction(client))
