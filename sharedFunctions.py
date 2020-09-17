import discord
from discord.ext import commands
import asyncio
import pyfiglet
from tinydb import TinyDB, Query, where
from tinydb.operations import add, subtract
import aiohttp        
import aiofiles
import os.path
import os
import json
import random
import logging

db = TinyDB('json/db.json') #Database file: stores points of every user.
cfg = TinyDB("json/config.json") #Config file: stores configurations for the bot. Modify at your heart's content!
srv = TinyDB('json/server.json') #Server-specific configuration - allows you to modify stuff like the name of the reactions, for example.
post = TinyDB('json/comments.json') #Comment leaderboard.
priv = TinyDB('json/blacklist.json') #Privacy Mode blacklist. Users with PM on will not have their messages logged in the comment leaderboard.
dm = TinyDB('json/deletables.json') #Message deletion for Leaderboards.

table = db.table('_default', cache_size=None)

for c in cfg:
	bottoken = c['bottoken']
	botname = c['botname']
	support = c['support']
	botver = c['botver']
	prefix = c['prefix']
	botowner = c['botowner']

async def getProfile(author, ctx, self):
	valor = str(author)
	searchvalor = str(author.id)

	result = db.get(Query()['username'] == searchvalor)

	#
	# CONSEGUIR VALOR EN LA GLB
	#

	server = str(ctx.message.guild.id)
	db.clear_cache()
	lbsult = db.all() # doesnt work
	leaderboard = {} # Prepares an empty dictionary.
	for x in lbsult: # For each entry in the database:
		leaderboard[x.get("username")] = int(x.get("points")) # ...save the user's ID and its amount of points in a new Python database.
	leaderboard = sorted(leaderboard.items(), key = lambda x : x[1], reverse=True) # Sort this database by amount of points.
	s = ""
	leadervalue = 1

	for key, value in leaderboard: # For each value in the new, sorted DB:
		if key == searchvalor:
			break
		else:
			leadervalue += 1

	#
	# CONSEGUIR VALOR EN LA LLB
	#

	llbsult = db.search(Query().servers.all([server])) # doesnt work
	lleaderboard = {} # Prepares an empty dictionary.
	for x in llbsult: # For each entry in the database:
		lleaderboard[x.get("username")] = int(x.get("points")) # ...save the user's ID and its amount of points in a new Python database.
	lleaderboard = sorted(lleaderboard.items(), key = lambda x : x[1], reverse=True) # Sort this database by amount of points.
	s = ""
	localvalue = 1

	for key, value in lleaderboard: # For each value in the new, sorted DB:
		if key == searchvalor:
			break
		else:
			localvalue += 1

	#
	# GLB BADGE
	#

	if leadervalue == 1:
		leaderemblem = "🥇"
	elif leadervalue == 2:
		leaderemblem = "🥈"
	elif leadervalue == 3:
		leaderemblem = "🥉"
	elif leadervalue <= 10:
		leaderemblem = "🏅"
	else:
		leaderemblem = " "

	#
	# REVISAR ESTATUS DE CURATOR
	#

	curatoremblem = ""
	curatoremote = self.client.get_emoji(742136325628756000)
	role = discord.utils.get(ctx.guild.roles, name="Curator")
	if role in author.roles:
		curatoremblem = str(curatoremote)

	#
	# REVISAR ESTATUS DE BOTOWNER
	#

	botemblem = ""
	for x in botowner:
		if (int(author.id) == int(x)):
			botemblem = "👨‍💻"

	#
	# POINTS SENT
	#

	sentpoints = post.search(Query().voters.any([author.id]))

	#
	# STARS RECEIVED
	#

	starlist = post.search(Query().username == str(author.id))
	starsrec = 0
	for star in starlist:
		if 'stars' in star:
			starsrec += star['stars']

	#
	# SUPPORT BADGES (WIP)
	#

	#checkM = self.client.get_emoji(741669341409312889)
	#print(str(checkM))

	#
	# MANDAR VALOR DE EMBED
	#

	embed=discord.Embed(title=author.name + ' ' + leaderemblem + str(curatoremblem) + botemblem)
	embed.set_thumbnail(url=author.avatar_url)
	embed.add_field(name="Karma", value=result.get('points'), inline=True)
	embed.add_field(name="Global Rank", value=leadervalue, inline=True)
	embed.add_field(name="Local Rank", value=localvalue, inline=True)
	embed.add_field(name="Reacted posts", value=len(sentpoints), inline=True)
	embed.add_field(name="Stars received", value=starsrec, inline=True)
	await ctx.send(embed=embed)

#####

