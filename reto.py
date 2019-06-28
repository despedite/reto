import discord
from discord.ext import commands
import asyncio
import pyfiglet
import mysql.connector
from mysql.connector import Error

prefix = "?"
bot = commands.Bot(command_prefix=prefix)
client = discord.Client()
ascii_banner = pyfiglet.figlet_format("Rēto.py")

try:
	connection = mysql.connector.connect(host='DATABASE_HOST_HERE',database='DATABASE_NAME_HERE',user='DATABASE_USER_HERE',password='DATABASE_PASS_HERE')
	if connection.is_connected():
		db_Info = connection.get_server_info()
		print("Connected to MySQL database!")
		cursor = connection.cursor()
		cursor.execute("select database();")
		record = cursor.fetchone()
except Error as e :
	print ("Error while connecting to MySQL", e)

# -------------------------
#	  ON READY COMMAND
# -------------------------

@bot.event
async def on_ready():
	print (ascii_banner)
	print ("Rēto is ONLINE!")
	print ("Running with the name " + str(bot.user) )
	print ("Invite link: https://discordapp.com/api/oauth2/authorize?client_id=591466921812164608&permissions=1342449744&scope=bot")
	print ("?setup to get started!")
	print ("--------------------------------------------")
	game = discord.Game("?setup to get started! | 1.0.1")
	await bot.change_presence(activity=game)

# -------------------------
#			SETUP
# -------------------------

