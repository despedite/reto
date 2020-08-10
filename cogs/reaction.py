import discord
from discord.ext import commands
import asyncio
from tinydb import TinyDB, Query, where
from tinydb.operations import add, subtract
import aiohttp		  
import aiofiles
import os.path
import os

from sharedFunctions import printLeaderboard, createLeaderboardEmbed

db = TinyDB('json/db.json') #Database file: stores points of every user.
cfg = TinyDB("json/config.json") #Config file: stores configurations for the bot. Modify at your heart's content!
srv = TinyDB('json/server.json') #Server-specific configuration - allows you to modify stuff like the name of the reactions, for example.
post = TinyDB('json/comments.json') #Comment leaderboard.
priv = TinyDB('json/blacklist.json') #Privacy Mode blacklist. Users with PM on will not have their messages logged in the comment leaderboard.
best = TinyDB('json/bestname.json') #name and type of notif
dm = TinyDB('json/deletables.json') #Message deletion for Leaderboards.

config = cfg.search(Query()['search'] == 'value')
for c in config:
	bottoken = c['bottoken']
	botname = c['botname']
	support = c['support']
	botver = c['botver']
	prefix = c['prefix']

class Reaction(commands.Cog):
	"""
	Code for the bot's Reaction feature - assigning posts and all.
	"""
	def __init__(self, client):
		self.client = client
	
	# -------------------------------
	#		   USER REACTS
	# -------------------------------
		
	@commands.Cog.listener()
	async def on_reaction_add(self, reaction, user):
		value = user.id
		User=Query()
		votedbefore = post.count((User.voters.any([user.id])) & (User.msgid == str(reaction.message.id)))
		if votedbefore == 0:
			if user.id != reaction.message.author.id: # remove when testing!

				if not isinstance(reaction.emoji, str):
					# -------------------------
					#	  REACTION = :10:
					# -------------------------
					
					channel = reaction.message.channel
					is_nsfw = channel.is_nsfw()
					
					if reaction.emoji.name == '10' and reaction.count == 1:
						channel = reaction.message.channel
						
						messageurl = "https://discordapp.com/channels/" + str(reaction.message.guild.id) + "/" + str(reaction.message.channel.id) + "/" + str(reaction.message.id)
						
						# Post the message in #best-of

						contenido=reaction.message.content
						autor=reaction.message.author.name
						foto=reaction.message.author.avatar_url
						if(len(reaction.message.attachments) > 0):
							imagen=reaction.message.attachments[0].url
						subido=reaction.users(limit=1)
						emberino=discord.Embed(description=contenido)
						emberino.set_author(name=autor, url=messageurl, icon_url=foto)
						if(len(reaction.message.attachments) > 0):
							emberino.set_image(url=imagen)
							
						# the difficult challenge of finding the channel to post to
						
						best.clear_cache()
						server = str(reaction.message.guild.id)
						channel = best.search(Query().serverid == server)
						print("query: " + str(channel))
						try:
							channel = channel[0]['channelid'] # channel id of best-of channel
							print("id: " + str(channel))
							channel = discord.utils.get(reaction.message.guild.channels, id=channel)
							print("new: " + str(channel))
							if channel == None:
								print("something wrong iguess")
								channel = discord.utils.get(reaction.message.guild.channels, name="best-of")
								if channel == None:
									# if the bot doesn't find a channel named best-of, the channnel has been deleted. create a new one!
									print("The channel has been deleted! Oh no!")
									await reaction.message.guild.create_text_channel('best-of')
									channel = discord.utils.get(reaction.message.guild.channels, name="best-of")
									best.upsert({'serverid': server, 'channelid': channel.id, 'notification': "message"}, Query().serverid == server)
									channelformsg = reaction.message.channel
									await channelformsg.send("The *Best Of* channel doesn't exist, if the bot has permissions it has been created.")
									channel = best.search(Query().serverid == server)
									channel = channel[0]['channelid']
									channel = discord.utils.get(reaction.message.guild.channels, id=channel)
								else:
									# if the bot does find a channel named best-of, the channel needs to be linked to the new db.
									# this is for legacy users (1.3.5 and below)
									print("#best-of is a legacy channel, so I added it to the DB.")
									best.upsert({'serverid': server, 'channelid': channel.id, 'notification': "message"}, Query().serverid == server)
									channel = best.search(Query().serverid == server)
									channel = channel[0]['channelid']
									channel = discord.utils.get(reaction.message.guild.channels, id=channel)
						except IndexError:
							print("something wrong iguess")
							channel = discord.utils.get(reaction.message.guild.channels, name="best-of")
							if channel == None:
								# if the bot doesn't find a channel named best-of, the channnel has been deleted. create a new one!
								print("The channel has been deleted! Oh no!")
								await reaction.message.guild.create_text_channel('best-of')
								channel = discord.utils.get(reaction.message.guild.channels, name="best-of")
								best.upsert({'serverid': server, 'channelid': channel.id, 'notification': "message"}, Query().serverid == server)
								channelformsg = reaction.message.channel
								await channelformsg.send("The *Best Of* channel doesn't exist, if the bot has permissions it has been created.")
								channel = best.search(Query().serverid == server)
								channel = channel[0]['channelid']
								channel = discord.utils.get(reaction.message.guild.channels, id=channel)
							else:
								# if the bot does find a channel named best-of, the channel needs to be linked to the new db.
								# this is for legacy users (1.3.5 and below)
								print("#best-of is a legacy channel, so I added it to the DB.")
								best.upsert({'serverid': server, 'channelid': channel.id, 'notification': "message"}, Query().serverid == server)
								channel = best.search(Query().serverid == server)
								channel = channel[0]['channelid']
								channel = discord.utils.get(reaction.message.guild.channels, id=channel)
						
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
						
						# Finally, the bot sends the message to the Best-Of channel.
						
						if channel == None:
							channelformsg = reaction.message.channel
							await channelformsg.send("Uh-oh! This shouldn't have happened.")
						else:
							await channel.send(embed=emberino)

						# Log post for post leaderboard
							
						priv.clear_cache()
						exists = priv.count(Query().username == reaction.message.author.id)
						valuetwo = str(reaction.message.id)
						username = str(reaction.message.author.id)
						postexists = post.count(Query().msgid == valuetwo)
						if postexists == 0:
							if exists == 0:
								print("post wasnt previously on lb")
								if (len(reaction.message.attachments) > 0):
									post.insert({'msgid': valuetwo, 'username': username, 'points': 10, 'servers': server, 'content': reaction.message.content, 'embed': reaction.message.attachments[0].url, 'voters': [user.id], 'stars': 1, 'nsfw': is_nsfw})
								else:
									post.insert({'msgid': valuetwo, 'username': username, 'points': 10, 'servers': server, 'content': reaction.message.content, 'embed': '', 'voters': [user.id], 'stars': 1, 'nsfw': is_nsfw})
							else:
								print("user has privacy mode on")
						else:
							print("post was previously on db")
							voters = await reaction.users().flatten()
							post.update(add('points',10), where('msgid') == valuetwo)
							post.update(add('voters',[user.id]), where('msgid') == valuetwo)
							post.update(add('stars',1), where('msgid') == valuetwo)
							#send = await channel.send("Huzzah! **{}**'s post was so good it got starred more than once. They now have {} points. (+10)".format(reaction.message.author.name,result.get('points')))
						
						# Send a confirmation message

						channel = reaction.message.channel
						result = db.get(Query()['username'] == value)
						
						bestofname = best.search(Query().serverid == server)
						bestofname = bestofname[0]['channelid']
						bestofname = discord.utils.get(reaction.message.guild.channels, id=bestofname)

						notifmode = best.search(Query().serverid == server)
						notifmode = notifmode[0]['notification']
						checkM = self.client.get_emoji(660217963911184384)
						if notifmode == "reaction":
							react = await reaction.message.add_reaction(checkM)
						if (notifmode != "reaction") and (notifmode != "disabled"):
							send = await channel.send("Congrats, **{}**! Your post will be forever immortalized in the **#{}** channel. You now have {} points. (+10)".format(reaction.message.author.name,bestofname.name,result.get('points')))
						
						# Delete said message
						if notifmode == "reaction":
							await asyncio.sleep(1) 
							botid = self.client.user
							await reaction.message.remove_reaction(checkM, botid)
						if (notifmode != "reaction") and (notifmode != "disabled"):
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
							# Send a confirmation message or reaction
							notifmode = best.search(Query().serverid == server)
							notifmode = notifmode[0]['notification']
							checkM = self.client.get_emoji(660217963911184384)
							if notifmode == "reaction":
								react = await reaction.message.add_reaction(checkM)
							if (notifmode != "reaction") and (notifmode != "disabled"):
								result = db.get(Query()['username'] == value)
								heart = await channel.send("**Hearted!** {} now has {} points. (+1)".format(reaction.message.author.name,result.get('points')))
							if notifmode == "reaction":
								await asyncio.sleep(1) 
								botid = self.client.user
								await reaction.message.remove_reaction(checkM, botid)
							if (notifmode != "reaction") and (notifmode != "disabled"):
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
							
							# Log post for post leaderboard
							
							priv.clear_cache()
							exists = priv.count(Query().username == reaction.message.author.id)
							valuetwo = str(reaction.message.id)
							username = str(reaction.message.author.id)
							postexists = post.count(Query().msgid == valuetwo)
							if postexists == 0:
								if exists == 0:
									print("post wasnt previously on lb")
									if(len(reaction.message.attachments) > 0):
										post.insert({'msgid': valuetwo, 'username': username, 'points': 1, 'servers': server, 'content': reaction.message.content, 'embed': reaction.message.attachments[0].url, 'voters': [user.id], 'stars': 0, 'nsfw': is_nsfw})
									else:
										post.insert({'msgid': valuetwo, 'username': username, 'points': 1, 'servers': server, 'content': reaction.message.content, 'embed': '', 'voters': [user.id], 'stars': 0, 'nsfw': is_nsfw})
								else:
									print("user has privacy mode on")
							else:
								print("post was previously on db")
								post.update(add('points',1), where('msgid') == valuetwo)
								post.update(add('voters', [user.id]), where('msgid') == valuetwo)

							best.clear_cache()
							notifmode = best.search(Query().serverid == server)
							notifmode = notifmode[0]['notification']
							checkM = self.client.get_emoji(660217963911184384)
							if notifmode == "reaction":
								react = await reaction.message.add_reaction(checkM)
							if (notifmode != "reaction") and (notifmode != "disabled"):
								result = db.get(Query()['username'] == value)
								heart = await channel.send("**Hearted!** {} now has {} points. (+1)".format(reaction.message.author.name,result.get('points')))
							
							# Delete said message
							if notifmode == "reaction":
								await asyncio.sleep(1) 
								botid = self.client.user
								await reaction.message.remove_reaction(checkM, botid)
							if (notifmode != "reaction") and (notifmode != "disabled"):
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
							db.insert({'username': value, 'points': -1, 'servers': [server]})
							# Send a confirmation message
							notifmode = best.search(Query().serverid == server)
							notifmode = notifmode[0]['notification']
							checkM = self.client.get_emoji(660217963911184384)
							if notifmode == "reaction":
								react = await reaction.message.add_reaction(checkM)
							if (notifmode != "reaction") and (notifmode != "disabled"):
								result = db.get(Query()['username'] == value)
								crush = await channel.send("**Crushed.** {} now has {} points. (-1)".format(reaction.message.author.name,result.get('points')))
							if notifmode == "reaction":
								await asyncio.sleep(1) 
								botid = self.client.user
								await reaction.message.remove_reaction(checkM, botid)
							if (notifmode != "reaction") and (notifmode != "disabled"):
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
							
							# Log post for post leaderboard
							
							priv.clear_cache()
							exists = priv.count(Query().username == reaction.message.author.id)
							
							valuetwo = str(reaction.message.id)
							username = str(reaction.message.author.id)
							postexists = post.count(Query().msgid == valuetwo)
							if postexists == 0:
								if exists == 0:
									print("post wasnt previously on lb")
									if(len(reaction.message.attachments) > 0):
										post.insert({'msgid': valuetwo, 'username': username, 'points': -1, 'servers': server, 'content': reaction.message.content, 'embed': reaction.message.attachments[0].url, 'voters': [user.id], 'stars': 0, 'nsfw': is_nsfw})
									else:
										post.insert({'msgid': valuetwo, 'username': username, 'points': -1, 'servers': server, 'content': reaction.message.content, 'embed': '', 'voters': [user.id], 'stars': 0, 'nsfw': is_nsfw})
								else:
									print("user has privacy mode on")
							else:
								print("post was previously on db")
								post.update(subtract('points',1), where('msgid') == valuetwo)
								post.update(add('voters', [user.id]), where('msgid') == valuetwo)

							# Send a confirmation message
							best.clear_cache()
							notifmode = best.search(Query().serverid == server)
							notifmode = notifmode[0]['notification']
							checkM = self.client.get_emoji(660217963911184384)
							if notifmode == "reaction":
								react = await reaction.message.add_reaction(checkM)
							if (notifmode != "reaction") and (notifmode != "disabled"):
								result = db.get(Query()['username'] == value)
								crush = await channel.send("**Crushed.** {} now has {} points. (-1)".format(reaction.message.author.name,result.get('points')))
							
							# Delete said message
							if notifmode == "reaction":
								await asyncio.sleep(1) 
								botid = self.client.user
								await reaction.message.remove_reaction(checkM, botid)
							if (notifmode != "reaction") and (notifmode != "disabled"):
								await asyncio.sleep(3) 
								await crush.delete()		

				else:

					# -------------------------
					#  REACTION = :WASTEBASKET:
					#       (leaderboards)
					# -------------------------	
					if reaction.emoji == '🗑️':
						await deleteMessages(reaction)

					if reaction.emoji == '➡️':
						result = dm.get(Query()['id'] == reaction.message.id)
						page = result.get('page') + 1
						currentguild = str(reaction.message.guild.id)
						isGlobal = result.get('global')
						print(isGlobal)
						if (isGlobal == True):
							result = post.all()
						else:
							result = post.search(Query()['servers'] == currentguild)
						leaderboard = {} # Prepares an empty dictionary.
						j = 0
						for x in result: # For each entry in the database:
							leaderboard[j] = [int(x.get("points")), str(x.get("content")), str(x.get("username")), str(x.get("embed")), str(x.get("servers")), str(x.get("stars")), str(x.get("nsfw"))] # ...save the user's ID and its amount of points in a new Python database.
							j = j+1
						
						leaderboard = sorted(leaderboard.items(), key = lambda x : x[1][0], reverse=True)

						await printLeaderboard(page, leaderboard, self, reaction.message.guild, reaction.message, reaction.message.channel, False, isGlobal)

						await deleteMessages(reaction)

					if reaction.emoji == '⬅️':

						result = dm.get(Query()['id'] == reaction.message.id)
						page = result.get('page') - 1
						currentguild = str(reaction.message.guild.id)
						isGlobal = result.get('global')
						if (isGlobal == True):
							result = post.all()
						else:
							result = post.search(Query()['servers'] == currentguild)
						leaderboard = {} # Prepares an empty dictionary.
						j = 0
						for x in result: # For each entry in the database:
							leaderboard[j] = [int(x.get("points")), str(x.get("content")), str(x.get("username")), str(x.get("embed")), str(x.get("servers")), str(x.get("stars")), str(x.get("nsfw"))] # ...save the user's ID and its amount of points in a new Python database.
							j = j+1
						
						leaderboard = sorted(leaderboard.items(), key = lambda x : x[1][0], reverse=True)

						await printLeaderboard(page, leaderboard, self, reaction.message.guild, reaction.message, reaction.message.channel, False, isGlobal)

						await deleteMessages(reaction)



async def deleteMessages(reaction):
	channel = reaction.message.channel
	result = dm.get(Query()['id'] == reaction.message.id)
	messageIds = result.get('messages')
	for x in messageIds:
		msg = await channel.fetch_message(x)
		await msg.delete()

def setup(client):
	client.add_cog(Reaction(client))