async def printLeaderboard(page, leaderboard, self, ctx, ctxMessage, ctxChannel, args, isGlobal):
	numero = ((page-1) * 5) + 1
	ceronumero = 1
	lbEmbed = [None] * 12
	embedIds = [None] * 12
	typeArgs = 'default'

	hardLimit = 6 #maximum amount of pages you can show on ?gplb. default is 6 (up to 25 messages)

	if len(leaderboard) == 0:
		await ctx.send("_Looks like this leaderboard is empty! Why don't we get started by reacting to posts?_")
		await ctxMessage.remove_reaction(checkM, botid)

	elif (isGlobal == True and not page > hardLimit) or isGlobal == False: 
		if ctxMessage:
			checkM = self.client.get_emoji(660250625107296256)
			react = await ctxMessage.add_reaction(checkM)
		
		for key,values in leaderboard[(numero-1):]:
			if numero != ((page * 5) + 1):
				if args:
					if args[0] == "nsfw":
						if (values[6] == "True"):
							typeArgs = 'nsfw'
							lbEmbed[ceronumero] = await createLeaderboardEmbed(self, values, numero, ceronumero, ctx, ctxMessage, ctxChannel, lbEmbed, page)
							if not lbEmbed[ceronumero] == False:
								embedIds[ceronumero] = lbEmbed[ceronumero].id
							numero = numero + 1
							ceronumero = ceronumero + 1
					elif args[0] == "sfw" and isGlobal == False:
						if (values[6] != "True" or values[6] == "None"):
							typeArgs = 'sfw'
							lbEmbed[ceronumero] = await createLeaderboardEmbed(self, values, numero, ceronumero, ctx, ctxMessage, ctxChannel, lbEmbed, page)
							if not lbEmbed[ceronumero] == False:
								embedIds[ceronumero] = lbEmbed[ceronumero].id
							numero = numero + 1
							ceronumero = ceronumero + 1

					elif args[0] == "all" and isGlobal == True:
						typeArgs = 'all'
						lbEmbed[ceronumero] = await createLeaderboardEmbed(self, values, numero, ceronumero, ctx, ctxMessage, ctxChannel, lbEmbed, page)
						if not lbEmbed[ceronumero] == False:
							embedIds[ceronumero] = lbEmbed[ceronumero].id
						numero = numero + 1
						ceronumero = ceronumero + 1
					else:
						print("Oh no.")
						typeArgs = 'mention'
						lbEmbed[ceronumero] = await createLeaderboardEmbed(self, values, numero, ceronumero, ctx, ctxMessage, ctxChannel, lbEmbed, page)
						if not lbEmbed[ceronumero] == False:
							embedIds[ceronumero] = lbEmbed[ceronumero].id
						numero = numero + 1
						ceronumero = ceronumero + 1
				else:
					if isGlobal == False:
						typeArgs = 'default'
						lbEmbed[ceronumero] = await createLeaderboardEmbed(self, values, numero, ceronumero, ctx, ctxMessage, ctxChannel, lbEmbed, page)
						if not lbEmbed[ceronumero] == False:
							embedIds[ceronumero] = lbEmbed[ceronumero].id
						numero = numero + 1
						ceronumero = ceronumero + 1
					elif values[6] != "True" or values[6] == "None":
						typeArgs = 'default'
						lbEmbed[ceronumero] = await createLeaderboardEmbed(self, values, numero, ceronumero, ctx, ctxMessage, ctxChannel, lbEmbed, page)
						if not lbEmbed[ceronumero] == False:
							embedIds[ceronumero] = lbEmbed[ceronumero].id
						numero = numero + 1
						ceronumero = ceronumero + 1

		cleanIds = list(filter(None, embedIds))
		if (lbEmbed[(int(ceronumero)-1)] == False): 
			lbEmbed[(int(ceronumero)-1)] = lbEmbed[(int(ceronumero)-2)]
		remove = await lbEmbed[(int(ceronumero)-1)].add_reaction("🗑️")
		if page > 1:
			nextitem = await lbEmbed[(int(ceronumero)-1)].add_reaction("⬅️")
		if (numero) == ((page * 5) + 1) and (page != hardLimit - 1 or isGlobal == False):
			if (len(leaderboard) >= numero):
				nextitem = await lbEmbed[(int(ceronumero)-1)].add_reaction("➡️")

		dm.insert({'id': lbEmbed[(int(ceronumero)-1)].id, 'messages': cleanIds, 'type': typeArgs, 'page': page, 'global': isGlobal})

		botid = self.client.user
		await ctxMessage.remove_reaction(checkM, botid)

async def createLeaderboardEmbed(self, values, numero, ceronumero, ctx, ctxMessage, ctxChannel, lbEmbed, page):

	emoji = discord.utils.get(ctxMessage.guild.emojis, name="plus")
	guild = ctxMessage.guild #Optimization!

	username = self.client.get_user(int(values[2]))
	guild = self.client.get_guild(int(values[4]))
	contenido=values[1]
	autor=username
	foto=username.avatar_url
	if(len(values[3]) > 0):
		imagen=values[3]

	if numero == 1:
		emberino=discord.Embed(description=contenido, colour=discord.Colour(0xffd700))
	elif numero == 2:
		emberino=discord.Embed(description=contenido, colour=discord.Colour(0xc0c0c0))
	elif numero == 3:
		emberino=discord.Embed(description=contenido, colour=discord.Colour(0xcd7f32))
	else:
		emberino=discord.Embed(description=contenido, colour=discord.Colour(0xa353a9))
	emberino.set_author(name=autor
	, icon_url=foto)
	emberino.set_footer(text=guild, icon_url=guild.icon_url)
	if numero == 1:
		emberino.add_field(name="Position", value="🥇 "+str(numero), inline=True)
	elif numero == 2:
		emberino.add_field(name="Position", value="🥈 "+str(numero), inline=True)
	elif numero == 3:
		emberino.add_field(name="Position", value="🥉 "+str(numero), inline=True)
	else:
		emberino.add_field(name="Position", value="✨ "+str(numero), inline=True)
	emberino.add_field(name="Karma", value=f"{emoji} " + str(values[0]), inline=True)
	if (values[5] != "None"): #if theres 'stars' value in post
		emberino.add_field(name="Stars", value=":star2: "+str(values[5]), inline=True)
	if(len(values[3]) > 0):
		emberino.set_image(url=values[3])

	if numero != ((page * 5) + 1):
		lbEmbed[ceronumero] = await ctxChannel.send(embed=emberino)
	else:
		lbEmbed[ceronumero] = False
	return lbEmbed[ceronumero]