@bot.command(pass_context=True)
async def setup(ctx):
	await ctx.send("Oh, hi there! Let's get the bot set up.")
	await ctx.send("Before starting, check that there is space to create three new emojis and that the bot has sufficient permissions. If the setup process doesn't finish properly, correct these issues and input ?setup again.")
	
	# Si el rol "Curator" no existe, el bot lo crea.
	try:
		rolesearch = discord.utils.get(ctx.guild.roles, name="Curator")
		if rolesearch == None:
			await ctx.guild.create_role(name="Curator")
			await ctx.send(":one: I've created the role **Curator**. Give this role to the people you want to allow posting on the Best Of channel.")
		else:
			await ctx.send(":one: The role **Curator** already exists, no further action has been taken.")
	except:
		await ctx.send(":x: An error has occurred while creating the role **Curator**. Check the bot's permissions and try again!")
	
	# Si el canal "best-of" no existe, el bot lo crea.
	try:
		channelsearch = discord.utils.get(ctx.guild.channels, name="best-of")
		if channelsearch == None:
			await ctx.guild.create_text_channel('best-of')
			await ctx.send(":two: The channel **best-of** has been created. Here's where messages that have had the reaction '10' will go.")
		else:
			await ctx.send(":two: The channel **best-of** already exists, no further action has been taken.")
	except:
		await ctx.send(":x: An error has occurred while creating the channel **#best-of**. Check the bot's permissions and try again!")

	# Si el usuario no tiene asignado el rol "Curator", el bot se lo asigna.
	try:
		if discord.utils.get(ctx.message.author.roles, name="Curator") is None:
			role = discord.utils.get(ctx.guild.roles, name="Curator")
			await ctx.message.author.add_roles(role)
			await ctx.send(":three: The role **Curator** has been assigned to you! This means that you can access the emoji :10: later on. For other people, assign it to them manually and after a restart (CTRL+R) they should be able to access said emoji.")
		else:
			await ctx.send(":three: The role **Curator** has already been assigned, no further action has been taken.")
	except:
		await ctx.send(":x: An error has occurred while assigning you the role **Curator**. Check the bot's permissions and try again!")

	# Si el emoji "10" no existe, el bot lo crea.
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
		#PLEASE REMOVE AFTER FIX AND THANKS
		#await ctx.send("If this is your first install and permissions are correct, this is a common issue. Just re-run ?setup while I fix the issue.")

	# Si el emoji "plus" no existe, el bot lo crea.
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
	
	# Si el emoji "minus" no existe, el bot lo crea.
	try:
		minussearch = discord.utils.get(ctx.guild.emojis, name="minus")
		if minussearch == None:
			with open("images/minus.png", "rb") as image:
				await ctx.guild.create_custom_emoji(name="minus", image=image.read())
				await ctx.send(":six: The emoji **:minus:** has been created. This emoji can be used by anyone to decrease the commenter's karma by one.")
		else:
			await ctx.send(":six: The emoji **:minus:** already exists, no further action has been taken.")
		
		await ctx.send("-----------------------")
		await ctx.send("You're all set! Now all you have to do is assign the **Curator** role on Server Settings to people you want to let contribute to #best_of. A Discord restart (CTRL+R) may be needed to see the emoji.")
		await ctx.send("Thank you very much for installing **Rēto**! If you have any issues, please contact **@Erik#0944**. :heart:")
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
		
		#Mostrar el mensaje en un canal especial

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
		#await self.bot.say(embed=embed)
		channel = discord.utils.get(reaction.message.guild.channels, name="best-of")

		#Añadir usuario a la tabla?
		cursor = connection.cursor(buffered=True)
		cursor.execute("SELECT * FROM score WHERE username='{}'".format(reaction.message.author))
		data="error" #initially just assign the value
		for i in cursor:
			data=i #if cursor has no data then loop will not run and value of data will be 'error'
		if data=="error":
			print("El usuario no existe en la base de datos. Añadiendolo...")
			insert_stmt = ("INSERT INTO score (username,points,id) VALUES ('{}', '{}', NULL)".format(reaction.message.author, 10))
			cursor.execute(insert_stmt)
			connection.commit()
			print ("Record inserted successfully into python_users table")
		else:
			print ("El usuario ya existe en la base de datos. Añadiendole 10 puntos...")
			update_stmt = ("UPDATE score SET points=points+10 WHERE username='{}'".format(reaction.message.author))
			cursor.execute(update_stmt)
			connection.commit()
			print ("Puntos actualizados!")
		
		# Si el canal "best-of" no existe, el bot lo crea y postea el mensaje ahi.
		
		if channel == None:
			await reaction.message.guild.create_text_channel('best-of')
			channel = reaction.message.channel
			await channel.send("The channel **best-of** doesn't exist, if the bot has permissions it has been created.")
			channel = discord.utils.get(reaction.message.guild.channels, name="best-of")
			await channel.send(embed=emberino)
		else:
			await channel.send(embed=emberino)
		
		#Manda el puto mensaje

		channel = reaction.message.channel
		valor = ("SELECT points FROM score WHERE username='{}'".format(reaction.message.author))
		cursor.execute(valor)
		valor2 = cursor.fetchone()
		
		
		send = await channel.send("Congrats, **{}**! Your post will be forever immortalized in the server's #best-of. You now have {} points. (+10)".format(reaction.message.author.name,valor2[0]))
		
		#Eliminar el mensaje
		await asyncio.sleep(3) 
		await send.delete()
	
	# -------------------------
	#	  REACTION = :PLUS:
	# -------------------------	
	
	if reaction.emoji.name == 'plus':
		channel = reaction.message.channel

		#Añadir usuario a la tabla?
		cursor = connection.cursor(buffered=True)
		cursor.execute("SELECT * FROM score WHERE username='{}'".format(reaction.message.author))
		data="error" #initially just assign the value
		for i in cursor:
			data=i #if cursor has no data then loop will not run and value of data will be 'error'
		if data=="error":
			print("El usuario no existe en la base de datos. Añadiendolo...")
			insert_stmt = ("INSERT INTO score (username,points,id) VALUES ('{}', '{}', NULL)".format(reaction.message.author, 1))
			cursor.execute(insert_stmt)
			connection.commit()
			print ("Record inserted successfully into python_users table")
			valor = ("SELECT points FROM score WHERE username='{}'".format(reaction.message.author))
			cursor.execute(valor)
			valor2 = cursor.fetchone()
			
			#Manda el puto mensaje
			
			heart = await channel.send("**Hearted!** {} now has {} points. (+1)".format(reaction.message.author.name,valor2[0]))
			await asyncio.sleep(3) 
			await heart.delete()
		else:
			print ("El usuario ya existe en la base de datos. Añadiendole 1 punto...")
			update_stmt = ("UPDATE score SET points=points+1 WHERE username='{}'".format(reaction.message.author))
			cursor.execute(update_stmt)
			connection.commit()
			print ("Puntos actualizados!")
			valor = ("SELECT points FROM score WHERE username='{}'".format(reaction.message.author))
			cursor.execute(valor)
			valor2 = cursor.fetchone()
			
			#Manda el puto mensaje
			
			heart = await channel.send("**Hearted!** {} now has {} points. (+1)".format(reaction.message.author.name,valor2[0]))
			await asyncio.sleep(3) 
			await heart.delete()
	# -------------------------
	#	  REACTION = :MINUS:
	# -------------------------	
	
	if reaction.emoji.name == 'minus':
		channel = reaction.message.channel

		#Añadir usuario a la tabla?
		cursor = connection.cursor(buffered=True)
		cursor.execute("SELECT * FROM score WHERE username='{}'".format(reaction.message.author))
		data="error" #initially just assign the value
		for i in cursor:
			data=i #if cursor has no data then loop will not run and value of data will be 'error'
		if data=="error":
			print("El usuario no existe en la base de datos. Añadiendolo...")
			insert_stmt = ("INSERT INTO score (username,points,id) VALUES ('{}', '{}', NULL)".format(reaction.message.author, 0))
			cursor.execute(insert_stmt)
			connection.commit()
			print ("Record inserted successfully into python_users table")
			valor = ("SELECT points FROM score WHERE username='{}'".format(reaction.message.author))
			cursor.execute(valor)
			valor2 = cursor.fetchone()
			
			#Manda el puto mensaje
			
			crush = await channel.send("**Crushed.** {} now has {} points. (-1)".format(reaction.message.author.name,valor2[0]))
			await asyncio.sleep(3) 
			await crush.delete()
		else:
			print ("El usuario ya existe en la base de datos. Restandolé 1 punto...")
			update_stmt = ("UPDATE score SET points=points-1 WHERE username='{}'".format(reaction.message.author))
			cursor.execute(update_stmt)
			connection.commit()
			print ("Puntos actualizados!")
			valor = ("SELECT points FROM score WHERE username='{}'".format(reaction.message.author))
			cursor.execute(valor)
			valor2 = cursor.fetchone()
			
			#Manda el puto mensaje
			
			crush = await channel.send("**Crushed.** {} now has {} points. (-1)".format(reaction.message.author.name,valor2[0]))
			await asyncio.sleep(3) 
			await crush.delete()

# -------------------------
#	      ?KARMA
# -------------------------

@bot.command(aliases=['points', 'point'])
async def karma(ctx, *args):
	if not args:
		valor = ("SELECT points FROM score WHERE username='{}'".format(ctx.message.author))
		cursor.execute(valor)
		valor2 = cursor.fetchone()
		
		send = await ctx.send("The user **{}** has a total of **{}** points.".format(ctx.message.author.name,valor2[0]))
	elif not ctx.message.mentions:
		await ctx.send("Invalid command! Do **?karma** to find out about your score, or @mention another user to find their score.")
	else:
		valor = ("SELECT points FROM score WHERE username='{}'".format(ctx.message.mentions[0]))
		cursor.execute(valor)
		valor2 = cursor.fetchone()
			
		send = await ctx.send("The user **{}** has a total of **{}** points.".format(ctx.message.mentions[0].name,valor2[0]))

# -------------------------
#	   MISC. COMMANDS
# -------------------------

@bot.command()
async def ping(ctx):
	latency = bot.latency
	await ctx.send(latency)

@bot.command()
async def invite(ctx):
	await ctx.send("Here's an invitation link for the bot: https://discordapp.com/api/oauth2/authorize?client_id=591466921812164608&permissions=1342449744&scope=bot")

bot.run('TOKEN_HERE')
